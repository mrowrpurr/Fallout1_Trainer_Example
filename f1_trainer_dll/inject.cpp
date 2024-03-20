#include <_Log_.h>

#include <dll_injection>
#include <iostream>


int main() {
    auto dllPath =
        "C:/Code/mrowrpurr/Fallout1_Trainer_Example/build/windows/x86/debug/f1_trainer.dll";
    if (DLL_Injection::InjectDLL("falloutwHR.exe", dllPath)) {
        std::cout << "DLL injected successfully" << std::endl;
    } else {
        std::cout << "DLL injection failed" << std::endl;
    }
}
