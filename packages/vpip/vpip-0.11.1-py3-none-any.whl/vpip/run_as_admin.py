# pylint: disable=invalid-name, attribute-defined-outside-init

from contextlib import contextmanager
import ctypes
from ctypes import wintypes

class RunError(OSError):
    pass

# Define SHELLEXECUTEINFO structure
class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", wintypes.ULONG),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", wintypes.INT),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", wintypes.LPVOID),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIcon", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE), # This is where the process handle would be returned
    ]

# Constants for fMask
SEE_MASK_NOCLOSEPROCESS = 0x00000040 # To get a process handle back

# ShellExecuteExW function
ShellExecuteExW = ctypes.windll.shell32.ShellExecuteExW
ShellExecuteExW.argtypes = [ctypes.POINTER(SHELLEXECUTEINFO)]
ShellExecuteExW.restype = wintypes.BOOL

def escape_double_quote(s: str) -> str:
    """Escape double quotes in a string for Windows command line."""
    return s.replace('"', '""')

def win_join_params(params: list[str]) -> str:
    """Join parameters for Windows command line."""
    return " ".join([f'"{escape_double_quote(p)}"' if " " in p or '"' in p else p for p in params])

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

@contextmanager
def run_as_admin_shellexecuteex(file_path, params: str | list[str] = "", working_dir="", show_cmd=1):
    if not isinstance(params, str):
        params = win_join_params(params)
    sei = SHELLEXECUTEINFO()
    sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
    sei.fMask = SEE_MASK_NOCLOSEPROCESS # Request a process handle
    sei.hwnd = 0 # No parent window
    sei.lpVerb = "runas" # The key to elevate privileges
    sei.lpFile = file_path
    sei.lpParameters = params
    sei.lpDirectory = working_dir
    sei.nShow = show_cmd

    if not ShellExecuteExW(ctypes.byref(sei)):
        error_code = ctypes.get_last_error()
        raise RunError(f"ShellExecuteEx failed. Error code: {error_code}")

    # Note: sei.hProcess will be a valid handle ONLY if SEE_MASK_NOCLOSEPROCESS is used.
    # You can then use this handle with kernel32.WaitForSingleObject, etc.
    try:
        yield sei.hProcess
    finally:
        wait_handle_close(sei.hProcess)

def wait_handle_close(handle):
    """Wait for a handle to close."""
    kernel32 = ctypes.WinDLL('kernel32')
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    INFINITE = 0xFFFFFFFF
    result = kernel32.WaitForSingleObject(handle, INFINITE)
    if result == 0:  # WAIT_OBJECT_0
        kernel32.CloseHandle(handle)
