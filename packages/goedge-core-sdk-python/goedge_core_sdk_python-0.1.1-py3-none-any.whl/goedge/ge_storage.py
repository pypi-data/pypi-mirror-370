# -*- coding: utf-8 -*-

"""
GoEdge Storage SDK Python Wrapper

This module provides a Python interface to the GoEdge Storage C SDK using ctypes.
It assumes that a pre-compiled shared library (e.g., 'libge-storage.so' on Linux)
is located in the same directory as this file.

You must compile the C SDK into a shared library and place it here.
For example, on Linux:
gcc -shared -fPIC -o libge-storage.so <source_files>.c -I<include_dirs> -luv
"""

import os
import sys
import ctypes
import ctypes.util

# --- Library Loading ---

def find_ge_storage_library():
    """
    Finds the 'libge-storage.so' shared library in a specific order of locations.
    Search Order:
    1. Directories listed in the LD_LIBRARY_PATH environment variable.
    2. Standard system library paths (using ctypes.util.find_library).
    3. The same directory as this script.
    """
    lib_full_name = 'libge-storage.so'
    lib_short_name = 'ge-storage'  # For find_library

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
    # two levels up from this file (src/goedge/ge_storage.py)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    lib_path = os.path.join(project_root, lib_full_name)
    if os.path.exists(lib_path):
        return lib_path

    return None

_lib_path = find_ge_storage_library()

if _lib_path is None:
    print("Error: Could not find the C shared library 'libge-storage.so'.")
    print("Search order:")
    print("  1. Directories in LD_LIBRARY_PATH")
    print("  2. Standard system library paths")
    print("  3. The script's own directory ({})".format(os.path.dirname(__file__)))
    print("Please ensure 'libge-storage.so' is available in one of these locations.")
    sys.exit(1)

try:
    _lib = ctypes.CDLL(_lib_path)
except OSError as e:
    print("Error: Found library at '{}', but failed to load it.".format(_lib_path))
    print("Original error: {}".format(e))
    sys.exit(1)


# --- Constants and Enums (from ge_storage.h) ---

# Storage Response Types
STORAGE_RESP_TP_SELECT = 0
STORAGE_RESP_TP_LIST = 1
STORAGE_RESP_TP_MAX = 2

# Storage Types
STORAGE_TYPE_INT64 = 0
STORAGE_TYPE_REAL = 1
STORAGE_TYPE_STR = 2
STORAGE_TYPE_MAX = 3


# --- Structures (from ge_storage.h) ---

class StorageValue(ctypes.Union):
    """
    Corresponds to the storage_value union in C.
    """
    _fields_ = [
        ('intger', ctypes.c_int64),
        ('real', ctypes.c_double),
        ('str', ctypes.c_char_p),
    ]

class StoragePoint(ctypes.Structure):
    """
    Corresponds to the storage_point struct in C.
    """
    _fields_ = [
        ('ts', ctypes.c_uint64),
        ('value', StorageValue),
    ]
    
    def get_value(self, storage_type):
        """Safely get the value based on storage type"""
        if storage_type == 0:  # STORAGE_TYPE_INT64
            return self.value.intger
        elif storage_type == 1:  # STORAGE_TYPE_REAL
            return self.value.real
        elif storage_type == 2:  # STORAGE_TYPE_STR
            return self.value.str
        else:
            return None

class StorageArrayPoint(ctypes.Structure):
    """
    Corresponds to the storage_array_point struct in C.
    """
    _fields_ = [
        ('n', ctypes.c_int),
        # Note: Flexible array member 'points[]' is not included in _fields_
        # It starts immediately after the struct in memory
    ]
    
    def get_point(self, index):
        """Safely get a point by index"""
        if index < 0 or index >= self.n:
            return None
        # The flexible array starts right after the 'n' field, but we must account for padding.
        # The array will be aligned to the alignment of its element type (StoragePoint).
        offset = type(self).n.offset + type(self).n.size
        align = ctypes.alignment(StoragePoint)
        padding = (align - (offset % align)) % align
        array_address = ctypes.addressof(self) + offset + padding
        element_ptr = ctypes.cast(array_address, ctypes.POINTER(StoragePoint))
        return element_ptr[index]

class StorageData(ctypes.Structure):
    """
    Corresponds to the storage_data struct in C.
    """
    _fields_ = [
        ('type', ctypes.c_int),  # storage_type_e
        ('name', ctypes.c_char_p),
        ('array_point', ctypes.POINTER(StorageArrayPoint)),
    ]
    
    def get_array_point(self):
        """Safely get the array_point"""
        if not self.array_point:
            return None
        return self.array_point.contents

class StorageArrayData(ctypes.Structure):
    """
    Corresponds to the storage_array_data struct in C.
    """
    _fields_ = [
        ('n', ctypes.c_int),
        # Note: Flexible array member 'data[]' is not included in _fields_
        # It starts immediately after the struct in memory
    ]
    
    def get_data(self, index):
        """Safely get a data item by index"""
        if index < 0 or index >= self.n:
            return None
        # The flexible array starts right after the 'n' field, but we must account for padding.
        # The array will be aligned to the alignment of its element type (StorageData).
        offset = type(self).n.offset + type(self).n.size
        align = ctypes.alignment(StorageData)
        padding = (align - (offset % align)) % align
        array_address = ctypes.addressof(self) + offset + padding
        element_ptr = ctypes.cast(array_address, ctypes.POINTER(StorageData))
        return element_ptr[index]

class StorageSeries(ctypes.Structure):
    """
    Corresponds to the storage_series struct in C.
    """
    _fields_ = [
        ('name', ctypes.c_char_p),
    ]

class StorageArraySeries(ctypes.Structure):
    """
    Corresponds to the storage_array_series struct in C.
    """
    _fields_ = [
        ('n', ctypes.c_int),
        # Note: Flexible array member 'series[]' is not included in _fields_
        # It starts immediately after the struct in memory
    ]
    
    def get_series(self, index):
        """Safely get a series by index"""
        if index < 0 or index >= self.n:
            return None
        # The flexible array starts right after the 'n' field, but we must account for padding.
        # The array will be aligned to the alignment of its element type (StorageSeries).
        offset = type(self).n.offset + type(self).n.size
        align = ctypes.alignment(StorageSeries)
        padding = (align - (offset % align)) % align
        array_address = ctypes.addressof(self) + offset + padding
        element_ptr = ctypes.cast(array_address, ctypes.POINTER(StorageSeries))
        return element_ptr[index]

class StorageReqData(ctypes.Structure):
    """
    Corresponds to the storage_req_data struct in C.
    """
    _fields_ = [
        ('public_data', ctypes.c_void_p),  # save query_data_t
        ('result', ctypes.c_int),
        ('array_data', ctypes.POINTER(StorageArrayData)),
        ('array_series', ctypes.POINTER(StorageArraySeries)),
        ('count', ctypes.c_uint64),
        ('tp', ctypes.c_int),  # storage_resp_tp_e
    ]

class QueryData(ctypes.Structure):
    """
    Corresponds to the query_data struct in C.
    """
    _fields_ = [
        ('user_data', ctypes.c_void_p),  # user data
        ('query', ctypes.c_char_p),
        ('req_data', StorageReqData),
        ('cb', ctypes.c_void_p),  # query_req_cb - function pointer
        ('sync_call', ctypes.c_void_p),  # uv_sem_t - this is an opaque type
    ]

class InsertReqData(ctypes.Structure):
    """
    Corresponds to the insert_req_data struct in C.
    """
    _fields_ = [
        ('public_data', ctypes.c_void_p),  # save insert_data_t
        ('result', ctypes.c_int),
        ('tp', ctypes.c_int),  # storage_resp_tp_e
    ]

class InsertData(ctypes.Structure):
    """
    Corresponds to the insert_data struct in C.
    """
    _fields_ = [
        ('user_data', ctypes.c_void_p),  # user data
        ('req_data', InsertReqData),
        ('name', ctypes.c_char_p),
        ('num', ctypes.c_int),
        ('series', ctypes.POINTER(ctypes.c_void_p)),  # siridb_series_t *[MAX_INSERT_NUM]
        ('cb', ctypes.c_void_p),  # insert_req_cb - function pointer
        ('sync_call', ctypes.c_void_p),  # uv_sem_t - this is an opaque type
    ]


# --- Callback Function Types ---

# Define callback types
QUERY_REQ_CB = ctypes.CFUNCTYPE(None, ctypes.POINTER(StorageReqData))
INSERT_REQ_CB = ctypes.CFUNCTYPE(None, ctypes.POINTER(InsertReqData))


# --- C Function Prototypes ---

# Query functions
_lib.ge_storage_create_query.argtypes = [ctypes.c_char_p, ctypes.c_void_p, QUERY_REQ_CB]
_lib.ge_storage_create_query.restype = ctypes.POINTER(QueryData)

_lib.ge_storage_query.argtypes = [ctypes.POINTER(QueryData)]
_lib.ge_storage_query.restype = ctypes.c_int

_lib.ge_storage_create_query_sync.argtypes = [ctypes.c_char_p]
_lib.ge_storage_create_query_sync.restype = ctypes.POINTER(QueryData)

_lib.ge_storage_query_sync.argtypes = [ctypes.POINTER(QueryData)]
_lib.ge_storage_query_sync.restype = ctypes.c_int

_lib.ge_storage_destroy_query.argtypes = [ctypes.POINTER(QueryData)]
_lib.ge_storage_destroy_query.restype = None

# Insert functions
_lib.ge_storage_create_insert.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(StoragePoint), ctypes.c_void_p, INSERT_REQ_CB]
_lib.ge_storage_create_insert.restype = ctypes.POINTER(InsertData)

_lib.ge_storage_insert.argtypes = [ctypes.POINTER(InsertData)]
_lib.ge_storage_insert.restype = ctypes.c_int

_lib.ge_storage_create_insert_sync.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(StoragePoint)]
_lib.ge_storage_create_insert_sync.restype = ctypes.POINTER(InsertData)

_lib.ge_storage_insert_sync.argtypes = [ctypes.POINTER(InsertData)]
_lib.ge_storage_insert_sync.restype = ctypes.c_int

_lib.ge_storage_destroy_insert.argtypes = [ctypes.POINTER(InsertData)]
_lib.ge_storage_destroy_insert.restype = None


# --- Python Wrapper Functions ---

# Create a default no-op callback
DEFAULT_QUERY_CALLBACK = QUERY_REQ_CB(lambda req_data_ptr: None)

# Store references to callbacks to prevent garbage collection
_callback_refs = {}

def create_query(query, user_data=None, callback=None):
    """Creates a query object for asynchronous querying."""
    if callback:
        cb = QUERY_REQ_CB(callback)
        # Store reference to prevent garbage collection
        _callback_refs[id(cb)] = cb
        result = _lib.ge_storage_create_query(query.encode('utf-8'), user_data, cb)
    else:
        # Use a default no-op callback to prevent segmentation fault
        result = _lib.ge_storage_create_query(query.encode('utf-8'), user_data, DEFAULT_QUERY_CALLBACK)
    return result

def execute_query(query_data):
    """Executes an asynchronous query."""
    return _lib.ge_storage_query(query_data)

def create_query_sync(query):
    """Creates a query object for synchronous querying."""
    return _lib.ge_storage_create_query_sync(query.encode('utf-8'))

def execute_query_sync(query_data):
    """Executes a synchronous query."""
    return _lib.ge_storage_query_sync(query_data)

def destroy_query(query_data):
    """Destroys a query object."""
    _lib.ge_storage_destroy_query(query_data)

# Create a default no-op callback
DEFAULT_INSERT_CALLBACK = INSERT_REQ_CB(lambda req_data_ptr: None)

def create_insert(name, storage_type, storage_point, user_data=None, callback=None):
    """Creates an insert object for asynchronous insertion."""
    point = StoragePoint()
    point.ts = storage_point['ts']
    
    if storage_type == STORAGE_TYPE_STR:
        point.value.str = storage_point['value'].encode('utf-8')
    elif storage_type == STORAGE_TYPE_REAL:
        point.value.real = storage_point['value']
    else:  # STORAGE_TYPE_INT64
        point.value.intger = storage_point['value']
    
    if callback:
        cb = INSERT_REQ_CB(callback)
        # Store reference to prevent garbage collection
        _callback_refs[id(cb)] = cb
        result = _lib.ge_storage_create_insert(name.encode('utf-8'), storage_type, ctypes.byref(point), user_data, cb)
    else:
        # Use a default no-op callback to prevent segmentation fault
        result = _lib.ge_storage_create_insert(name.encode('utf-8'), storage_type, ctypes.byref(point), user_data, DEFAULT_INSERT_CALLBACK)
    return result

def execute_insert(insert_data):
    """Executes an asynchronous insert."""
    return _lib.ge_storage_insert(insert_data)

def create_insert_sync(name, storage_type, storage_point):
    """Creates an insert object for synchronous insertion."""
    point = StoragePoint()
    point.ts = storage_point['ts']
    
    if storage_type == STORAGE_TYPE_STR:
        point.value.str = storage_point['value'].encode('utf-8')
    elif storage_type == STORAGE_TYPE_REAL:
        point.value.real = storage_point['value']
    else:  # STORAGE_TYPE_INT64
        point.value.intger = storage_point['value']
    
    return _lib.ge_storage_create_insert_sync(name.encode('utf-8'), storage_type, ctypes.byref(point))

def execute_insert_sync(insert_data):
    """Executes a synchronous insert."""
    return _lib.ge_storage_insert_sync(insert_data)

def destroy_insert(insert_data):
    """Destroys an insert object."""
    _lib.ge_storage_destroy_insert(insert_data)


# --- Optimized API Functions ---

def query_storage(query, user_data=None):
    """
    A simplified API that combines create, execute, and destroy operations for querying.
    
    Args:
        query (str): The query string to execute.
        user_data (optional): User data to pass to the query.
        
    Returns:
        tuple: A tuple containing (result_code, query_data_pointer).
               result_code: The result of the query execution.
               query_data_pointer: Pointer to the query data (mainly for debugging).
    """
    # Create query
    query_data = create_query_sync(query)
    if not query_data:
        return -1, None  # Failed to create query
    
    # Execute query
    result = execute_query_sync(query_data)
    
    # Destroy query
    destroy_query(query_data)
    
    return result, query_data


def insert_storage(name, storage_type, storage_point, user_data=None):
    """
    A simplified API that combines create, execute, and destroy operations for inserting.
    
    Args:
        name (str): The name of the series to insert data into.
        storage_type (int): The type of data to insert (STORAGE_TYPE_INT64, STORAGE_TYPE_REAL, or STORAGE_TYPE_STR).
        storage_point (dict): A dictionary with 'ts' and 'value' keys.
        user_data (optional): User data to pass to the insert operation.
        
    Returns:
        int: The result of the insert execution.
    """
    # Create insert
    insert_data = create_insert_sync(name, storage_type, storage_point)
    if not insert_data:
        return -1  # Failed to create insert
    
    # Execute insert
    result = execute_insert_sync(insert_data)
    
    # Destroy insert
    destroy_insert(insert_data)
    
    return result


# --- Simplified Asynchronous API Functions ---

def query_storage_async(query, callback=None, user_data=None):
    """
    A simplified API for asynchronous querying that creates a query with a callback.
    
    Args:
        query (str): The query string to execute.
        callback (function): Callback function to be called when the query completes.
        user_data (optional): User data to pass to the query.
        
    Returns:
        Pointer to query data, or None if failed to create query.
    """
    
    # Create query with callback
    query_data = create_query(query, user_data, callback)
    if not query_data:
        return None  # Failed to create query
    
    # Execute query
    result = execute_query(query_data)

    # Destroy query
    destroy_query(query_data)

    return result  # Return the result


def insert_storage_async(name, storage_type, storage_point, callback, user_data=None):
    """
    A simplified API for asynchronous inserting that combines create and execute operations.
    
    Args:
        name (str): The name of the series to insert data into.
        storage_type (int): The type of data to insert (STORAGE_TYPE_INT64, STORAGE_TYPE_REAL, or STORAGE_TYPE_STR).
        storage_point (dict): A dictionary with 'ts' and 'value' keys.
        callback (function): Callback function to be called when the insert completes.
        user_data (optional): User data to pass to the insert operation.
        
    Returns:
        int: Result code from the execute operation, or -1 if failed to create insert.
    """
    # Create insert with callback
    insert_data = create_insert(name, storage_type, storage_point, user_data, callback)
    if not insert_data:
        return -1  # Failed to create insert
    
    print(f"   create_insert")

    # Execute insert
    result = execute_insert(insert_data)

    # Destroy insert
    destroy_insert(insert_data)
    
    return result