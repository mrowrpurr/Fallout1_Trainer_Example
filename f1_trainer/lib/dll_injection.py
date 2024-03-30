import ctypes
from ctypes import wintypes

# Load Windows DLLs
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Constants
PROCESS_ALL_ACCESS = 0x001F0FFF
MEM_COMMIT_RESERVE = 0x1000 | 0x2000
PAGE_READWRITE = 0x04


# Define the PROCESSENTRY32 structure
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


def get_process_id_by_name(target_process_name):
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if kernel32.Process32First(snapshot, ctypes.byref(entry)):
        while True:
            process_name = entry.szExeFile.decode()
            if process_name.lower() == target_process_name.lower():
                pid = entry.th32ProcessID
                kernel32.CloseHandle(snapshot)
                return pid
            if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                break
    kernel32.CloseHandle(snapshot)
    return None


def inject_dll(target_process_name, dll_path):
    pid = get_process_id_by_name(target_process_name)
    if pid is None:
        print("Target process not found.")
        return False

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        print("Failed to open target process.")
        return False

    dll_path_bytes = (dll_path + "\0").encode("utf-8")
    arg_address = kernel32.VirtualAllocEx(
        h_process, None, len(dll_path_bytes), MEM_COMMIT_RESERVE, PAGE_READWRITE
    )

    if not arg_address:
        print("Memory allocation failed.")
        kernel32.CloseHandle(h_process)
        return False

    written = ctypes.c_size_t(0)
    result = kernel32.WriteProcessMemory(
        h_process,
        arg_address,
        dll_path_bytes,
        len(dll_path_bytes),
        ctypes.byref(written),
    )
    if not result:
        error_code = kernel32.GetLastError()
        print(
            f"Failed to write DLL path to target process memory. Last Error: {error_code}"
        )
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
        kernel32.CloseHandle(h_process)
        return False

    if not result:
        print("Failed to write DLL path to target process memory.")
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
        kernel32.CloseHandle(h_process)
        return False

    thread_id = wintypes.DWORD()
    h_thread = kernel32.CreateRemoteThread(
        h_process,
        None,
        0,
        kernel32.LoadLibraryA,
        arg_address,
        0,
        ctypes.byref(thread_id),
    )

    if not h_thread:
        print("Failed to create remote thread.")
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
        kernel32.CloseHandle(h_process)
        return False

    kernel32.WaitForSingleObject(h_thread, wintypes.INFINITE)
    kernel32.CloseHandle(h_thread)
    kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # MEM_RELEASE
    kernel32.CloseHandle(h_process)
    print(f"Successfully injected {dll_path} into {target_process_name} (PID: {pid}).")
    return True


# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python inject.py <process_name> <dll_path>")
#         sys.exit(1)
#     target_process_name = sys.argv[1]
#     dll_path = sys.argv[2]
#     inject_dll(target_process_name, dll_path)
