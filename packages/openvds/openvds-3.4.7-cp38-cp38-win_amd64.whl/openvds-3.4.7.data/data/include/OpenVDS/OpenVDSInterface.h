/****************************************************************************
** Copyright 2019 The Open Group
** Copyright 2019 Bluware, Inc.
** Copyright 2020 Microsoft Corp.
** Copyright 2020 Google, Inc.
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

#ifndef OPENVDS_OPENVDSINTERFACE_H
#define OPENVDS_OPENVDSINTERFACE_H

#include <OpenVDS/openvds_export.h>
#include <OpenVDS/Log.h>

#include <cstdint>
#include <string>
#include <vector>
#include <tuple>

namespace OpenVDS
{
typedef struct VDS *VDSHandle;
typedef struct VDSError Error;

class VolumeDataLayout;
class MetadataReadAccess;
class MetadataWriteAccess;
class VolumeDataAccessManager;
class VolumeDataPageAccessor;
class VolumeDataLayoutDescriptor;
class VolumeDataAxisDescriptor;
class VolumeDataChannelDescriptor;
class GlobalState;
class IOManager;
class IVolumeDataAccessManager;
struct WaveletAdaptiveLevel;

struct OpenOptions;

enum class CompressionMethod;

template<typename T>
struct VectorWrapper
{
  VectorWrapper()
    : data(nullptr)
    , size(0)
  {}
  VectorWrapper(const std::vector<T> &toWrap)
    : data(toWrap.data())
    , size(toWrap.size())
  {}

  const T *data;
  size_t size;
};

struct StringWrapper
{
  StringWrapper()
    : data(nullptr)
    , size(0)
  {}

  StringWrapper(const std::string& toWrap)
    : data(toWrap.c_str())
    , size(toWrap.size())
  {}

  template<size_t SIZE>
  StringWrapper(const char(&toWrap)[SIZE])
    : data(toWrap)
    , size(SIZE - 1)
  {}
#ifdef JAVA_WRAPPER_GENERATOR
  StringWrapper(const char* cstr)
    : data(cstr)
    , size(strlen(cstr))
  {}
#endif

  const char* data;
  size_t size;
};

/// <summary>
/// The OpenVDS versioning interface is a stable base class for the OpenVDS global interface that can be used to check what version of the OpenVDS interface is provided
/// </summary>
class OpenVDSVersioningInterface
{
protected:
           OpenVDSVersioningInterface() {}
  virtual ~OpenVDSVersioningInterface() {}
public:
  virtual const char               *GetOpenVDSName() = 0;
  virtual const char               *GetOpenVDSVersion() = 0;
  virtual void                      GetOpenVDSVersion(int &major, int &minor, int &patch) = 0;
  virtual const char               *GetOpenVDSRevision() = 0;
};

/// <summary>
/// The OpenVDS interface is used to provide a versioned entrypoint for the API with wrappers for standard types to ensure ABI compatibility
/// </summary>
class OpenVDSInterface : public OpenVDSVersioningInterface
{
protected:
           OpenVDSInterface() {}
  virtual ~OpenVDSInterface() {}
public:
  typedef void (*ErrorHandler)(Error *error, int errorCode, const char *errorMessage);
  typedef void (*WaveletAdaptiveLevelsHandler)(std::vector<WaveletAdaptiveLevel> *waveletAdaptiveLevelsVector, float compressionTolerance, float compressionRatio, int64_t compressedSize);

  virtual OpenOptions*              CreateOpenOptions(StringWrapper url, StringWrapper connectionString, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual bool                      IsSupportedProtocol(StringWrapper url) = 0;
  virtual VDSHandle                 Open(StringWrapper url, StringWrapper connectionString, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 OpenWithAdaptiveCompressionTolerance(StringWrapper url, StringWrapper connectionString, float waveletAdaptiveTolerance, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 OpenWithAdaptiveCompressionRatio(StringWrapper url, StringWrapper connectionString, float waveletAdaptiveRatio, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 Open(const OpenOptions& options, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 Open(IOManager*ioManager, LogLevel logLevel, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual bool                      IsCompressionMethodSupported(CompressionMethod compressionMethod) = 0;
  virtual VDSHandle                 Create(StringWrapper url, StringWrapper connectionString, VolumeDataLayoutDescriptor const& layoutDescriptor, VectorWrapper<VolumeDataAxisDescriptor> axisDescriptors, VectorWrapper<VolumeDataChannelDescriptor> channelDescriptors, MetadataReadAccess const& metadata, CompressionMethod compressionMethod, float compressionTolerance, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 Create(const OpenOptions& options, VolumeDataLayoutDescriptor const& layoutDescriptor, VectorWrapper<VolumeDataAxisDescriptor> axisDescriptors, VectorWrapper<VolumeDataChannelDescriptor> channelDescriptors, MetadataReadAccess const& metadata, CompressionMethod compressionMethod, float compressionTolerance, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VDSHandle                 Create(IOManager* ioManager, VolumeDataLayoutDescriptor const &layoutDescriptor, VectorWrapper<VolumeDataAxisDescriptor> axisDescriptors, VectorWrapper<VolumeDataChannelDescriptor> channelDescriptors, MetadataReadAccess const &metadata, CompressionMethod compressionMethod, float compressionTolerance, LogLevel logLevel, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual VolumeDataLayout         *GetLayout(VDSHandle handle) = 0;
  virtual IVolumeDataAccessManager *GetAccessManagerInterface(VDSHandle handle) = 0;
  virtual MetadataWriteAccess      *GetMetadataWriteAccessInterface(VDSHandle handle) = 0;
  virtual CompressionMethod         GetCompressionMethod(VDSHandle handle) = 0;
  virtual float                     GetCompressionTolerance(VDSHandle handle) = 0;
  virtual void                      Close(VDSHandle handle, bool flush) = 0;
  virtual void                      Close(VDSHandle handle, bool flush, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual void                      RetryableClose(VDSHandle handle, bool flush) = 0;
  virtual void                      RetryableClose(VDSHandle handle, bool flush, ErrorHandler errorHandler, Error *error=nullptr) = 0;
  virtual GlobalState              *GetGlobalState() = 0;
  virtual int64_t                   GetWaveletCompressedSize(VDSHandle handle) = 0;
  virtual int64_t                   GetWaveletUncompressedSize(VDSHandle handle) = 0;
  virtual void                      GetWaveletAdaptiveLevels(VDSHandle handle, WaveletAdaptiveLevelsHandler WaveletAdaptiveLevelsHandler, std::vector<WaveletAdaptiveLevel> *waveletAdaptiveLevelsVector) = 0;
};

#ifndef OPENVDS_REPLACE_INTERFACE
OPENVDS_EXPORT OpenVDSInterface &GetOpenVDSInterface(const char* version);
OPENVDS_EXPORT void              SetOpenVDSInterface(OpenVDSInterface &openVDSInterface);
#endif

} // end namespace OpenVDS

#endif // OPENVDS_OPENVDSINTERFACE_H
