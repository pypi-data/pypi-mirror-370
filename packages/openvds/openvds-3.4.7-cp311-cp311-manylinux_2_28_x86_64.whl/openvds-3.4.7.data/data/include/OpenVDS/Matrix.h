#ifndef OPENVDS_MATRIX_H
#define OPENVDS_MATRIX_H
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

#include "Vector.h"
#include <math.h>

namespace OpenVDS
{

// column major matrix
template<typename T, size_t SIZE>
struct Matrix
{
  typedef T element_type;
  enum { element_count = SIZE * SIZE };

  Vector<T, SIZE> data[SIZE];

  Matrix()
    : data{}
  {}
};

using IntMatrix2x2 = Matrix<int,2>;
using IntMatrix3x3 = Matrix<int,3>;
using IntMatrix4x4 = Matrix<int,4>;

using FloatMatrix2x2 = Matrix<float, 2>;
using FloatMatrix3x3 = Matrix<float, 3>;
using FloatMatrix4x4 = Matrix<float, 4>;

using DoubleMatrix2x2 = Matrix<double, 2>;
using DoubleMatrix3x3 = Matrix<double, 3>;
using DoubleMatrix4x4 = Matrix<double, 4>;

template<size_t N>
using IntMatrix = Matrix<int, N>;
template<size_t N>
using FloatMatrix = Matrix<float, N>;
template<size_t N>
using DoubleMatrix = Matrix<double, N>;

} // end namespace OpenVDS

#endif // OPENVDS_MATRIX_H
