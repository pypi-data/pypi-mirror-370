add_library(pegtl INTERFACE)

target_include_directories(pegtl
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# Collect all public headers under pxr/ (re-glob on file changes)
file(GLOB_RECURSE PEGTL_PUBLIC_HEADERS 
    CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/pxr/*.hpp")

target_sources(pegtl
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
        FILES
            ${PEGTL_PUBLIC_HEADERS}
)

install(
    TARGETS pegtl EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-pegtl-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-pegtl
)
