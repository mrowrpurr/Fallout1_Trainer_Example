#include <_Log_.h>
#include <windows.h>

#include <format>
#include <thread>

_LogToFile_("C:/Temp/f1_trainer_dll.log");

volatile bool serverRunning = false;

void ServerThreadFunction() {
    _Log_("ServerThreadFunction");
    const std::wstring pipeName = L"\\\\.\\pipe\\ExamplePipe";
    HANDLE             pipe     = CreateNamedPipeW(
        pipeName.c_str(), PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        PIPE_UNLIMITED_INSTANCES, 1024, 1024, 0, NULL
    );

    if (pipe == INVALID_HANDLE_VALUE) {
        return;
    }

    serverRunning = true;
    while (serverRunning) {
        if (ConnectNamedPipe(pipe, NULL) || GetLastError() == ERROR_PIPE_CONNECTED) {
            char  buffer[1024] = {0};
            DWORD bytesRead;
            BOOL  result = ReadFile(pipe, buffer, sizeof(buffer), &bytesRead, NULL);

            if (result) {
                std::string receivedText(buffer, bytesRead);
                std::string responseText =
                    std::format("CHANGED! You sent us the text: '{}'", receivedText);

                DWORD bytesWritten;
                WriteFile(pipe, responseText.c_str(), responseText.length(), &bytesWritten, NULL);
            }
            DisconnectNamedPipe(pipe);
        }
    }
    _Log_("ServerThreadFunction end");
    CloseHandle(pipe);
}

std::thread serverThread;

extern "C" __declspec(dllexport) void StopServer() {
    _Log_("StopServer");
    serverRunning = false;
    if (serverThread.joinable()) {
        serverThread.join();
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            MessageBoxW(
                NULL, L"DLL_PROCESS_ATTACH called", L"Notification", MB_OK | MB_ICONINFORMATION
            );
            _Log_("DLL_PROCESS_ATTACH");
            serverThread = std::thread(ServerThreadFunction);
            break;
        case DLL_PROCESS_DETACH:
            _Log_("DLL_PROCESS_DETACH");
            StopServer();
            break;
    }
    return TRUE;
}
