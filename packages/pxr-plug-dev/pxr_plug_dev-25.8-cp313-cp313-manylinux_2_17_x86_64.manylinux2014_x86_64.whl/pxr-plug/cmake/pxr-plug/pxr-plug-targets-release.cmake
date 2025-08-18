#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyPlug" for configuration "Release"
set_property(TARGET pxr::pyPlug APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyPlug PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-plug/lib/python/pxr/Plug/_plug.so"
  IMPORTED_SONAME_RELEASE "_plug.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyPlug )
list(APPEND _cmake_import_check_files_for_pxr::pyPlug "${_IMPORT_PREFIX}/pxr-plug/lib/python/pxr/Plug/_plug.so" )

# Import target "pxr::plug" for configuration "Release"
set_property(TARGET pxr::plug APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::plug PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-plug/lib/libPxrPlug.so"
  IMPORTED_SONAME_RELEASE "libPxrPlug.so"
  )

list(APPEND _cmake_import_check_targets pxr::plug )
list(APPEND _cmake_import_check_files_for_pxr::plug "${_IMPORT_PREFIX}/pxr-plug/lib/libPxrPlug.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
