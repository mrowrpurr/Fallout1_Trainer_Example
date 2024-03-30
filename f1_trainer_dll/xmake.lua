add_repositories("MrowrLib https://github.com/MrowrLib/Packages.git")
add_requires("dll_injector", "spdlog", "_Log_")

target("test_dll_injection")
    set_kind("binary")
    add_files("test_dll_injection.cpp")
    add_packages("dll_injector")

target("f1_trainer")
    set_kind("shared")
    add_files("f1_trainer.cpp")
    add_packages("spdlog", "_Log_")
    add_links("User32")
