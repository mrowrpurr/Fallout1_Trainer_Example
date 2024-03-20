import ctypes
import ctypes.wintypes as wintypes
from typing import Optional

# Load necessary DLLs
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)

# Define necessary types and prototypes
PROCESS_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * wintypes.MAX_PATH),
    ]


def get_process_id(process_name: str) -> Optional[int]:
    print(f"Getting process ID for: {process_name}...")
    h_snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
    if h_snapshot == ctypes.c_void_p(-1).value:
        return None

    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if kernel32.Process32First(h_snapshot, ctypes.byref(entry)):
        while True:
            if process_name.encode("utf-8") == entry.szExeFile:
                kernel32.CloseHandle(h_snapshot)
                return entry.th32ProcessID
            if not kernel32.Process32Next(h_snapshot, ctypes.byref(entry)):
                break
    kernel32.CloseHandle(h_snapshot)
    return None


def inject_dll(process_name: str, dll_path: str) -> bool:
    print("Injecting DLL...")
    pid = get_process_id(process_name)
    print(f"PID: {pid}")
    if pid is None:
        return False

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        return False

    dll_path_bytes = dll_path.encode("utf-8")
    arg_address = kernel32.VirtualAllocEx(
        h_process, None, len(dll_path_bytes), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE
    )
    if not arg_address:
        return False

    written = ctypes.c_size_t(0)
    if not kernel32.WriteProcessMemory(
        h_process,
        arg_address,
        dll_path_bytes,
        len(dll_path_bytes),
        ctypes.byref(written),
    ):
        return False

    h_thread_id = kernel32.CreateRemoteThread(
        h_process,
        None,
        0,
        kernel32.LoadLibraryA,
        arg_address,
        0,
        0,
    )

    if h_thread_id:
        ctypes.windll.kernel32.WaitForSingleObject(
            h_thread_id, ctypes.wintypes.DWORD(0xFFFFFFFF)
        )  # INFINITE
        kernel32.CloseHandle(h_thread_id)
    else:
        return False

    kernel32.CloseHandle(h_process)  # Close the process handle here
    return True
