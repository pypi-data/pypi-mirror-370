#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyWork" for configuration "Release"
set_property(TARGET pxr::pyWork APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyWork PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-work/lib/python/pxr/Work/_work.so"
  IMPORTED_SONAME_RELEASE "_work.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyWork )
list(APPEND _cmake_import_check_files_for_pxr::pyWork "${_IMPORT_PREFIX}/pxr-work/lib/python/pxr/Work/_work.so" )

# Import target "pxr::work" for configuration "Release"
set_property(TARGET pxr::work APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::work PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-work/lib/libPxrWork.so"
  IMPORTED_SONAME_RELEASE "libPxrWork.so"
  )

list(APPEND _cmake_import_check_targets pxr::work )
list(APPEND _cmake_import_check_files_for_pxr::work "${_IMPORT_PREFIX}/pxr-work/lib/libPxrWork.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
