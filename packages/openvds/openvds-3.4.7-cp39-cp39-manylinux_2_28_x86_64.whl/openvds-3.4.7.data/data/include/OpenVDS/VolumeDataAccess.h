/****************************************************************************
** Copyright 2019 The Open Group
** Copyright 2019 Bluware, Inc.
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

#ifndef OPENVDS_VOLUMEDATAACCESS_H
#define OPENVDS_VOLUMEDATAACCESS_H

#include <OpenVDS/VolumeData.h>
#include <OpenVDS/VolumeDataLayout.h>
#include <OpenVDS/VolumeDataChannelDescriptor.h>
#include <OpenVDS/Vector.h>
#include <OpenVDS/Exceptions.h>

namespace OpenVDS {

enum class VDSProduceStatus
{
  Normal,
  Remapped,
  Unavailable
};

class VolumeDataPageAccessor;
class VolumeDataLayout;
struct VDS;

template <typename INDEX, typename T> class IVolumeDataReadAccessor;
template <typename INDEX, typename T> class IVolumeDataReadWriteAccessor;

template <typename T>
struct IndexRegion
{
    T Min;
    T Max;

    IndexRegion() {}
    IndexRegion(T Min, T Max) : Min(Min), Max(Max) {}
};

class IVolumeDataAccessor
{
protected:
                IVolumeDataAccessor() {}
  virtual      ~IVolumeDataAccessor() {}
public:
  class Manager
  {
  protected:
                  Manager() {}
    virtual      ~Manager() {}
  public:
    virtual void  DestroyVolumeDataAccessor(IVolumeDataAccessor *accessor) = 0;

    virtual IVolumeDataAccessor *
                  CloneVolumeDataAccessor(IVolumeDataAccessor const &accessor) = 0;
  };

  virtual Manager &
                GetManager() = 0;

  virtual VolumeDataLayout const *
                GetLayout() = 0;
};

template <typename INDEX>
class IVolumeDataRegions
{
protected:
  virtual      ~IVolumeDataRegions() {}

public:
  virtual int64_t
                RegionCount() = 0;

  virtual IndexRegion<INDEX>
                Region(int64_t region) = 0;

  virtual int64_t
                RegionFromIndex(INDEX index) = 0;
};

template <typename INDEX>
class IVolumeDataAccessorWithRegions : public IVolumeDataAccessor, public IVolumeDataRegions<INDEX>
{
public:
  virtual IndexRegion<INDEX>
                CurrentRegion() = 0;
};

template <typename INDEX, typename T>
class IVolumeDataReadAccessor : public IVolumeDataAccessorWithRegions<INDEX>
{
public:
  virtual T     GetValue(INDEX index) = 0;
};

template <typename INDEX, typename T>
class IVolumeDataReadWriteAccessor : public IVolumeDataReadAccessor<INDEX, T>
{
public:
  virtual void SetValue(INDEX index, T value) = 0;
  virtual void Commit() = 0;
  virtual void Cancel() = 0;
};

class VolumeDataPage
{
protected:
                VolumeDataPage() {}
  virtual      ~VolumeDataPage() {}
public:
  virtual VolumeDataPageAccessor &
                GetVolumeDataPageAccessor() const = 0;
  virtual void  GetMinMax(int (&min)[Dimensionality_Max], int (&max)[Dimensionality_Max]) const = 0;
  virtual void  GetMinMaxExcludingMargin(int (&minExcludingMargin)[Dimensionality_Max], int (&maxExcludingMargin)[Dimensionality_Max]) const = 0;
  virtual ReadErrorException
                GetError() const = 0;
  virtual const void *
                GetBuffer(int(&size)[Dimensionality_Max], int (&pitch)[Dimensionality_Max]) = 0;
  const void   *GetBuffer(int (&pitch)[Dimensionality_Max]) { int size[Dimensionality_Max]; return GetBuffer(size, pitch); }
  virtual void *GetWritableBuffer(int(&size)[Dimensionality_Max], int (&pitch)[Dimensionality_Max]) = 0;
  void         *GetWritableBuffer(int (&pitch)[Dimensionality_Max]) { int size[Dimensionality_Max]; return GetWritableBuffer(size, pitch); }
  virtual void  UpdateWrittenRegion(const int (&writtenMin)[Dimensionality_Max], const int (&writtenMax)[Dimensionality_Max]) = 0;
  virtual void  Release() = 0;
};

class VolumeDataPageAccessor
{
public:
  enum AccessMode
  {
    AccessMode_ReadOnly,                     ///< The volume data page accessor will only be used for reading
    AccessMode_ReadWrite,                    ///< The volume data page accessor will be used for reading and writing (can only be used with LOD 0, the other LODs will be automatically updated)
    AccessMode_Create,                       ///< The volume data page accessor will be used to write new data, overwriting any existing data (can only be used with LOD 0, the other LODs will be automatically created)
    AccessMode_CreateWithoutLODGeneration,   ///< The volume data page accessor will be used to write new data, overwriting any existing data (each LOD has to be created separately)
    AccessMode_ReadWriteWithoutLODGeneration ///< The volume data page accessor will be used used for reading and writing (each LOD has to be created separately)
  };

protected:
                VolumeDataPageAccessor() {}
  virtual      ~VolumeDataPageAccessor() {}

  virtual int     GetChunkCountInSuperChunk(int64_t superChunkIndex) const = 0;
  virtual void    GetChunkIndicesInSuperChunk(int64_t *chunkIndices, int64_t superChunkIndex) const = 0;
public:
  virtual VolumeDataLayout const *GetLayout() const = 0;

  virtual int   GetLOD() const = 0;
  virtual int   GetChannelIndex() const = 0;
  virtual VolumeDataChannelDescriptor GetChannelDescriptor() const = 0;
  virtual void  GetNumSamples(int (&numSamples)[Dimensionality_Max]) const = 0;

  virtual int64_t GetChunkCount() const = 0;
  virtual void  GetChunkMinMax(int64_t chunk, int (&min)[Dimensionality_Max], int (&max)[Dimensionality_Max]) const = 0;
  virtual void  GetChunkMinMaxExcludingMargin(int64_t chunk, int (&minExcludingMargin)[Dimensionality_Max], int (&maxExcludingMargin)[Dimensionality_Max]) const = 0;

  /// <summary>
  /// Get the volume data hash for the given chunk index.
  /// The value returned may be tested using the methods VolumeDataHash_IsDefined,
  /// VolumeDataHash_IsNoValue, and VolumeDataHash_IsConstant defined in VolumeData.h.
  /// </summary>
  /// <param name="chunkIndex">
  /// The chunk index to get the volume data hash for.
  /// </param>
  /// <returns>
  /// The volume data hash for the chunk.
  /// </returns>
  virtual uint64_t GetChunkVolumeDataHash(int64_t chunkIndex) const = 0;
  virtual int64_t GetChunkIndex(const int (&position)[Dimensionality_Max]) const = 0;

  /// <summary>
  /// Get the chunk index for this VolumeDataPageAccessor corresponding to the given chunk index in the primary channel.
  /// Because some channels can have mappings (e.g. one value per trace), the number of chunks can be less than in the primary
  /// channel and we need to have a mapping to figure out the chunk index in each channel that is produced together.
  /// </summary>
  /// <param name="primaryChannelChunkIndex">
  /// The index of the chunk in the primary channel (channel 0) that we want to map to a chunk index for this VolumeDataPageAccessor.
  /// </param>
  /// <returns>
  /// The chunk index for this VolumeDataPageAccessor corresponding to the given chunk index in the primary channel.
  /// </returns>
  virtual int64_t GetMappedChunkIndex(int64_t primaryChannelChunkIndex) const = 0;

  /// <summary>
  /// Get the primary channel chunk index corresponding to the given chunk index of this VolumeDataPageAccessor.
  /// In order to avoid creating duplicates requests when a channel is mapped, we need to know which primary channel chunk index is representative of
  /// a particular mapped chunk index.
  /// </summary>
  /// <param name="chunkIndex">
  /// The chunk index for this VolumeDataPageAccessor that we want the representative primary channel chunk index of.
  /// </param>
  /// <returns>
  /// The primary channel chunk index corresponding to the given chunk index for this VolumeDataPageAccessor.
  /// </returns>
  virtual int64_t GetPrimaryChannelChunkIndex(int64_t chunkIndex) const = 0;

  /// <summary>
  /// Get the number of super-chunks for this VolumeDataPageAccessor.
  /// Each super-chunk is an overlapping block of chunks from the remap source of this VolumeDataPageAccessor and the chunks in this VolumeDataPageAccessor.
  /// In order to produce the chunks as efficiently as possible (if there are more chunks than super-chunks), any code that iterates over all the chunks of
  /// a page accessor should iterate over the super-chunks and then over the chunks within each super-chunk.
  /// </summary>
  /// <returns>
  /// The number of super-chunks for this VolumeDataPageAccessor.
  /// </returns>
  virtual int64_t GetSuperChunkCount() const = 0;

  /// <summary>
  /// Get the list of chunks in the given super-chunk.
  /// Each super-chunk is an overlapping block of chunks from the remap source of this VolumeDataPageAccessor and the chunks in this VolumeDataPageAccessor.
  /// In order to produce the chunks as efficiently as possible (if there are more chunks than super-chunks), any code that iterates over all the chunks of
  /// a page accessor should iterate over the super-chunks and then over the chunks within each super-chunk.
  /// </summary>
  /// <param name="superChunkIndex">
  /// The super-chunk index for this VolumeDataPageAccessor that we want the list of chunks in.
  /// </param>
  /// <returns>
  /// The list of chunks in the super-chunk
  /// </returns>
  std::vector<int64_t>
  GetChunkIndicesInSuperChunk(int64_t superChunkIndex) const
  {
    std::vector<int64_t> chunkIndicesInSuperChunk(GetChunkCountInSuperChunk(superChunkIndex));
    GetChunkIndicesInSuperChunk(chunkIndicesInSuperChunk.data(), superChunkIndex);
    return chunkIndicesInSuperChunk;
  }

  virtual int   AddReference() = 0;
  virtual int   RemoveReference() = 0;

  virtual int   GetMaxPages() = 0;
  virtual void  SetMaxPages(int maxPages) = 0;

  virtual VolumeDataPage *CreatePage(int64_t chunkIndex) = 0;

  /// <summary>
  /// Copy a page of data from another VolumeDataPageAccessor with a compatible layout. This method is not blocking so if you want to access the copied data you need to call ReadPage which will block until the copy is done and return the copied data.
  /// </summary>
  /// <param name="chunkIndex">
  /// The chunk index to copy
  /// </param>
  /// <param name="source">
  /// The VolumeDataPageAccessor to copy data from
  /// </param>
  virtual void  CopyPage(int64_t chunkIndex, VolumeDataPageAccessor const &source) = 0;
  virtual VolumeDataPage *ReadPage(int64_t chunkIndex) = 0;
  virtual VolumeDataPage *ReadPageAtPosition(const int (&position)[Dimensionality_Max]) = 0;

  virtual void  Commit() = 0;
};

/// \class VolumeDataReadAccessor
/// \brief A class that provides random read access to the voxel values of a VDS
template <typename INDEX, typename T>
class VolumeDataReadAccessor
{
protected:
  IVolumeDataReadAccessor<INDEX, T> *
                        m_accessor;
public:
  VolumeDataLayout const *
                        GetLayout() const { return m_accessor ? m_accessor->GetLayout() : NULL; }

  int64_t               RegionCount() const { return m_accessor ? m_accessor->RegionCount() : 0; }

  IndexRegion<INDEX>    Region(int64_t region) const { return m_accessor ? m_accessor->Region(region) : IndexRegion<INDEX>(); }

  int64_t               RegionFromIndex(INDEX index) { return m_accessor ? m_accessor->RegionFromIndex(index) : 0; }

  IndexRegion<INDEX>    CurrentRegion() const { return m_accessor ? m_accessor->CurrentRegion() : IndexRegion<INDEX>(); }

  T                     GetValue(INDEX index) const { return m_accessor ? m_accessor->GetValue(index) : T(); }

                        VolumeDataReadAccessor() : m_accessor() {}

                        VolumeDataReadAccessor(IVolumeDataReadAccessor<INDEX, T> *accessor) : m_accessor(accessor) {}

                        VolumeDataReadAccessor(VolumeDataReadAccessor const &readAccessor) : m_accessor(readAccessor.m_accessor ? static_cast<IVolumeDataReadAccessor<INDEX, T>*>(readAccessor.m_accessor->GetManager().CloneVolumeDataAccessor(*readAccessor.m_accessor)) : NULL) {}

                       ~VolumeDataReadAccessor() { if(m_accessor) m_accessor->GetManager().DestroyVolumeDataAccessor(m_accessor); }
};

/// \class VolumeDataReadWriteAccessor
/// \brief A class that provides random read/write access to the voxel values of a VDS
template <typename INDEX, typename T>
class VolumeDataReadWriteAccessor : public VolumeDataReadAccessor<INDEX, T>
{
protected:
  using VolumeDataReadAccessor<INDEX, T>::m_accessor;
  IVolumeDataReadWriteAccessor<INDEX, T> *
                        Accessor() { return static_cast<IVolumeDataReadWriteAccessor<INDEX, T> *>(m_accessor); }
public:
  void                  SetValue(INDEX index, T value) { if(Accessor()) return Accessor()->SetValue(index, value); }
  void                  Commit() { if(Accessor()) return Accessor()->Commit(); }
  void                  Cancel() { if(Accessor()) return Accessor()->Cancel(); }

                        VolumeDataReadWriteAccessor() : VolumeDataReadAccessor<INDEX, T>() {}

                        VolumeDataReadWriteAccessor(IVolumeDataReadWriteAccessor<INDEX, T> *accessor) : VolumeDataReadAccessor<INDEX, T>(accessor) {}

                        VolumeDataReadWriteAccessor(VolumeDataReadWriteAccessor const &readWriteAccessor) :  VolumeDataReadAccessor<INDEX, T>(readWriteAccessor.m_accessor ? static_cast<IVolumeDataReadWriteAccessor<INDEX, T>*>(readWriteAccessor.m_accessor->GetManager().CloneVolumeDataAccessor(*readWriteAccessor.m_accessor)) : NULL) {}
};

//-----------------------------------------------------------------------------
// 2D VolumeDataAccessors
//-----------------------------------------------------------------------------

using VolumeData2DInterpolatingAccessorR64 = VolumeDataReadAccessor<FloatVector2, double>;
using VolumeData2DInterpolatingAccessorR32 = VolumeDataReadAccessor<FloatVector2, float>;

using VolumeData2DReadAccessorR64 = VolumeDataReadAccessor<IntVector2, double>;
using VolumeData2DReadAccessorU64 = VolumeDataReadAccessor<IntVector2, uint64_t>;
using VolumeData2DReadAccessorR32 = VolumeDataReadAccessor<IntVector2, float>;
using VolumeData2DReadAccessorU32 = VolumeDataReadAccessor<IntVector2, uint32_t>;
using VolumeData2DReadAccessorU16 = VolumeDataReadAccessor<IntVector2, uint16_t>;
using VolumeData2DReadAccessorU8 = VolumeDataReadAccessor<IntVector2, uint8_t>;
using VolumeData2DReadAccessor1Bit = VolumeDataReadAccessor<IntVector2, bool>;

using VolumeData2DReadWriteAccessorR64 = VolumeDataReadWriteAccessor<IntVector2, double>;
using VolumeData2DReadWriteAccessorU64 = VolumeDataReadWriteAccessor<IntVector2, uint64_t>;
using VolumeData2DReadWriteAccessorR32 = VolumeDataReadWriteAccessor<IntVector2, float>;
using VolumeData2DReadWriteAccessorU32 = VolumeDataReadWriteAccessor<IntVector2, uint32_t>;
using VolumeData2DReadWriteAccessorU16 = VolumeDataReadWriteAccessor<IntVector2, uint16_t>;
using VolumeData2DReadWriteAccessorU8 = VolumeDataReadWriteAccessor<IntVector2, uint8_t>;
using VolumeData2DReadWriteAccessor1Bit = VolumeDataReadWriteAccessor<IntVector2, bool>;

//-----------------------------------------------------------------------------
// 3D VolumeDataAccessors
//-----------------------------------------------------------------------------

using VolumeData3DInterpolatingAccessorR64 = VolumeDataReadAccessor<FloatVector3, double>;
using VolumeData3DInterpolatingAccessorR32 = VolumeDataReadAccessor<FloatVector3, float>;

using VolumeData3DReadAccessorR64 = VolumeDataReadAccessor<IntVector3, double>;
using VolumeData3DReadAccessorU64 = VolumeDataReadAccessor<IntVector3, uint64_t>;
using VolumeData3DReadAccessorR32 = VolumeDataReadAccessor<IntVector3, float>;
using VolumeData3DReadAccessorU32 = VolumeDataReadAccessor<IntVector3, uint32_t>;
using VolumeData3DReadAccessorU16 = VolumeDataReadAccessor<IntVector3, uint16_t>;
using VolumeData3DReadAccessorU8 = VolumeDataReadAccessor<IntVector3, uint8_t>;
using VolumeData3DReadAccessor1Bit = VolumeDataReadAccessor<IntVector3, bool>;

using VolumeData3DReadWriteAccessorR64 = VolumeDataReadWriteAccessor<IntVector3, double>;
using VolumeData3DReadWriteAccessorU64 = VolumeDataReadWriteAccessor<IntVector3, uint64_t>;
using VolumeData3DReadWriteAccessorR32 = VolumeDataReadWriteAccessor<IntVector3, float>;
using VolumeData3DReadWriteAccessorU32 = VolumeDataReadWriteAccessor<IntVector3, uint32_t>;
using VolumeData3DReadWriteAccessorU16 = VolumeDataReadWriteAccessor<IntVector3, uint16_t>;
using VolumeData3DReadWriteAccessorU8 = VolumeDataReadWriteAccessor<IntVector3, uint8_t>;
using VolumeData3DReadWriteAccessor1Bit = VolumeDataReadWriteAccessor<IntVector3, bool>;

//-----------------------------------------------------------------------------
// 4D VolumeDataAccessors
//-----------------------------------------------------------------------------

using VolumeData4DInterpolatingAccessorR64 = VolumeDataReadAccessor<FloatVector4, double>;
using VolumeData4DInterpolatingAccessorR32 = VolumeDataReadAccessor<FloatVector4, float>;

using VolumeData4DReadAccessorR64 = VolumeDataReadAccessor<IntVector4, double>;
using VolumeData4DReadAccessorU64 = VolumeDataReadAccessor<IntVector4, uint64_t>;
using VolumeData4DReadAccessorR32 = VolumeDataReadAccessor<IntVector4, float>;
using VolumeData4DReadAccessorU32 = VolumeDataReadAccessor<IntVector4, uint32_t>;
using VolumeData4DReadAccessorU16 = VolumeDataReadAccessor<IntVector4, uint16_t>;
using VolumeData4DReadAccessorU8 = VolumeDataReadAccessor<IntVector4, uint8_t>;
using VolumeData4DReadAccessor1Bit = VolumeDataReadAccessor<IntVector4, bool>;

using VolumeData4DReadWriteAccessorR64 = VolumeDataReadWriteAccessor<IntVector4, double>;
using VolumeData4DReadWriteAccessorU64 = VolumeDataReadWriteAccessor<IntVector4, uint64_t>;
using VolumeData4DReadWriteAccessorR32 = VolumeDataReadWriteAccessor<IntVector4, float>;
using VolumeData4DReadWriteAccessorU32 = VolumeDataReadWriteAccessor<IntVector4, uint32_t>;
using VolumeData4DReadWriteAccessorU16 = VolumeDataReadWriteAccessor<IntVector4, uint16_t>;
using VolumeData4DReadWriteAccessorU8 = VolumeDataReadWriteAccessor<IntVector4, uint8_t>;
using VolumeData4DReadWriteAccessor1Bit = VolumeDataReadWriteAccessor<IntVector4, bool>;

} // end namespace OpenVDS

#endif // OPENVDS_VOLUMEDATAACCESS_H
