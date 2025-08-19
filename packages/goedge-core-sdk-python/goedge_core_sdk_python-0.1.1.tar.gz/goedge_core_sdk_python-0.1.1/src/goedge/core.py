# -*- coding: utf-8 -*-

"""
GoEdge Core SDK Python Wrapper

This module provides a Python interface to the GoEdge Core C SDK using ctypes.
It assumes that a pre-compiled shared library (e.g., 'libgoedge-core.so' on Linux)
is located in the same directory as this file.

You must compile the C SDK into a shared library and place it here.
For example, on Linux:
gcc -shared -fPIC -o libgoedge-core.so <source_files>.c -I<include_dirs> -ldbus-1 -lcjson
"""

import os
import sys
import ctypes
import ctypes.util # Import the util module

# --- Library Loading ---

def find_ge_library():
    """
    Finds the 'libge-core.so' shared library in a specific order of locations.
    Search Order:
    1. Directories listed in the LD_LIBRARY_PATH environment variable.
    2. Standard system library paths (using ctypes.util.find_library).
    3. The same directory as this script.
    """
    lib_full_name = 'libge-core.so'
    lib_short_name = 'ge-core'  # For find_library

    # 1. Search in LD_LIBRARY_PATH
    ld_path = os.environ.get('LD_LIBRARY_PATH')
    if ld_path:
        for path in ld_path.split(':'):
            if path:  # Ignore empty strings from trailing/double colons
                lib_path = os.path.join(path, lib_full_name)
                if os.path.exists(lib_path):
                    return lib_path

    # 2. Search in standard system paths
    lib_path = ctypes.util.find_library(lib_short_name)
    if lib_path:
        return lib_path

    # 3. Fallback to the project's root directory
    # two levels up from this file (src/goedge/core.py)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    lib_path = os.path.join(project_root, lib_full_name)
    if os.path.exists(lib_path):
        return lib_path

    return None

_lib_path = find_ge_library()

if _lib_path is None:
    print("Error: Could not find the C shared library 'libge-core.so'.")
    print("Search order:")
    print("  1. Directories in LD_LIBRARY_PATH")
    print("  2. Standard system library paths")
    print("  3. The script's own directory ({})".format(os.path.dirname(__file__)))
    print("Please ensure 'libge-core.so' is available in one of these locations.")
    sys.exit(1)

try:
    _lib = ctypes.CDLL(_lib_path)
except OSError as e:
    print("Error: Found library at '{}', but failed to load it.".format(_lib_path))
    print("Original error: {}".format(e))
    sys.exit(1)


# --- Constants and Enums (from ge_error.h, ge_core.h) ---

GE_SUCCESS = 0

# Log Levels
LOG_LEVEL_DEBUG = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_WARN = 2
LOG_LEVEL_ERROR = 3

# Data Types (ge_data_type_e)
GE_TYPE_INT = 0
GE_TYPE_BOOL = 1
GE_TYPE_FLOAT = 2
GE_TYPE_TEXT = 3
GE_TYPE_DATE = 4
GE_TYPE_ENUM = 5
GE_TYPE_STRUCT = 6
GE_TYPE_ARRAY = 7
GE_TYPE_DOUBLE = 8
GE_TYPE_UINT32 = 9
GE_TYPE_INT64 = 10
GE_TYPE_UINT64 = 11
GE_TYPE_JSON = 12


# --- Structures (from ge_core.h) ---

class GeDeviceData(ctypes.Structure):
    """
    Corresponds to the ge_device_data_t struct in C.
    """
    _fields_ = [
        ('type', ctypes.c_int),                    # ge_data_type_e
        ('key', ctypes.c_char * 64),
        ('value', ctypes.c_char * 256),
        ('group', ctypes.c_char * 64),
        ('timestamp', ctypes.c_ulonglong),
    ]

# --- Callback Function Types ---

GET_PROPERTIES_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_int,                               # dev_handle
    ctypes.POINTER(GeDeviceData),               # properties[]
    ctypes.c_int,                               # properties_count
    ctypes.c_void_p                             # usr_data
)

SET_PROPERTIES_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_int,                               # dev_handle
    ctypes.POINTER(GeDeviceData),               # properties[]
    ctypes.c_int,                               # properties_count
    ctypes.c_void_p                             # usr_data
)

CALL_SERVICE_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_int,                               # dev_handle
    ctypes.c_char_p,                            # service_name
    ctypes.POINTER(GeDeviceData),               # data[]
    ctypes.c_int,                               # data_count
    ctypes.POINTER(GeDeviceData),               # output_data[]
    ctypes.c_void_p                             # usr_data
)

TRIGGER_COLLECT_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_int,                               # dev_handle
    ctypes.POINTER(GeDeviceData),               # properties[]
    ctypes.c_int,                               # properties_count
    ctypes.c_void_p                             # usr_data
)

CONFIG_CHANGED_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_char_p,                            # key
    ctypes.c_char_p                             # config
)

MESSAGE_NOTIFY_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_char_p,                            # dest
    ctypes.c_char_p,                            # message_name
    ctypes.c_char_p                             # payload
)

MESSAGE_NOTIFY_CALLBACK2 = ctypes.CFUNCTYPE(
    ctypes.c_int,                               # return type
    ctypes.c_char_p,                            # dest
    ctypes.c_char_p,                            # message_name
    ctypes.c_char_p,                            # payload
    ctypes.c_void_p                             # user_data
)


class GeDeviceCallback(ctypes.Structure):
    """
    Corresponds to the ge_device_callback_t struct in C.
    """
    _fields_ = [
        ('get_properties_cb', GET_PROPERTIES_CALLBACK),
        ('set_properties_cb', SET_PROPERTIES_CALLBACK),
        ('call_service_cb', CALL_SERVICE_CALLBACK),
        ('trigger_collect_cb', TRIGGER_COLLECT_CALLBACK),
        ('service_output_max_count', ctypes.c_int),
    ]


# --- C Function Prototypes ---

# Core functions
_lib.ge_core_init.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
_lib.ge_core_init.restype = ctypes.c_int

_lib.ge_core_init2.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
_lib.ge_core_init2.restype = ctypes.c_int

_lib.ge_core_exit.argtypes = []
_lib.ge_core_exit.restype = None

# Device management functions
_lib.ge_register_and_online_by_device_name.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(GeDeviceCallback), ctypes.c_void_p]
_lib.ge_register_and_online_by_device_name.restype = ctypes.c_int

_lib.ge_device_offline.argtypes = [ctypes.c_int]
_lib.ge_device_offline.restype = ctypes.c_int

_lib.ge_device_online.argtypes = [ctypes.c_int]
_lib.ge_device_online.restype = ctypes.c_int

# Data reporting functions
_lib.ge_report_properties.argtypes = [ctypes.c_int, ctypes.POINTER(GeDeviceData), ctypes.c_int]
_lib.ge_report_properties.restype = ctypes.c_int

_lib.ge_report_event.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(GeDeviceData), ctypes.c_int]
_lib.ge_report_event.restype = ctypes.c_int

# Config functions
_lib.ge_get_config_size.argtypes = [ctypes.c_char_p]
_lib.ge_get_config_size.restype = ctypes.c_int

_lib.ge_get_module_config_size.argtypes = []
_lib.ge_get_module_config_size.restype = ctypes.c_int

_lib.ge_get_module_config.argtypes = [ctypes.c_char_p, ctypes.c_int]
_lib.ge_get_module_config.restype = ctypes.c_int


_lib.ge_get_config.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
_lib.ge_get_config.restype = ctypes.c_int

_lib.ge_register_config_changed_callback.argtypes = [ctypes.c_char_p, CONFIG_CHANGED_CALLBACK]
_lib.ge_register_config_changed_callback.restype = ctypes.c_int

# Message functions
_lib.ge_register_message_notify_callback.argtypes = [ctypes.c_char_p, ctypes.c_char_p, MESSAGE_NOTIFY_CALLBACK]
_lib.ge_register_message_notify_callback.restype = ctypes.c_int

_lib.ge_register_message_notify_callback2.argtypes = [ctypes.c_char_p, ctypes.c_char_p, MESSAGE_NOTIFY_CALLBACK2, ctypes.c_void_p]
_lib.ge_register_message_notify_callback2.restype = ctypes.c_int

_lib.ge_send_message.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_lib.ge_send_message.restype = ctypes.c_int

# TSL functions
_lib.ge_get_tsl_size.argtypes = [ctypes.c_char_p]
_lib.ge_get_tsl_size.restype = ctypes.c_int

_lib.ge_get_tsl.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
_lib.ge_get_tsl.restype = ctypes.c_int

# Logging
_lib.ge_log.argtypes = [ctypes.c_int, ctypes.c_char_p]
_lib.ge_log.restype = ctypes.c_int


# --- Python Wrapper Functions ---

def core_init(module_name, worker_thread_nums, log_level):
    """Initializes the core SDK."""
    return _lib.ge_core_init(module_name.encode('utf-8'), worker_thread_nums, log_level)

def core_init2(module_name, worker_thread_nums, log_level, flags):
    """Initializes the core SDK with flags."""
    return _lib.ge_core_init2(module_name.encode('utf-8'), worker_thread_nums, log_level, flags)

def core_exit():
    """Exits and cleans up the core SDK."""
    _lib.ge_core_exit()

def register_and_online_by_device_name(product_key, device_name, device_cb, usr_data=None):
    """Registers a device using its name and brings it online."""
    return _lib.ge_register_and_online_by_device_name(
        product_key.encode('utf-8'),
        device_name.encode('utf-8'),
        ctypes.byref(device_cb),
        usr_data
    )

def device_offline(dev_handle):
    """Takes a device offline."""
    return _lib.ge_device_offline(dev_handle)

def device_online(dev_handle):
    """Brings an offline device online."""
    return _lib.ge_device_online(dev_handle)

def report_properties(dev_handle, properties):
    """Reports device properties."""
    if not isinstance(properties, list):
        properties = [properties]
    
    prop_array = (GeDeviceData * len(properties))()
    for i, p in enumerate(properties):
        prop_array[i] = p
        
    return _lib.ge_report_properties(dev_handle, prop_array, len(properties))

def report_event(dev_handle, event_name, data):
    """Reports a device event."""
    if not isinstance(data, list):
        data = [data]

    data_array = (GeDeviceData * len(data))()
    for i, d in enumerate(data):
        data_array[i] = d
        
    return _lib.ge_report_event(dev_handle, event_name.encode('utf-8'), data_array, len(data))

def get_config(key):
    """Gets a configuration value for a given key."""
    size = _lib.ge_get_config_size(key.encode('utf-8'))
    if size <= 0:
        return None
    
    buffer = ctypes.create_string_buffer(size)
    ret = _lib.ge_get_config(key.encode('utf-8'), buffer, size)
    
    if ret == GE_SUCCESS:
        return buffer.value.decode('utf-8')
    return None

def get_module_config():
    """Gets the module's configuration."""
    size = _lib.ge_get_module_config_size()
    if size <= 0:
        return None

    buffer = ctypes.create_string_buffer(size)
    ret = _lib.ge_get_module_config(buffer, size)

    if ret == GE_SUCCESS:
        return buffer.value.decode('utf-8')
    return None

def register_config_changed_callback(key, callback):
    """Registers a callback for configuration changes."""
    return _lib.ge_register_config_changed_callback(key.encode('utf-8'), callback)

def register_message_notify_callback(dest, message_name, callback):
    """Registers a callback for message notifications."""
    return _lib.ge_register_message_notify_callback(
        dest.encode('utf-8'),
        message_name.encode('utf-8'),
        callback
    )

def register_message_notify_callback2(dest, message_name, callback, user_data=None):
    """Registers a callback for message notifications with user data."""
    return _lib.ge_register_message_notify_callback2(
        dest.encode('utf-8'),
        message_name.encode('utf-8'),
        callback,
        user_data
    )

def send_message(message_name, dest, payload):
    """Sends a message."""
    return _lib.ge_send_message(
        message_name.encode('utf-8'),
        dest.encode('utf-8'),
        payload.encode('utf-8')
    )

def get_tsl(product_key):
    """Gets the Thing Specification Language (TSL) for a product."""
    size = _lib.ge_get_tsl_size(product_key.encode('utf-8'))
    if size <= 0:
        return None
        
    buffer = ctypes.create_string_buffer(size)
    ret = _lib.ge_get_tsl(product_key.encode('utf-8'), buffer, size)
    
    if ret == GE_SUCCESS:
        return buffer.value.decode('utf-8')
    return None

def log(level, log_message):
    """Sends a message to the SDK's log."""
    return _lib.ge_log(level, log_message.encode('utf-8'))