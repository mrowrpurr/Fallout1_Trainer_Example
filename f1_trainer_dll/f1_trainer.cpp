#include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH: {
            // Close the currently running process:
            // using the latest C++ for doing it:
            exit(0);

            // auto* file = fopen("C:\\temp\\dll_log.txt", "a+");
            // if (file) {
            //     fprintf(file, "DLL has been loaded!\n");
            //     fclose(file);
            // }
            // MessageBox(NULL, TEXT("DLL has been loaded!"), TEXT("Notification"), MB_OK);
            break;
        }
        default:
            break;
    }
    return TRUE;
}