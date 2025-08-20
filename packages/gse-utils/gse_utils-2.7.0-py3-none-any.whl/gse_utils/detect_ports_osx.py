# Serial port detection for macOS
# Heavily based on https://github.com/pyserial/pyserial/blob/master/serial/tools/list_ports_osx.py
# and https://github.com/pyserial/pyserial/pull/784

# GSE Proprietary Software License
# Copyright (c) 2025 Global Satellite Engineering, LLC. All rights reserved.
# This software and associated documentation files (the "Software") are the proprietary and confidential information of Global Satellite Engineering, LLC ("GSE"). The Software is provided solely for the purpose of operating applications distributed by GSE and is subject to the following conditions:

# 1. NO RIGHTS GRANTED: This license does not grant any rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell the Software.
# 2. RESTRICTED ACCESS: You may only access the Software as part of a GSE application package and only to the extent necessary for operation of that application package.
# 3. PROHIBITION ON REVERSE ENGINEERING: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
# 4. PROPRIETARY NOTICES: You must retain all copyright, patent, trademark, and attribution notices present in the Software.
# 5. NO WARRANTIES: The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# 6. LIMITATION OF LIABILITY: In no event shall GSE be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.
# 7. TERMINATION: This license will terminate automatically if you fail to comply with any of the terms and conditions of this license. Upon termination, you must destroy all copies of the Software in your possession.

# THE SOFTWARE IS PROTECTED BY UNITED STATES COPYRIGHT LAW AND INTERNATIONAL TREATY. UNAUTHORIZED REPRODUCTION OR DISTRIBUTION IS SUBJECT TO CIVIL AND CRIMINAL PENALTIES.

import ctypes
from . import constants as ct

iokit = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/IOKit.framework/IOKit')
cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

# kIOMasterPortDefault is no longer exported in BigSur but no biggie, using NULL works just the same
kIOMasterPortDefault = 0 # WAS: ctypes.c_void_p.in_dll(iokit, "kIOMasterPortDefault")
kCFAllocatorDefault = ctypes.c_void_p.in_dll(cf, "kCFAllocatorDefault")

kCFStringEncodingMacRoman = 0
kCFStringEncodingUTF8 = 0x08000100

# defined in `IOKit/usb/USBSpec.h`
kUSBVendorString = 'USB Vendor Name'
kUSBSerialNumberString = 'USB Serial Number'

# `io_name_t` defined as `typedef char io_name_t[128];`
# in `device/device_types.h`
io_name_size = 128

# defined in `mach/kern_return.h`
KERN_SUCCESS = 0
# kern_return_t defined as `typedef int kern_return_t;` in `mach/i386/kern_return.h`
kern_return_t = ctypes.c_int

iokit.IOServiceMatching.restype = ctypes.c_void_p

iokit.IOServiceGetMatchingServices.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IOServiceGetMatchingServices.restype = kern_return_t

iokit.IORegistryEntryGetParentEntry.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IOServiceGetMatchingServices.restype = kern_return_t

iokit.IORegistryEntryCreateCFProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
iokit.IORegistryEntryCreateCFProperty.restype = ctypes.c_void_p

iokit.IORegistryEntryGetPath.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IORegistryEntryGetPath.restype = kern_return_t

iokit.IORegistryEntryGetName.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
iokit.IORegistryEntryGetName.restype = kern_return_t

iokit.IOObjectGetClass.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
iokit.IOObjectGetClass.restype = kern_return_t

iokit.IOObjectRelease.argtypes = [ctypes.c_void_p]

cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32]
cf.CFStringCreateWithCString.restype = ctypes.c_void_p

cf.CFStringGetCStringPtr.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
cf.CFStringGetCStringPtr.restype = ctypes.c_char_p

cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_uint32]
cf.CFStringGetCString.restype = ctypes.c_bool

cf.CFNumberGetValue.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
cf.CFNumberGetValue.restype = ctypes.c_void_p

# void CFRelease ( CFTypeRef cf );
cf.CFRelease.argtypes = [ctypes.c_void_p]
cf.CFRelease.restype = None

# CFNumber type defines
kCFNumberSInt8Type = 1
kCFNumberSInt16Type = 2
kCFNumberSInt32Type = 3
kCFNumberSInt64Type = 4

def get_string_property(device_type, property):
    """
    Search the given device for the specified string property

    @param device_type Type of Device
    @param property String to search for
    @return Python string containing the value, or None if not found.
    """
    key = cf.CFStringCreateWithCString(
            kCFAllocatorDefault,
            property.encode("utf-8"),
            kCFStringEncodingUTF8)

    CFContainer = iokit.IORegistryEntryCreateCFProperty(
            device_type,
            key,
            kCFAllocatorDefault,
            0)
    output = None

    if CFContainer:
        output = cf.CFStringGetCStringPtr(CFContainer, 0)
        if output is not None:
            output = output.decode('utf-8')
        else:
            buffer = ctypes.create_string_buffer(io_name_size);
            success = cf.CFStringGetCString(CFContainer, ctypes.byref(buffer), io_name_size, kCFStringEncodingUTF8)
            if success:
                output = buffer.value.decode('utf-8')
        cf.CFRelease(CFContainer)
    return output


def get_int_property(device_type, property, cf_number_type):
    """
    Search the given device for the specified string property

    @param device_type Device to search
    @param property String to search for
    @param cf_number_type CFType number

    @return Python string containing the value, or None if not found.
    """
    key = cf.CFStringCreateWithCString(
            kCFAllocatorDefault,
            property.encode("utf-8"),
            kCFStringEncodingUTF8)

    CFContainer = iokit.IORegistryEntryCreateCFProperty(
            device_type,
            key,
            kCFAllocatorDefault,
            0)

    if CFContainer:
        if (cf_number_type == kCFNumberSInt32Type):
            number = ctypes.c_uint32()
        elif (cf_number_type == kCFNumberSInt16Type):
            number = ctypes.c_uint16()
        cf.CFNumberGetValue(CFContainer, cf_number_type, ctypes.byref(number))
        cf.CFRelease(CFContainer)
        return number.value
    return None

def IORegistryEntryGetName(device):
    devicename = ctypes.create_string_buffer(io_name_size);
    res = iokit.IORegistryEntryGetName(device, ctypes.byref(devicename))
    if res != KERN_SUCCESS:
        return None
    # this works in python2 but may not be valid. Also I don't know if
    # this encoding is guaranteed. It may be dependent on system locale.
    return devicename.value.decode('utf-8')

def IOObjectGetClass(device):
    classname = ctypes.create_string_buffer(io_name_size)
    iokit.IOObjectGetClass(device, ctypes.byref(classname))
    return classname.value

def GetParentDeviceByType(device, parent_type):
    """ Find the first parent of a device that implements the parent_type
        @param IOService Service to inspect
        @return Pointer to the parent type, or None if it was not found.
    """
    # First, try to walk up the IOService tree to find a parent of this device that is a IOUSBDevice.
    parent_type = parent_type.encode('utf-8')
    while IOObjectGetClass(device) != parent_type:
        parent = ctypes.c_void_p()
        response = iokit.IORegistryEntryGetParentEntry(
                device,
                "IOService".encode("utf-8"),
                ctypes.byref(parent))
        # If we weren't able to find a parent for the device, we're done.
        if response != KERN_SUCCESS:
            return None
        device = parent
    return device


def GetIOServicesByType(service_type):
    """
    returns iterator over specified service_type
    """
    serial_port_iterator = ctypes.c_void_p()

    iokit.IOServiceGetMatchingServices(
            kIOMasterPortDefault,
            iokit.IOServiceMatching(service_type.encode('utf-8')),
            ctypes.byref(serial_port_iterator))

    services = []
    while iokit.IOIteratorIsValid(serial_port_iterator):
        service = iokit.IOIteratorNext(serial_port_iterator)
        if not service:
            break
        services.append(service)
    iokit.IOObjectRelease(serial_port_iterator)
    return services


def location_to_string(locationID):
    """
    helper to calculate port and bus number from locationID
    """
    loc = ['{}-'.format(locationID >> 24)]
    while locationID & 0xf00000:
        if len(loc) > 1:
            loc.append('.')
        loc.append('{}'.format((locationID >> 20) & 0xf))
        locationID <<= 4
    return ''.join(loc)

# Enrty point: check USB serial ports for the known interface names
def platform_detect():
    res = []
    for service in GetIOServicesByType('IOSerialBSDClient'):
        device = get_string_property(service, "IOCalloutDevice")
        if device:
            usb_device = GetParentDeviceByType(service, "IOUSBHostInterface")
            if not usb_device: # IOUSBInterface is deprecated
                usb_device = GetParentDeviceByType(service, "IOUSBInterface")
            if usb_device and get_string_property(usb_device, kUSBVendorString) == ct.USB_VENDOR_STRING:
                serial = get_string_property(usb_device, kUSBSerialNumberString)
                if (name := get_string_property(usb_device, "kUSBString")) == ct.USB_MGMT_PORT_NAME:
                    res.append((serial, ct.USB_MGMT_PORT_NAME, device))
                elif name == ct.USB_LOGS_PORT_NAME:
                    res.append((serial, ct.USB_LOGS_PORT_NAME, device))
                elif name == ct.USB_CONSOLE_PORT_NAME:
                    res.append((serial, ct.USB_CONSOLE_PORT_NAME, device))
    return res