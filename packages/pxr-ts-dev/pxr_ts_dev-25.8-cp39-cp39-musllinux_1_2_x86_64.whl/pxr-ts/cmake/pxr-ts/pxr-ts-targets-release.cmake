#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyTs" for configuration "Release"
set_property(TARGET pxr::pyTs APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyTs PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-ts/lib/python/pxr/Ts/_ts.so"
  IMPORTED_SONAME_RELEASE "_ts.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyTs )
list(APPEND _cmake_import_check_files_for_pxr::pyTs "${_IMPORT_PREFIX}/pxr-ts/lib/python/pxr/Ts/_ts.so" )

# Import target "pxr::ts" for configuration "Release"
set_property(TARGET pxr::ts APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::ts PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-ts/lib/libPxrTs.so"
  IMPORTED_SONAME_RELEASE "libPxrTs.so"
  )

list(APPEND _cmake_import_check_targets pxr::ts )
list(APPEND _cmake_import_check_files_for_pxr::ts "${_IMPORT_PREFIX}/pxr-ts/lib/libPxrTs.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
