############################################################################
# Copyright 2019 The Open Group
# Copyright 2019 Bluware, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###########################################################################/

import openvds.core
from openvds.core import *
from .volumedataaccess import VolumeDataAccessManager

openvds.core.IVolumeDataAccessManager.AccessMode = openvds.core.VolumeDataPageAccessor.AccessMode
openvds.core.VolumeDataAccessManager.AccessMode = openvds.core.VolumeDataPageAccessor.AccessMode
VolumeDataAccessManager.AccessMode = openvds.core.VolumeDataPageAccessor.AccessMode

VolumeDataAccessManager.AccessMode = VolumeDataPageAccessor.AccessMode

# Add alias for VDSError
Error = VDSError;

# Add global enums in local scope
VolumeDataChannelDescriptor.Format     = VolumeDataFormat
VolumeDataChannelDescriptor.Components = VolumeDataComponents

# Add unscoped enum keys
VolumeDataChannelDescriptor.Format_Any  = VolumeDataFormat.Format_Any
VolumeDataChannelDescriptor.Format_1Bit = VolumeDataFormat.Format_1Bit
VolumeDataChannelDescriptor.Format_U8   = VolumeDataFormat.Format_U8
VolumeDataChannelDescriptor.Format_U16  = VolumeDataFormat.Format_U16
VolumeDataChannelDescriptor.Format_R32  = VolumeDataFormat.Format_R32
VolumeDataChannelDescriptor.Format_U32  = VolumeDataFormat.Format_U32
VolumeDataChannelDescriptor.Format_R64  = VolumeDataFormat.Format_R64
VolumeDataChannelDescriptor.Format_U64  = VolumeDataFormat.Format_U64

VolumeDataChannelDescriptor.Components_1 = VolumeDataComponents.Components_1
VolumeDataChannelDescriptor.Components_2 = VolumeDataComponents.Components_2
VolumeDataChannelDescriptor.Components_4 = VolumeDataComponents.Components_4

def getAccessManager(handle: int):
    """Get the VolumeDataAccessManager for a VDS
    
    Parameter `handle`:
        The handle of the VDS
    
    Returns:
        The VolumeDataAccessManager of the VDS
    """
    return VolumeDataAccessManager(handle)
