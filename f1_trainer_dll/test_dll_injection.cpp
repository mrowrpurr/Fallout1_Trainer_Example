#include <dll_injector.h>

#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <processName> <dllPath>" << std::endl;
        return 1;
    }

    std::string processName = argv[1];
    std::string dllPath     = argv[2];

    if (!DLL_Injection::InjectDLL(processName, dllPath, true)) {
        std::cerr << "Failed to inject the DLL into the process." << std::endl;
        return 1;
    } else {
        std::cout << "Successfully injected the DLL into the process." << std::endl;
        return 0;
    }
}
