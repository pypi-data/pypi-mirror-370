#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pySdf" for configuration "Release"
set_property(TARGET pxr::pySdf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pySdf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-sdf/lib/python/pxr/Sdf/_sdf.so"
  IMPORTED_SONAME_RELEASE "_sdf.so"
  )

list(APPEND _cmake_import_check_targets pxr::pySdf )
list(APPEND _cmake_import_check_files_for_pxr::pySdf "${_IMPORT_PREFIX}/pxr-sdf/lib/python/pxr/Sdf/_sdf.so" )

# Import target "pxr::sdf" for configuration "Release"
set_property(TARGET pxr::sdf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::sdf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-sdf/lib/libPxrSdf.so"
  IMPORTED_SONAME_RELEASE "libPxrSdf.so"
  )

list(APPEND _cmake_import_check_targets pxr::sdf )
list(APPEND _cmake_import_check_files_for_pxr::sdf "${_IMPORT_PREFIX}/pxr-sdf/lib/libPxrSdf.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
