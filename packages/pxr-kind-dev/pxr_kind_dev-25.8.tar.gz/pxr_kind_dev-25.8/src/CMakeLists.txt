configure_file(
    pxr/kind/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/kind/pxr.h
    @ONLY
)
add_library(kind
    pxr/kind/registry.cpp
)

target_include_directories(kind
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(kind
    PUBLIC
        pxr::tf
        pxr::plug
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(kind
        PRIVATE
            pxr/kind/moduleDeps.cpp
    )

    target_link_libraries(kind
        PUBLIC
            pxr::boost-python
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(kind
        PRIVATE
            pxr/kind/pch.h
    )
endif()

set_target_properties(kind
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrKind"
)

target_compile_definitions(kind
    PRIVATE
        KIND_EXPORTS=1
        MFB_PACKAGE_MODULE=Kind
        MFB_PACKAGE_NAME=kind
        MFB_ALT_PACKAGE_NAME=kind
)

target_sources(kind
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/kind/pxr.h
            pxr/kind/api.h
            pxr/kind/registry.h
)

install(
    TARGETS kind EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    FILES
        pxr/kind/api.h
        pxr/kind/registry.h
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/kind
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-kind-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-kind
)
