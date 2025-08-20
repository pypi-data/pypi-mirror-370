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

#ifndef OPENVDS_VALUERANGEESTIMATOR_H
#define OPENVDS_VALUERANGEESTIMATOR_H

#include <vector>
#include <algorithm>

namespace OpenVDS
{

template<class T>
class HeapBasedValueRangeEstimator
{
private:
  std::vector<T>        m_minHeap,
                        m_maxHeap;
  const int             m_heapSizeMax;

  int                   m_nanCount;

public:
  HeapBasedValueRangeEstimator(float percentile, uint64_t sampleCount)
    : m_heapSizeMax(int(((100.0f - percentile) / 100.0f) * sampleCount / 2) + 1)
    , m_nanCount(0)
  {
    m_minHeap.reserve(m_heapSizeMax);
    m_maxHeap.reserve(m_heapSizeMax);
  }

  template<typename InputIt, typename IsNan>
  void UpdateValueRange(InputIt first, InputIt last, IsNan isNan)
  {
    std::for_each(first, last, [this, isNan](const T& element)
      {
        if (isNan(element))
        {
          ++m_nanCount;
          return;
        }
        if (int(m_minHeap.size()) < m_heapSizeMax)
        {
          m_minHeap.push_back(element);
          std::push_heap(m_minHeap.begin(), m_minHeap.end(), std::less<T>());
        }
        else if (element < m_minHeap[0])
        {
          std::pop_heap(m_minHeap.begin(), m_minHeap.end(), std::less<T>());
          m_minHeap.back() = element;
          std::push_heap(m_minHeap.begin(), m_minHeap.end(), std::less<T>());
        }

        if (int(m_maxHeap.size()) < m_heapSizeMax)
        {
          m_maxHeap.push_back(element);
          std::push_heap(m_maxHeap.begin(), m_maxHeap.end(), std::greater<T>());
        }
        else if (element > m_maxHeap[0])
        {
          std::pop_heap(m_maxHeap.begin(), m_maxHeap.end(), std::greater<T>());
          m_maxHeap.back() = element;
          std::push_heap(m_maxHeap.begin(), m_maxHeap.end(), std::greater<T>());
        }
      });
  }

  template<typename InputIt>
  void UpdateValueRange(InputIt first, InputIt last)
  {
    UpdateValueRange(first, last, [](T) {return false; });
  }
  void GetValueRange(float& valueRangeMin, float& valueRangeMax)
  {
    if (!m_minHeap.empty())
    {
      if (m_minHeap[0] != m_maxHeap[0])
      {
        valueRangeMin = m_minHeap[0];
        valueRangeMax = m_maxHeap[0];
      }
      else
      {
        valueRangeMin = m_minHeap[0];
        valueRangeMax = valueRangeMin + 1.0f;
      }
    }
    else
    {
      valueRangeMin = 0.0f;
      valueRangeMax = 1.0f;
    }
  }

  int NaNCount() const
  {
    return m_nanCount;
  }
};

} // end namespace OpenVDS

#endif // OPENVDS_VALUERANGEESTIMATOR_H
