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

#ifndef OPENVDS_EXCEPTIONS_H
#define OPENVDS_EXCEPTIONS_H

#include <exception>
#include "string.h"

namespace OpenVDS
{

class Exception : public std::exception
{
public:
  const char* what() const noexcept override { return GetErrorMessage(); }
  virtual const char *GetErrorMessage() const noexcept = 0;
};

template<int BUFFERSIZE>
class MessageBufferException : public Exception
{
public:
  enum
  {
    MESSAGE_BUFFER_SIZE = BUFFERSIZE
  };
private:
  char          m_messageBuffer[MESSAGE_BUFFER_SIZE];
  int           m_usedSize;
protected:
  MessageBufferException() : m_messageBuffer(), m_usedSize(0) {}
  MessageBufferException(MessageBufferException const &) = delete; /* derived classes have to add whatever they are copying from to the buffer */
  MessageBufferException& operator=(const MessageBufferException& other) = delete;

  const char *AddToBuffer(const char *message)
  {
    if(m_usedSize == MESSAGE_BUFFER_SIZE || !message)
    {
      return "";
    }

    const char *start = &m_messageBuffer[m_usedSize];

    while(*message && m_usedSize < MESSAGE_BUFFER_SIZE - 1)
    {
      m_messageBuffer[m_usedSize++] = *message++;
    }
    m_messageBuffer[m_usedSize++] = '\0';

    return start;
  }

  void ClearBuffer()
  {
    memset(m_messageBuffer, 0, MESSAGE_BUFFER_SIZE);
    m_usedSize = 0;
  }
};

class FatalException : public MessageBufferException<16384>
{
  const char *m_errorMessage;
public:
  FatalException(const char* errorMessage) :    MessageBufferException(), m_errorMessage(AddToBuffer(errorMessage)) {}
  FatalException(const FatalException& other) : MessageBufferException(), m_errorMessage(AddToBuffer(other.m_errorMessage)) {}
  FatalException& operator=(const FatalException& other) { if(this != &other) { ClearBuffer(); m_errorMessage = AddToBuffer(other.m_errorMessage); } return *this; }

  const char *GetErrorMessage() const noexcept override { return m_errorMessage; }
};

class InvalidOperation : public MessageBufferException<512>
{
  const char *m_errorMessage;
public:
  InvalidOperation(const char *errorMessage) :      MessageBufferException(), m_errorMessage(AddToBuffer(errorMessage)) {}
  InvalidOperation(const InvalidOperation& other) : MessageBufferException(), m_errorMessage(AddToBuffer(other.m_errorMessage)) {}
  InvalidOperation& operator=(const InvalidOperation& other) { if(this != &other) { ClearBuffer(); m_errorMessage = AddToBuffer(other.m_errorMessage); } return *this; }

  const char *GetErrorMessage() const noexcept override { return m_errorMessage; }
};

class InvalidArgument : public MessageBufferException<512>
{
  const char *m_errorMessage;
  const char *m_parameterName;

public:
  InvalidArgument(const char* errorMessage, const char *parameterName) : MessageBufferException(), m_errorMessage(AddToBuffer(errorMessage)),         m_parameterName(AddToBuffer(parameterName)) {}
  InvalidArgument(const InvalidArgument& other) :                        MessageBufferException(), m_errorMessage(AddToBuffer(other.m_errorMessage)), m_parameterName(AddToBuffer(other.m_parameterName)) {}
  InvalidArgument& operator=(const InvalidArgument& other) { if(this != &other) { ClearBuffer(); m_errorMessage = AddToBuffer(other.m_errorMessage); m_parameterName = AddToBuffer(other.m_parameterName); } return *this; }

  const char *GetErrorMessage() const noexcept override { return m_errorMessage; }
  const char *GetParameterName() const noexcept { return m_parameterName; }
};

class IndexOutOfRangeException : public MessageBufferException<512>
{
  const char* m_errorMessage;
public:
  IndexOutOfRangeException(const char* errorMessage) :              MessageBufferException(), m_errorMessage(AddToBuffer(errorMessage)) {}
  IndexOutOfRangeException(const IndexOutOfRangeException& other) : MessageBufferException(), m_errorMessage(AddToBuffer(other.m_errorMessage)) {}
  IndexOutOfRangeException& operator=(const IndexOutOfRangeException& other) { if(this != &other) { ClearBuffer(); m_errorMessage = AddToBuffer(other.m_errorMessage); } return *this; }

  const char *GetErrorMessage() const noexcept override { return m_errorMessage; }
};

class ReadErrorException : public MessageBufferException<512>
{
  const char* m_errorMessage;
  int         m_errorCode;

public:
  ReadErrorException(const char* errorMessage, int errorCode) : MessageBufferException(), m_errorMessage(AddToBuffer(errorMessage)),         m_errorCode(errorCode) {}
  ReadErrorException(const ReadErrorException& other) :         MessageBufferException(), m_errorMessage(AddToBuffer(other.m_errorMessage)), m_errorCode(other.m_errorCode) {}
  ReadErrorException& operator=(const ReadErrorException& other) { if(this != &other) { ClearBuffer(); m_errorMessage = AddToBuffer(other.m_errorMessage); m_errorCode = other.m_errorCode; } return *this; }

  const char *GetErrorMessage() const noexcept override { return m_errorMessage; }
  int         GetErrorCode() const noexcept { return m_errorCode; }
};

} // end namespace OpenVDS

#endif // OPENVDS_EXCEPTIONS_H
