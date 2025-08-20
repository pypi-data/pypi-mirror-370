/****************************************************************************
** Copyright 2022 The Open Group
** Copyright 2022 Bluware, Inc.
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

#pragma once

#include "OpenVDS/OpenVDS.h"
#include "SEGY.h"

namespace SEGY
{

// VDS-related data conversion functions

OPENVDS_EXPORT OpenVDS::VolumeDataFormat convertSegyFormat(SEGY::BinaryHeader::DataSampleFormatCode dataSampleFormatCode, OpenVDS::Error& error);

template<SEGY::BinaryHeader::DataSampleFormatCode dataSampleFormatCode>
int32_t
GetVDSIntegerOffsetForDataSampleFormat()
{
  switch (dataSampleFormatCode)
  {
    // VDS does not support IntegerOffset for Int32 and Int64 so updating this function
    // is not enough to properly handle Int32 types without converting them to float.
  case BinaryHeader::DataSampleFormatCode::Int16:
    return 32768;
  case BinaryHeader::DataSampleFormatCode::Int8:
    return 128;
  default:
    return 0;
  }
}

OPENVDS_EXPORT int32_t GetVDSIntegerOffsetForDataSampleFormat(BinaryHeader::DataSampleFormatCode dataSampleFormatCode);

inline float
IntToFloat(int fconv)
{
  union
  {
    int i;
    float f;
  } conv;
  conv.i = fconv;
  return conv.f;
}

inline int
FloatToInt(float fconv)
{
  union
  {
    int i;
    float f;
  } conv;
  conv.f = fconv;
  return conv.i;
}

} // end namespace SEGY
