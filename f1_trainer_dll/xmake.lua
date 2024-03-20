add_repositories("MrowrLib https://github.com/MrowrLib/Packages.git")
add_requires("dll_injection", "spdlog", "_Log_")

target("f1_trainer")
    set_kind("shared")
    add_files("f1_trainer.cpp")

target("inject_dll")
    set_kind("binary")
    add_files("inject.cpp")
    add_packages("dll_injection", "spdlog", "_Log_")
    add_includedirs(".")
