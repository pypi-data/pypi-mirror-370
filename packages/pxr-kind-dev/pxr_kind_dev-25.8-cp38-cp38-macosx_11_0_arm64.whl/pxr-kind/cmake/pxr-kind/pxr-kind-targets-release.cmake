#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyKind" for configuration "Release"
set_property(TARGET pxr::pyKind APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyKind PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-kind/lib/python/pxr/Kind/_kind.so"
  IMPORTED_SONAME_RELEASE "@rpath/_kind.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyKind )
list(APPEND _cmake_import_check_files_for_pxr::pyKind "${_IMPORT_PREFIX}/pxr-kind/lib/python/pxr/Kind/_kind.so" )

# Import target "pxr::kind" for configuration "Release"
set_property(TARGET pxr::kind APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::kind PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-kind/lib/libPxrKind.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libPxrKind.dylib"
  )

list(APPEND _cmake_import_check_targets pxr::kind )
list(APPEND _cmake_import_check_files_for_pxr::kind "${_IMPORT_PREFIX}/pxr-kind/lib/libPxrKind.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
