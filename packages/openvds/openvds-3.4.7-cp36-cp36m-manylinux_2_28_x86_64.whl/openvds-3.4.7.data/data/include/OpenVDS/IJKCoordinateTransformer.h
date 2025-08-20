/****************************************************************************
** Copyright 2021 The Open Group
** Copyright 2021 Bluware, Inc.
**
** Licensed under the Apache License, Version 2.0 (the "License");
** you may not use this file except in compliance with the License.
** You may obtain a copy of the License at
**
**     http://www.apache.org/licenses/LICENSE-2.0
**
** Unless required by applicable law or agreed to in writing, software
** distributed under the License is distributed on an "AS IS" BASIS,
** WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
** See the License for the specific language governing permissions and
** limitations under the License.
****************************************************************************/

#ifndef OPENVDS_IJKCOORDINATETRANSFORMER_H
#define OPENVDS_IJKCOORDINATETRANSFORMER_H

#include "VolumeDataLayout.h"
#include "CoordinateTransformer.h"
#include "Matrix.h"
#include <math.h>

namespace OpenVDS
{

/// <summary>
/// IJKCoordinateTransformer may be used to transform between the following three-dimensional index and coordinate systems of a volume:
/// 
/// IJK Index - a 3D index into the volume based on IJK dimensions. 
/// Dimensions I and J are usually horizontal directions, whereas K is usually the vertical direction.
/// Transforms are provided to/from integer IJK indexes and also floating-point IJK positions.
///
/// World Coordinate - a world position, related to IJK through the IJK grid definition provided on construction.
///
/// Annotation Coordinate - a coordinate position based on the annotation axes of the volume (inline, crossline, depth, time, etc.).
/// The order of annotation coordinate values correspond to the volume axes for each IJK dimension.
/// That is, the annotation coordinate X value specifies the coordinate for the annotation axis corresponding to the I direction, and so on. 
/// When used with a VDS, annotation coordinates are based on the VDS axis descriptors.
/// 
/// Voxel Index - a 3D index into the volume based on volume data dimesions, where
/// dimension 0 is the data dimension that changes the fastest, 
/// dimension 1 is the data dimension that changes second fastest, etc.
/// Transforms are provided to/from integer voxel indexes and also floating-point voxel positions.
/// When used with a VDS, voxel index 0 refers to dimension 0, ranging from 0 to Dimension0Size - 1, and so on.
/// The relationship between IJK dimensions and voxel dimensions is controlled by the IJK dimension map provided at construction. 
/// If the dimension map is (0, 1, 2), the IJK dimensions are the same as voxel dimensions. 
/// However, it is often the case that the dimension map is not (0, 1, 2), and so IJK dimensions are not the same as voxel dimensions, especially when used with a VDS. 
/// When used with a VDS, the dimension map is often set to (2, 1, 0), meaning that IJK corresponds to voxel dimensions (2, 1, 0).
/// However, this is not a strict rule, and the dimension map will generally be defined based on the VDS axis descriptors. 
/// If a particular VDS axis is given the name "I", "J", or "K", that axis index will be considered as dimension I, J, or K. This is not very common.
/// If a particular VDS axis is given the name "Inline", it will be considered as dimension I.
/// If a particular VDS axis is given the name "Crossline", it will be considered as dimension J.
/// If a particular VDS axis is given the name "Time", "Depth", or "Sample", it will be considered as dimension K.
/// </summary>
struct IJKCoordinateTransformer
{
public:
                        IJKCoordinateTransformer() {}

                        IJKCoordinateTransformer(const IJKGridDefinition& ijkGridDefinition, const IntVector3& ijkSize)
                          : m_IJKGridDefinition(ijkGridDefinition), 
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(2, 1, 0)
                        {
                          InitTransformMatrixes();
                        }
                        
                        IJKCoordinateTransformer(const IJKGridDefinition& ijkGridDefinition, const IntVector3& ijkSize, const IntVector3& ijkToVoxelDimensionMap)
                          : m_IJKGridDefinition(ijkGridDefinition), 
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(ijkToVoxelDimensionMap)
                        {
                          InitTransformMatrixes();
                        }
                        
                        IJKCoordinateTransformer(const VDSIJKGridDefinition& vdsIJKGridDefinition, const IntVector3& ijkSize)
                          : m_IJKGridDefinition(vdsIJKGridDefinition),
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(vdsIJKGridDefinition.dimensionMap)
                        {
                          InitTransformMatrixes();
                        }

                        IJKCoordinateTransformer(const IJKGridDefinition& ijkGridDefinition, const IntVector3& ijkSize, const DoubleVector3& ijkAnnotationStart, const DoubleVector3& ijkAnnotationEnd)
                          : m_IJKGridDefinition(ijkGridDefinition), 
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(2, 1, 0),
                            m_IJKAnnotationStart(ijkAnnotationStart),
                            m_IJKAnnotationEnd(ijkAnnotationEnd)
                        {
                          InitTransformMatrixes();
                        }
                        
                        IJKCoordinateTransformer(const IJKGridDefinition& ijkGridDefinition, const IntVector3& ijkSize, const IntVector3& ijkToVoxelDimensionMap, const DoubleVector3& ijkAnnotationStart, const DoubleVector3& ijkAnnotationEnd)
                          : m_IJKGridDefinition(ijkGridDefinition), 
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(ijkToVoxelDimensionMap),
                            m_IJKAnnotationStart(ijkAnnotationStart),
                            m_IJKAnnotationEnd(ijkAnnotationEnd)
                        {
                          InitTransformMatrixes();
                        }
                        
                        IJKCoordinateTransformer(const VDSIJKGridDefinition& vdsIJKGridDefinition, const IntVector3& ijkSize, const DoubleVector3& ijkAnnotationStart, const DoubleVector3& ijkAnnotationEnd)
                          : m_IJKGridDefinition(vdsIJKGridDefinition),
                            m_IJKSize(ijkSize),
                            m_IJKToVoxelDimensionMap(vdsIJKGridDefinition.dimensionMap),
                            m_IJKAnnotationStart(ijkAnnotationStart),
                            m_IJKAnnotationEnd(ijkAnnotationEnd)
                        {
                          InitTransformMatrixes();
                        }

                        IJKCoordinateTransformer(const VolumeDataLayout* layout)
                        {
                          VDSIJKGridDefinition cVDSIJKGridDefinition = layout->GetVDSIJKGridDefinitionFromMetadata();
                          m_IJKGridDefinition = cVDSIJKGridDefinition;

                          m_IJKToVoxelDimensionMap = cVDSIJKGridDefinition.dimensionMap;
                          m_IJKSize = IntVector3(layout->GetDimensionNumSamples(m_IJKToVoxelDimensionMap[0]), layout->GetDimensionNumSamples(m_IJKToVoxelDimensionMap[1]), layout->GetDimensionNumSamples(m_IJKToVoxelDimensionMap[2]));
                          m_IJKAnnotationStart = DoubleVector3(layout->GetDimensionMin(m_IJKToVoxelDimensionMap[0]), layout->GetDimensionMin(m_IJKToVoxelDimensionMap[1]), layout->GetDimensionMin(m_IJKToVoxelDimensionMap[2]));
                          m_IJKAnnotationEnd = DoubleVector3(layout->GetDimensionMax(m_IJKToVoxelDimensionMap[0]), layout->GetDimensionMax(m_IJKToVoxelDimensionMap[1]), layout->GetDimensionMax(m_IJKToVoxelDimensionMap[2]));
                          InitTransformMatrixes();
                        }

  /// <summary>
  /// The IJK grid definition relating IJK coordinates to world XYZ coordinates
  /// </summary>
  const IJKGridDefinition&
  IJKGrid() const
  {
    return m_IJKGridDefinition;
  }

  /// <summary>
  /// The number of voxels in each IJK dimension
  /// </summary>
  const IntVector3&
  IJKSize() const
  {
    return m_IJKSize;
  }
  
  /// <summary>
  /// Mapping from IJK to voxel volume dimensions
  /// </summary>
  const IntVector3&
  IJKToVoxelDimensionMap() const
  {
    return m_IJKToVoxelDimensionMap;
  }

  /// <summary>
  /// The matrix used to transform from IJK coordinates to world coordinates
  /// </summary>
  const DoubleMatrix4x4&
  IJKToWorldTransform() const
  {
    return m_IJKToWorldTransform;
  }

  /// <summary>
  /// The matrix used to transform from world coordinates to IJK coordinates
  /// </summary>
  const DoubleMatrix4x4&
  WorldToIJKTransform() const
  {
    return m_WorldToIJKTransform;
  }

  /// <summary>
  /// The annotation start coordinates, corresponding to min IJK index (i.e. 0, 0, 0)
  /// </summary>
  const DoubleVector3&
  IJKAnnotationStart() const
  {
    return m_IJKAnnotationStart;
  }

  /// <summary>
  /// The annotation end coordinates, corresponding to max IJK index (i.e. IJKSize - (1, 1, 1))
  /// </summary>
  const DoubleVector3&
  IJKAnnotationEnd() const
  {
    return m_IJKAnnotationEnd;
  }

  /// <summary>
  /// Whether or not the annotation start/end coordinates are set, which defines the annotation coordinate system
  /// </summary>
  bool
  AnnotationsDefined() const
  {
    return m_IJKAnnotationStart != m_IJKAnnotationEnd;
  }
  
  /// <summary>
  /// Transform the given IJK position to a world position
  /// </summary>
  DoubleVector3
  IJKPositionToWorld(const DoubleVector3& ijkPosition) const
  {
    DoubleVector3
      worldPosition(ijkPosition);

    HomogeneousMultiply(worldPosition, worldPosition, m_IJKToWorldTransform);

    return worldPosition;
  }

  /// <summary>
  /// Transform the given IJK index to a world position
  /// </summary>
  DoubleVector3
  IJKIndexToWorld(const IntVector3& ijkIndex) const
  {
    DoubleVector3
      ijkPosition(ijkIndex.X, ijkIndex.Y, ijkIndex.Z);

    DoubleVector3
      worldPosition = IJKPositionToWorld(ijkPosition);

    return worldPosition;
  }
  
  /// <summary>
  /// Transform the given IJK position to an annotation position
  /// </summary>
  DoubleVector3
  IJKPositionToAnnotation(const DoubleVector3& ijkPosition) const
  {
    if (!AnnotationsDefined())
    {
      // Survey annotation coordinates are undefined
      return m_IJKAnnotationStart;
    }

    DoubleVector3
      annotationRange = m_IJKAnnotationEnd - m_IJKAnnotationStart;

    // We check for ijkPosition == 0 and don't divide by the size in order to avoid problems with 1 voxel thick volumes
    DoubleVector3
      annotationFactor(
        ijkPosition.X == 0 ? 0 : ijkPosition.X / (m_IJKSize.X - 1),
        ijkPosition.Y == 0 ? 0 : ijkPosition.Y / (m_IJKSize.Y - 1),
        ijkPosition.Z == 0 ? 0 : ijkPosition.Z / (m_IJKSize.Z - 1));

    DoubleVector3
      annotationOffset(annotationFactor);

    annotationOffset = Multiply(annotationOffset, annotationRange);

    DoubleVector3
      annotationPosition = m_IJKAnnotationStart + annotationOffset;

    return annotationPosition;
  }

  /// <summary>
  /// Transform the given IJK index to an annotation position
  /// </summary>
  DoubleVector3
  IJKIndexToAnnotation(const IntVector3& ijkIndex) const
  {
    DoubleVector3
      ijkPosition(ijkIndex.X, ijkIndex.Y, ijkIndex.Z);

    DoubleVector3
      annotationPosition = IJKPositionToAnnotation(ijkPosition);

    return annotationPosition;
  }

  /// <summary>
  /// Transform the given IJK position to a voxel position
  /// </summary>
  DoubleVector3
  IJKPositionToVoxelPosition(const DoubleVector3& ijkPosition) const
  {
    DoubleVector3
      voxelPosition;
    voxelPosition[m_IJKToVoxelDimensionMap.X] = ijkPosition.X;
    voxelPosition[m_IJKToVoxelDimensionMap.Y] = ijkPosition.Y;
    voxelPosition[m_IJKToVoxelDimensionMap.Z] = ijkPosition.Z;
    return voxelPosition;
  }

  /// <summary>
  /// Transform the given IJK index to a voxel index
  /// </summary>
  IntVector3
  IJKIndexToVoxelIndex(const IntVector3& ijkIndex) const
  {
    IntVector3
      voxelIndex;
    voxelIndex[m_IJKToVoxelDimensionMap.X] = ijkIndex.X;
    voxelIndex[m_IJKToVoxelDimensionMap.Y] = ijkIndex.Y;
    voxelIndex[m_IJKToVoxelDimensionMap.Z] = ijkIndex.Z;
    return voxelIndex;
  }

  /// <summary>
  /// Transform the given world position to a IJK position
  /// </summary>
  DoubleVector3
  WorldToIJKPosition(const DoubleVector3& worldPosition) const
  {
    DoubleVector3
      ijkPosition(worldPosition);

    HomogeneousMultiply(ijkPosition, ijkPosition, m_WorldToIJKTransform);

    return ijkPosition;
  }

  /// <summary>
  /// Transform the given world position to a IJK index
  /// </summary>
  IntVector3
  WorldToIJKIndex(const DoubleVector3& worldPosition) const
  {
    DoubleVector3
      ijkPosition = WorldToIJKPosition(worldPosition);

    IntVector3
      ijkIndex = ConvertIJKPositionToIndex(ijkPosition);

    return ijkIndex;
  }
  
  /// <summary>
  /// Transform the given world position to an annotation position
  /// </summary>
  DoubleVector3
  WorldToAnnotation(DoubleVector3 worldPosition) const
  {
    DoubleVector3
      ijkPosition = WorldToIJKPosition(worldPosition);

    DoubleVector3
      annotationPosition = IJKPositionToAnnotation(ijkPosition);

    return annotationPosition;
  }
  
  /// <summary>
  /// Transform the given world position to a voxel position
  /// </summary>
  DoubleVector3
  WorldToVoxelPosition(const DoubleVector3& worldPosition) const
  {
    DoubleVector3
      ijkPosition = WorldToIJKPosition(worldPosition);

    DoubleVector3
      voxelPosition = IJKPositionToVoxelPosition(ijkPosition);

    return voxelPosition;
  }
  
  /// <summary>
  /// Transform the given world position to a voxel index
  /// </summary>
  IntVector3
  WorldToVoxelIndex(const DoubleVector3& worldPosition) const
  {
    IntVector3
      ijkIndex = WorldToIJKIndex(worldPosition);

    IntVector3
      voxelIndex = IJKIndexToVoxelIndex(ijkIndex);

    return voxelIndex;
  }
  
  /// <summary>
  /// Transform the given annotation position to a IJK position
  /// </summary>
  DoubleVector3
  AnnotationToIJKPosition(const DoubleVector3& annotationPosition) const
  {
    if (!AnnotationsDefined())
    {
      // Survey annotation coordinates are undefined; return min IJK position
      return DoubleVector3(0, 0, 0);
    }

    // We check for offset == 0 and don't divide by the range in order to avoid problems with 1 voxel thick volumes
    DoubleVector3
      annotationRange = m_IJKAnnotationEnd - m_IJKAnnotationStart;
    DoubleVector3
      annotationOffset = annotationPosition - m_IJKAnnotationStart;
    DoubleVector3
      annotationFactor(
        annotationOffset.X == 0 ? 0 : annotationOffset.X / annotationRange.X,
        annotationOffset.Y == 0 ? 0 : annotationOffset.Y / annotationRange.Y,
        annotationOffset.Z == 0 ? 0 : annotationOffset.Z / annotationRange.Z);

    DoubleVector3
      ijkPosition(m_IJKSize.X - 1, m_IJKSize.Y - 1, m_IJKSize.Z - 1);

    ijkPosition = Multiply(ijkPosition, annotationFactor);

    return ijkPosition;
  }

  /// <summary>
  /// Transform the given annotation position to a IJK index
  /// </summary>
  IntVector3
  AnnotationToIJKIndex(const DoubleVector3& annotationPosition) const
  {
    DoubleVector3
      ijkPosition = AnnotationToIJKPosition(annotationPosition);

    IntVector3
      ijkIndex = ConvertIJKPositionToIndex(ijkPosition);

    return ijkIndex;
  }
  
  /// <summary>
  /// Transform the given annotation position to a world position
  /// </summary>
  DoubleVector3
  AnnotationToWorld(DoubleVector3 annotationPosition) const
  {
    DoubleVector3
      ijkPosition = AnnotationToIJKPosition(annotationPosition);

    DoubleVector3
      worldPosition = IJKPositionToWorld(ijkPosition);

    return worldPosition;
  }
  
  /// <summary>
  /// Transform the given annotation position to a voxel position
  /// </summary>
  DoubleVector3
  AnnotationToVoxelPosition(const DoubleVector3& annotationPosition) const
  {
    DoubleVector3
      ijkPosition = AnnotationToIJKPosition(annotationPosition);

    DoubleVector3
      voxelPosition = IJKPositionToVoxelPosition(ijkPosition);

    return voxelPosition;
  }

  /// <summary>
  /// Transform the given annotation position to a voxel index
  /// </summary>
  IntVector3
  AnnotationToVoxelIndex(const DoubleVector3& annotationPosition) const
  {
    IntVector3
      ijkIndex = AnnotationToIJKIndex(annotationPosition);

    IntVector3
      voxelIndex = IJKIndexToVoxelIndex(ijkIndex);

    return voxelIndex;
  }
  
  /// <summary>
  /// Transform the given voxel position to an IJK position
  /// </summary>
  DoubleVector3
  VoxelPositionToIJKPosition(const DoubleVector3& voxelPosition) const
  {
    DoubleVector3
      ijkPosition(
        voxelPosition[m_IJKToVoxelDimensionMap.X],
        voxelPosition[m_IJKToVoxelDimensionMap.Y],
        voxelPosition[m_IJKToVoxelDimensionMap.Z]);

    return ijkPosition;
  }
  
  /// <summary>
  /// Transform the given voxel index to an IJK index
  /// </summary>
  IntVector3
  VoxelIndexToIJKIndex(const IntVector3& voxelIndex) const
  {
    IntVector3
      ijkIndex(
        voxelIndex[m_IJKToVoxelDimensionMap.X],
        voxelIndex[m_IJKToVoxelDimensionMap.Y],
        voxelIndex[m_IJKToVoxelDimensionMap.Z]);

    return ijkIndex;
  }
  
  /// <summary>
  /// Transform the given voxel position to a world position
  /// </summary>
  DoubleVector3
  VoxelPositionToWorld(const DoubleVector3& voxelPosition) const
  {
    DoubleVector3
      ijkPosition = VoxelPositionToIJKPosition(voxelPosition);

    DoubleVector3
      worldPosition = IJKPositionToWorld(ijkPosition);

    return worldPosition;
  }

  /// <summary>
  /// Transform the given voxel index to a world position
  /// </summary>
  DoubleVector3
  VoxelIndexToWorld(const IntVector3& voxelIndex) const
  {
    IntVector3
      ijkIndex = VoxelIndexToIJKIndex(voxelIndex);

    DoubleVector3
      worldPosition = IJKIndexToWorld(ijkIndex);

    return worldPosition;
  }
  
  /// <summary>
  /// Transform the given voxel position to an annotation position
  /// </summary>
  DoubleVector3
  VoxelPositionToAnnotation(const DoubleVector3& voxelPosition) const
  {
    DoubleVector3
      ijkPosition = VoxelPositionToIJKPosition(voxelPosition);

    DoubleVector3
      annotationPosition = IJKPositionToAnnotation(ijkPosition);

    return annotationPosition;
  }

  /// <summary>
  /// Transform the given voxel index to an annotation position
  /// </summary>
  DoubleVector3
  VoxelIndexToAnnotation(const IntVector3& voxelIndex) const
  {
    IntVector3
      ijkIndex = VoxelIndexToIJKIndex(voxelIndex);

    DoubleVector3
      annotationPosition = IJKIndexToAnnotation(ijkIndex);

    return annotationPosition;
  }
  
  /// <summary>
  /// Determine whether the given IJK position is out of range
  /// </summary>
  bool
  IsIJKPositionOutOfRange(const DoubleVector3& ijkPosition) const
  {
    return ErrorCodeIfIJKPositionOutOfRange(ijkPosition) != 0;
  }

  /// <summary>
  /// Determine whether the given IJK index is out of range 
  /// </summary>
  bool
  IsIJKIndexOutOfRange(const IntVector3& ijkIndex) const
  {
    return
      ijkIndex.X < 0 ||
      ijkIndex.Y < 0 ||
      ijkIndex.Z < 0 ||
      ijkIndex.X >= m_IJKSize.X ||
      ijkIndex.Y >= m_IJKSize.Y ||
      ijkIndex.Z >= m_IJKSize.Z;
  }

  /// <summary>
  /// Determine whether the given voxel position is out of range
  /// </summary>
  bool
  IsVoxelPositionOutOfRange(const DoubleVector3& voxelPosition) const
  {
    return ErrorCodeIfVoxelPositionOutOfRange(voxelPosition) != 0;
  }
  
  /// <summary>
  /// Determine whether the given voxel index is out of range 
  /// </summary>
  bool
  IsVoxelIndexOutOfRange(const IntVector3& voxelIndex) const
  {
    return
      voxelIndex.X < 0 ||
      voxelIndex.Y < 0 ||
      voxelIndex.Z < 0 ||
      voxelIndex[m_IJKToVoxelDimensionMap.X] >= m_IJKSize.X ||
      voxelIndex[m_IJKToVoxelDimensionMap.Y] >= m_IJKSize.Y ||
      voxelIndex[m_IJKToVoxelDimensionMap.Z] >= m_IJKSize.Z;
  }
  
  /// <summary>
  /// Convert the given IJK position to IJK index.
  /// Return (-1, -1, -1) if any component is outside valid range.
  /// </summary>
  IntVector3
  ConvertIJKPositionToIndex(const DoubleVector3& ijkPosition) const
  {
    // Return (-1, -1, -1) if any component is outside valid IJK range (volume for one voxel spans negative/positive 0.5)
    
    if (ijkPosition.X < -0.5 ||
        ijkPosition.Y < -0.5 ||
        ijkPosition.Z < -0.5 ||
        ijkPosition.X > (m_IJKSize.X - 0.5) ||
        ijkPosition.Y > (m_IJKSize.Y - 0.5) ||
        ijkPosition.Z > (m_IJKSize.Z - 0.5))
    {
      return IntVector3(-1, -1, -1);
    }

    // Inside valid IJK range we round to nearest integer
    return IntVector3(
      (int)floor(ijkPosition.X + 0.5),
      (int)floor(ijkPosition.Y + 0.5),
      (int)floor(ijkPosition.Z + 0.5));
  }

  /// <summary>
  /// Convert the given voxel position to voxel index.
  /// Return (-1, -1, -1) if any component is outside valid range.
  /// </summary>
  IntVector3
  ConvertVoxelPositionToIndex(const DoubleVector3& voxelPosition) const
  {
    // Return (-1, -1, -1) if any component is outside valid voxel range (volume for one voxel spans negative/positive 0.5)

    if (voxelPosition.X < -0.5 ||
        voxelPosition.Y < -0.5 ||
        voxelPosition.Z < -0.5 ||
        voxelPosition[m_IJKToVoxelDimensionMap.X] > (m_IJKSize.X - 0.5) ||
        voxelPosition[m_IJKToVoxelDimensionMap.Y] > (m_IJKSize.Y - 0.5) ||
        voxelPosition[m_IJKToVoxelDimensionMap.Z] > (m_IJKSize.Z - 0.5))
    {
      return IntVector3(-1, -1, -1);
    }

    // Inside valid voxel range we round to nearest integer
    return IntVector3(
      (int)floor(voxelPosition.X + 0.5),
      (int)floor(voxelPosition.Y + 0.5),
      (int)floor(voxelPosition.Z + 0.5));
  }
  
  /// <summary>
  /// Equality operator
  /// </summary>
  inline bool
  operator== (const IJKCoordinateTransformer& rhs) const
  {
    return m_IJKGridDefinition == rhs.m_IJKGridDefinition &&
           m_IJKSize == rhs.m_IJKSize &&
           m_IJKToVoxelDimensionMap == rhs.m_IJKToVoxelDimensionMap &&
           m_IJKAnnotationStart == rhs.m_IJKAnnotationStart &&
           m_IJKAnnotationEnd == rhs.m_IJKAnnotationEnd;
  }
  
  int
  ErrorCodeIfIJKPositionOutOfRange(const DoubleVector3& ijkPosition) const
  {
    const double 
      EPSILON = 0;

    if (ijkPosition.X < -EPSILON || ijkPosition.X > (m_IJKSize.X - 1) + EPSILON)
    {
      // I
      return 1;
    }

    if (ijkPosition.Y < -EPSILON || ijkPosition.Y > (m_IJKSize.Y - 1) + EPSILON)
    {
      // J
      return 2;
    }

    if (ijkPosition.Z < -EPSILON || ijkPosition.Z > (m_IJKSize.Z - 1) + EPSILON)
    {
      // K
      return 3;
    }

    return 0;
  }
  
  int
  ErrorCodeIfVoxelPositionOutOfRange(const DoubleVector3& voxelPosition) const
  {
    const double 
      EPSILON = 0;

    if (voxelPosition.X < -EPSILON)
    {
      // 0
      return 1;
    }
    
    if (voxelPosition.Y < -EPSILON)
    {
      // 1
      return 2;
    }

    if (voxelPosition.Z < -EPSILON)
    {
      // 2
      return 3;
    }

    if (voxelPosition[m_IJKToVoxelDimensionMap.X] > (m_IJKSize.X - 1) + EPSILON)
    {
      return m_IJKToVoxelDimensionMap.X + 1;
    }
    
    if (voxelPosition[m_IJKToVoxelDimensionMap.Y] > (m_IJKSize.Y - 1) + EPSILON)
    {
      return m_IJKToVoxelDimensionMap.Y + 1;
    }
    
    if (voxelPosition[m_IJKToVoxelDimensionMap.Z] > (m_IJKSize.Z - 1) + EPSILON)
    {
      return m_IJKToVoxelDimensionMap.Z + 1;
    }
    
    return 0;
  }
  
protected:

  template<typename T, size_t SIZE>
  void setUnitMatrix(Matrix<T, SIZE> &a)
  {
    for (int i = 0; i < int(SIZE); i++)
    {
      a.data[i] = Vector<T, SIZE>();
      a.data[i][i] = T(1);
    }
  }

  DoubleVector3 getPositionMatrix(DoubleMatrix4x4 &a) const
  {
    return DoubleVector3(a.data[3].X, a.data[3].Y, a.data[3].Z);
  }
  
  DoubleVector3 getScaleMatrix(DoubleMatrix4x4 &a) const
  {
    DoubleVector3
      c1(a.data[0].X, a.data[0].Y, a.data[0].Z),
      c2(a.data[1].X, a.data[1].Y, a.data[1].Z),
      c3(a.data[2].X, a.data[2].Y, a.data[2].Z);

    double
      l1 = Length(c1),
      l2 = Length(c2),
      l3 = Length(c3);

    return DoubleVector3(l1,l2,l3);
  }

  void setPositionOrientationScaleMatrix(DoubleMatrix4x4 & a, DoubleVector3 position, DoubleMatrix3x3 orientation, DoubleVector3 scale)
  {
    // Scale matrix (i.e. diagonal matrix scaleX, scaleY, scaleZ), pre-multiplied
    // by orientation gives product matrix:
    a.data[0].X = scale.X * orientation.data[0].X;
    a.data[1].X = scale.Y * orientation.data[1].X;
    a.data[2].X = scale.Z * orientation.data[2].X;

    a.data[0].Y = scale.X * orientation.data[0].Y;
    a.data[1].Y = scale.Y * orientation.data[1].Y;
    a.data[2].Y = scale.Z * orientation.data[2].Y;

    a.data[0].Z = scale.X * orientation.data[0].Z;
    a.data[1].Z = scale.Y * orientation.data[1].Z;
    a.data[2].Z = scale.Z * orientation.data[2].Z;

    // Set translation:
    a.data[3].X = position.X;
    a.data[3].Y = position.Y;
    a.data[3].Z = position.Z;

    // Fill in unused/default values (4th coordinate kept as w = 1)
    a.data[0].T = 0;
    a.data[1].T = 0;
    a.data[2].T = 0;
    a.data[3].T = 1;
  }

  void setOrientationMatrix(DoubleMatrix4x4 &a, DoubleMatrix3x3 &orientation)
  {

    DoubleVector3
      position = getPositionMatrix(a),
      scale = getScaleMatrix(a);
    setPositionOrientationScaleMatrix(a, position, orientation, scale);
  }

  bool InverseMatrix(DoubleMatrix4x4 &result, const DoubleMatrix4x4 & matrix)
  {
    double a0 = matrix.data[0].X * matrix.data[1].Y - matrix.data[1].X * matrix.data[0].Y;
    double a1 = matrix.data[0].X * matrix.data[2].Y - matrix.data[2].X * matrix.data[0].Y;
    double a2 = matrix.data[0].X * matrix.data[3].Y - matrix.data[3].X * matrix.data[0].Y; 
    double a3 = matrix.data[1].X * matrix.data[2].Y - matrix.data[2].X * matrix.data[1].Y;    
    double a4 = matrix.data[1].X * matrix.data[3].Y - matrix.data[3].X * matrix.data[1].Y;            
    double a5 = matrix.data[2].X * matrix.data[3].Y - matrix.data[3].X * matrix.data[2].Y;

    double b0 = matrix.data[0].Z * matrix.data[1].T - matrix.data[1].Z * matrix.data[0].T;
    double b1 = matrix.data[0].Z * matrix.data[2].T - matrix.data[2].Z * matrix.data[0].T; 
    double b2 = matrix.data[0].Z * matrix.data[3].T - matrix.data[3].Z * matrix.data[0].T; 
    double b3 = matrix.data[1].Z * matrix.data[2].T - matrix.data[2].Z * matrix.data[1].T;  
    double b4 = matrix.data[1].Z * matrix.data[3].T - matrix.data[3].Z * matrix.data[1].T;
    double b5 = matrix.data[2].Z * matrix.data[3].T - matrix.data[3].Z * matrix.data[2].T;

    double det = (a0 * b5) - (a1 * b4) + (a2 * b3) + (a3 * b2) - (a4 * b1) + (a5 * b0);

    if (fabs(det) <= 1e-60)
    {
      result = DoubleMatrix4x4();
      return false;
    }

    // Make a copy because result and matrix could be the same object
    DoubleMatrix4x4 
      temp(matrix);

    Assign(result.data[0], +temp.data[1].Y * b5 - temp.data[2].Y * b4 + temp.data[3].Y * b3,
                           -temp.data[0].Y * b5 + temp.data[2].Y * b2 - temp.data[3].Y * b1,
                           +temp.data[0].Y * b4 - temp.data[1].Y * b2 + temp.data[3].Y * b0,
                           -temp.data[0].Y * b3 + temp.data[1].Y * b1 - temp.data[2].Y * b0);

    Assign(result.data[1], -temp.data[1].X * b5 + temp.data[2].X * b4 - temp.data[3].X * b3,
                           +temp.data[0].X * b5 - temp.data[2].X * b2 + temp.data[3].X * b1,
                           -temp.data[0].X * b4 + temp.data[1].X * b2 - temp.data[3].X * b0,
                           +temp.data[0].X * b3 - temp.data[1].X * b1 + temp.data[2].X * b0);

    Assign(result.data[2], +temp.data[1].T * a5 - temp.data[2].T * a4 + temp.data[3].T * a3,
                           -temp.data[0].T * a5 + temp.data[2].T * a2 - temp.data[3].T * a1,
                           +temp.data[0].T * a4 - temp.data[1].T * a2 + temp.data[3].T * a0,
                           -temp.data[0].T * a3 + temp.data[1].T * a1 - temp.data[2].T * a0);

    Assign(result.data[3], -temp.data[1].Z * a5 + temp.data[2].Z * a4 - temp.data[3].Z * a3,
                           +temp.data[0].Z * a5 - temp.data[2].Z * a2 + temp.data[3].Z * a1,
                           -temp.data[0].Z * a4 + temp.data[1].Z * a2 - temp.data[3].Z * a0,
                           +temp.data[0].Z * a3 - temp.data[1].Z * a1 + temp.data[2].Z * a0);
    
    double invDet = 1.0 / det;
    
    Scale(result.data[0], invDet);
    Scale(result.data[1], invDet);
    Scale(result.data[2], invDet);
    Scale(result.data[3], invDet);

    return true;
  }

  static void HomogeneousMultiply(DoubleVector3& result, const DoubleVector3 vectorA, const DoubleMatrix4x4& matrixA)
  {
    result.X = vectorA.X * matrixA.data[0].X +
      vectorA.Y * matrixA.data[1].X +
      vectorA.Z * matrixA.data[2].X +
      matrixA.data[3].X;

    result.Y = vectorA.X * matrixA.data[0].Y +
      vectorA.Y * matrixA.data[1].Y +
      vectorA.Z * matrixA.data[2].Y +
      matrixA.data[3].Y;

    result.Z = vectorA.X * matrixA.data[0].Z +
      vectorA.Y * matrixA.data[1].Z +
      vectorA.Z * matrixA.data[2].Z +
      matrixA.data[3].Z;
  }

  void                  
  InitTransformMatrixes()
  {
    setUnitMatrix(m_IJKToWorldTransform);

    m_IJKToWorldTransform.data[3][0] = m_IJKGridDefinition.origin.X;
    m_IJKToWorldTransform.data[3][1] = m_IJKGridDefinition.origin.Y;
    m_IJKToWorldTransform.data[3][2] = m_IJKGridDefinition.origin.Z;

    
    DoubleMatrix3x3 orientation;
    orientation.data[0] = m_IJKGridDefinition.iUnitStep;
    orientation.data[1] = m_IJKGridDefinition.jUnitStep;
    orientation.data[2] = m_IJKGridDefinition.kUnitStep;
    setOrientationMatrix(m_IJKToWorldTransform, orientation);

    m_WorldToIJKTransform = m_IJKToWorldTransform;
    InverseMatrix(m_WorldToIJKTransform, m_WorldToIJKTransform);
  }
    
  IJKGridDefinition     m_IJKGridDefinition;
  IntVector3            m_IJKSize;
  IntVector3            m_IJKToVoxelDimensionMap;

  DoubleVector3         m_IJKAnnotationStart;
  DoubleVector3         m_IJKAnnotationEnd;

  DoubleMatrix4x4       m_IJKToWorldTransform;
  DoubleMatrix4x4       m_WorldToIJKTransform;
};

} // end namespace OpenVDS

#endif // OPENVDS_IJKCOORDINATETRANSFORMER_H
