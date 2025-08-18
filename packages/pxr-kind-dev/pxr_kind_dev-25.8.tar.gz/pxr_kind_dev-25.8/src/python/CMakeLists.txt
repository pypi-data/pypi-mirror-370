add_library(pyKind SHARED
    module.cpp
    wrapRegistry.cpp
    wrapTokens.cpp
)

set_target_properties(pyKind
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _kind
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Kind"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Kind"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Kind"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyKind
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyKind
    PUBLIC
        kind
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyKind
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyKind PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyKind PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyKind
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Kind
        MFB_PACKAGE_NAME=kind
        MFB_ALT_PACKAGE_NAME=kind
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyKind>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyKind EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Kind
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Kind
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Kind
)
