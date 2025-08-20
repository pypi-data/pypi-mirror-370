#include <OpenVDS/OpenVDS.h>
#include <OpenVDS/VolumeDataLayoutDescriptor.h>
#include <OpenVDS/VolumeDataAxisDescriptor.h>
#include <OpenVDS/VolumeDataChannelDescriptor.h>
#include <OpenVDS/KnownMetadata.h>
#include <OpenVDS/GlobalMetadataCommon.h>
#include <OpenVDS/MetadataContainer.h>
#include <OpenVDS/VolumeDataLayout.h>
#include <OpenVDS/VolumeDataAccess.h>
#include <Noise/SimplexNoiseKernel.h>

#include <functional>
#include <random>

inline void getScaleOffsetForFormat(float min, float max, bool novalue, OpenVDS::VolumeDataFormat format, float &scale, float &offset)
{
  switch (format)
  {
  case OpenVDS::VolumeDataFormat::Format_U8:
    scale = 1.f / (255.f - novalue) * (max - min);
    offset = min;
    break;
  case OpenVDS::VolumeDataFormat::Format_U16:
    scale = 1.f/(65535.f - novalue) * (max - min);
    offset = min;
    break;
  case OpenVDS::VolumeDataFormat::Format_R32:
  case OpenVDS::VolumeDataFormat::Format_U32:
  case OpenVDS::VolumeDataFormat::Format_R64:
  case OpenVDS::VolumeDataFormat::Format_U64:
  case OpenVDS::VolumeDataFormat::Format_1Bit:
  case OpenVDS::VolumeDataFormat::Format_Any:
    scale = 1.0f;
    offset = 0.0f;
  }
}

inline OpenVDS::VDS *generateSimpleInMemory3DVDS(int32_t samplesX = 100, int32_t samplesY = 100, int32_t samplesZ = 100, OpenVDS::VolumeDataChannelDescriptor::Format format = OpenVDS::VolumeDataChannelDescriptor::Format_R32, OpenVDS::VolumeDataLayoutDescriptor::BrickSize brickSize = OpenVDS::VolumeDataLayoutDescriptor::BrickSize_32, OpenVDS::IOManager *ioManager = nullptr)
{
  int negativeMargin = 4;
  int positiveMargin = 4;
  int brickSize2DMultiplier = 4;
  auto lodLevels = OpenVDS::VolumeDataLayoutDescriptor::LODLevels_None;
  auto layoutOptions = OpenVDS::VolumeDataLayoutDescriptor::Options_None;
  OpenVDS::VolumeDataLayoutDescriptor layoutDescriptor(brickSize, negativeMargin, positiveMargin, brickSize2DMultiplier, lodLevels, layoutOptions);

  std::vector<OpenVDS::VolumeDataAxisDescriptor> axisDescriptors;
  axisDescriptors.emplace_back(samplesX, KNOWNMETADATA_SURVEYCOORDINATE_INLINECROSSLINE_AXISNAME_SAMPLE, "ms", 0.0f, 4.f);
  axisDescriptors.emplace_back(samplesY, KNOWNMETADATA_SURVEYCOORDINATE_INLINECROSSLINE_AXISNAME_CROSSLINE, "", 1932.f, 2536.f);
  axisDescriptors.emplace_back(samplesZ, KNOWNMETADATA_SURVEYCOORDINATE_INLINECROSSLINE_AXISNAME_INLINE,    "", 9985.f, 10369.f);

  std::vector<OpenVDS::VolumeDataChannelDescriptor> channelDescriptors;
  float rangeMin = -0.1234f;
  float rangeMax = 0.1234f;
  float intScale = 1.0f;
  float intOffset = 0.0f;
  getScaleOffsetForFormat(rangeMin, rangeMax, true, format, intScale, intOffset);
  channelDescriptors.push_back(OpenVDS::VolumeDataChannelDescriptor(format, OpenVDS::VolumeDataChannelDescriptor::Components_1, AMPLITUDE_ATTRIBUTE_NAME, "", rangeMin, rangeMax, OpenVDS::VolumeDataMapping::Direct, 1, OpenVDS::VolumeDataChannelDescriptor::Default, 0.f, intScale, intOffset));

  OpenVDS::MetadataContainer metadataContainer;
  OpenVDS::Error error;
  if (ioManager)
  {
    return OpenVDS::Create(ioManager, layoutDescriptor, axisDescriptors, channelDescriptors, metadataContainer, error);
  }
  OpenVDS::InMemoryOpenOptions options;
  return OpenVDS::Create(options, layoutDescriptor, axisDescriptors, channelDescriptors, metadataContainer, error);
}

inline void fillVolumeDataPages(std::shared_ptr<OpenVDS::VolumeDataPageAccessor> pageAccessor, std::function<void(void*buffer, OpenVDS::VolumeDataFormat format, OpenVDS::VolumeIndexer3D const &outputIndexer)> fillPage)
{
  int32_t chunkCount = int32_t(pageAccessor->GetChunkCount());
  auto layout = pageAccessor->GetLayout();
  OpenVDS::VolumeDataFormat format = layout->GetChannelFormat(pageAccessor->GetChannelIndex());

  for (int i = 0; i < chunkCount; i++)
  {
    OpenVDS::VolumeDataPage *page =  pageAccessor->CreatePage(i);
    OpenVDS::VolumeIndexer3D outputIndexer(page, 0, 0, OpenVDS::Dimensions_012, layout);

    int pitch[OpenVDS::Dimensionality_Max];
    void *buffer = page->GetWritableBuffer(pitch);
    fillPage(buffer, format, outputIndexer);
    page->Release();
  }
  pageAccessor->Commit();
}

inline void fill3DVDSWithNoise(OpenVDS::VDS *vds, int32_t channel = 0, const OpenVDS::FloatVector3 &frequency = OpenVDS::FloatVector3(0.6f, 2.f, 4.f), bool createLODs = true)
{
  OpenVDS::VolumeDataAccessManager accessManager = OpenVDS::GetAccessManager(vds);

  std::shared_ptr<OpenVDS::VolumeDataPageAccessor> pageAccessor = accessManager.CreateVolumeDataPageAccessor(OpenVDS::Dimensions_012, channel, 0, 100, createLODs ? OpenVDS::VolumeDataAccessManager::AccessMode_Create : OpenVDS::VolumeDataAccessManager::AccessMode_CreateWithoutLODGeneration);
  //ASSERT_TRUE(pageAccessor);

  fillVolumeDataPages(pageAccessor, [frequency](void*buffer, OpenVDS::VolumeDataFormat format, OpenVDS::VolumeIndexer3D const &outputIndexer)
  {
    OpenVDS::CalculateNoise3D(buffer, format, outputIndexer, frequency, 0.021f, 0.f, true, 345);
  });

  OpenVDS::Error error;
  accessManager.Flush(error);
}

inline void fill3DVDSWithBitNoise(OpenVDS::VDS *vds, int32_t channel = 0)
{
  OpenVDS::VolumeDataAccessManager accessManager = OpenVDS::GetAccessManager(vds);

  std::shared_ptr<OpenVDS::VolumeDataPageAccessor> pageAccessor = accessManager.CreateVolumeDataPageAccessor(OpenVDS::Dimensions_012, channel, 0, 100, OpenVDS::VolumeDataAccessManager::AccessMode_Create);
  //ASSERT_TRUE(pageAccessor);

  std::mt19937 gen(123);
  std::bernoulli_distribution dist(0.8);

  fillVolumeDataPages(pageAccessor, [&gen, &dist](void*buffer, OpenVDS::VolumeDataFormat format, OpenVDS::VolumeIndexer3D const &outputIndexer)
  {
    for (int i = 0; i < outputIndexer.dataBlockSamples[2]; i++)
    for (int j = 0; j < outputIndexer.dataBlockSamples[1]; j++)
    for (int k = 0; k < outputIndexer.dataBlockSamples[0]; k++)
    {
      OpenVDS::WriteElement(static_cast<bool *>(buffer), outputIndexer.LocalIndexToBitDataIndex({k, j, i}), dist(gen));
    }
  });

  OpenVDS::Error error;
  accessManager.Flush(error);
}
