import ctypes
import os
from ctypes import wintypes
from ctypes.wintypes import DWORD, HANDLE

# Import necessary Windows APIs from pywin32
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Constants
PROCESS_ALL_ACCESS = 0x001F0FFF
MEM_COMMIT_RESERVE = 0x1000 | 0x2000
PAGE_READWRITE = 0x04


# Define necessary structures
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ProcessID", DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(DWORD)),
        ("th32ModuleID", DWORD),
        ("cntThreads", DWORD),
        ("th32ParentProcessID", DWORD),
        ("pcPriClassBase", DWORD),
        ("dwFlags", DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]  # MAX_PATH


def get_process_id_by_name(exe_name: str) -> int:
    h_snapshot = kernel32.CreateToolhelp32Snapshot(2, 0)  # TH32CS_SNAPPROCESS
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if kernel32.Process32First(h_snapshot, ctypes.byref(entry)):
        while True:
            if entry.szExeFile.decode("utf-8") == exe_name:
                pid = entry.th32ProcessID
                kernel32.CloseHandle(h_snapshot)
                return pid
            if not kernel32.Process32Next(h_snapshot, ctypes.byref(entry)):
                break
    kernel32.CloseHandle(h_snapshot)
    return 0


def OLD_inject_dll(process_name: str, dll_path: str) -> bool:
    if not os.path.exists(dll_path):
        print(f"Error: DLL path '{dll_path}' does not exist.")
        return False

    pid = get_process_id_by_name(process_name)
    if pid == 0:
        print(f"Error: Process '{process_name}' not found.")
        return False

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        print("Error: Could not open target process.")
        return False

        ###
    kernel32.VirtualAllocEx.restype = ctypes.c_void_p
    kernel32.VirtualAllocEx.argtypes = [
        HANDLE,
        ctypes.c_void_p,
        ctypes.c_size_t,
        DWORD,
        DWORD,
    ]

    kernel32.WriteProcessMemory.argtypes = [
        HANDLE,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(DWORD),
    ]
    ###

    dll_path_encoded = dll_path.encode("utf-8")
    dll_size = len(dll_path_encoded) + 1  # Plus null terminator
    arg_address = kernel32.VirtualAllocEx(
        h_process, None, dll_size, MEM_COMMIT_RESERVE, PAGE_READWRITE
    )
    print(f"Allocated memory at: {hex(arg_address)}")

    if not arg_address:
        print("Error: Could not allocate memory in target process.")
        kernel32.CloseHandle(h_process)
        return False

    bytes_written = DWORD(0)
    if not kernel32.WriteProcessMemory(
        h_process, arg_address, dll_path_encoded, dll_size, ctypes.byref(bytes_written)
    ):
        print("Error: Could not write to process memory.")
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
        kernel32.CloseHandle(h_process)
        return False

    # Get the address of LoadLibraryA
    load_library_address = ctypes.windll.kernel32.GetProcAddress(
        ctypes.windll.kernel32.GetModuleHandleA("kernel32.dll"), b"LoadLibraryA"
    )

    kernel32.CreateRemoteThread.argtypes = [
        HANDLE,  # hProcess
        ctypes.c_void_p,  # lpThreadAttributes
        ctypes.c_size_t,  # dwStackSize
        ctypes.c_void_p,  # lpStartAddress (pointer to the function)
        ctypes.c_void_p,  # lpParameter
        DWORD,  # dwCreationFlags
        ctypes.POINTER(DWORD),  # lpThreadId
    ]
    kernel32.CreateRemoteThread.restype = HANDLE

    h_thread = kernel32.CreateRemoteThread(
        # h_process, None, 0, kernel32.LoadLibraryA, arg_address, 0, None
        h_process,
        None,
        0,
        load_library_address,
        arg_address,
        0,
        None,
    )
    if not h_thread:
        print("Error: Could not create remote thread.")
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
        kernel32.CloseHandle(h_process)
        return False

    # kernel32.WaitForSingleObject(h_thread, 0xFFFFFFFF)  # Wait indefinitely
    # kernel32.CloseHandle(h_thread)
    # kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
    # kernel32.CloseHandle(h_process)

    print(f"Injected DLL: {dll_path} into process: {process_name} (PID: {pid}).")

    return True


def inject_dll(process_name: str, dll_path: str) -> bool:
    pid = get_process_id_by_name(process_name)
    if pid == 0:
        print(f"Error: Process '{process_name}' not found.")
        return False

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        print("Error: Could not open target process.")
        return False

    dll_path_encoded = dll_path.encode("utf-8") + b"\x00"
    arg_address = kernel32.VirtualAllocEx(
        h_process, None, len(dll_path_encoded), MEM_COMMIT_RESERVE, PAGE_READWRITE
    )

    if not arg_address:
        print("Error: Could not allocate memory in target process.")
        kernel32.CloseHandle(h_process)
        return False

    bytes_written = wintypes.DWORD(0)
    if not kernel32.WriteProcessMemory(
        h_process,
        arg_address,
        dll_path_encoded,
        len(dll_path_encoded),
        ctypes.byref(bytes_written),
    ):
        print("Error: Could not write to process memory.")
        kernel32.CloseHandle(h_process)
        return False

    # Simplified approach: Assume LoadLibraryA is available at the same address across processes.
    load_library_address = kernel32.LoadLibraryA
    h_thread = kernel32.CreateRemoteThread(
        h_process, None, 0, load_library_address, arg_address, 0, None
    )

    if not h_thread:
        print("Error: Could not create remote thread.")
        kernel32.CloseHandle(h_process)
        return False

    print(f"Injected DLL: {dll_path} into process: {process_name}.")
    return True
