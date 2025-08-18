cmake_minimum_required(VERSION 3.23...4.1)

# Default build type value.
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the build type")

project(pxr-pegtl
    VERSION 0.25.8
    HOMEPAGE_URL "https://github.com/untwine/pxr-pegtl"
    LANGUAGES C CXX
)

if (NOT "${CMAKE_CXX_STANDARD}")
    set(CMAKE_CXX_STANDARD 17 CACHE STRING "Default C++ standard")
endif()

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(GNUInstallDirs)

add_subdirectory(src)

include(CMakePackageConfigHelpers)

configure_package_config_file(
    "cmake/pxr-pegtl-config.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/pxr-pegtl-config.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-pegtl
)

write_basic_package_version_file(
    "pxr-pegtl-config-version.cmake"
    COMPATIBILITY AnyNewerVersion
)

install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/pxr-pegtl-config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/pxr-pegtl-config-version.cmake"
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-pegtl
)
