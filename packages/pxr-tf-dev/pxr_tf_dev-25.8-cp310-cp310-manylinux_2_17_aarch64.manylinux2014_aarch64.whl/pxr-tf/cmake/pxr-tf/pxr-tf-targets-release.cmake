#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyTf" for configuration "Release"
set_property(TARGET pxr::pyTf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyTf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-tf/lib/python/pxr/Tf/_tf.so"
  IMPORTED_SONAME_RELEASE "_tf.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyTf )
list(APPEND _cmake_import_check_files_for_pxr::pyTf "${_IMPORT_PREFIX}/pxr-tf/lib/python/pxr/Tf/_tf.so" )

# Import target "pxr::tf" for configuration "Release"
set_property(TARGET pxr::tf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::tf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-tf/lib/libPxrTf.so"
  IMPORTED_SONAME_RELEASE "libPxrTf.so"
  )

list(APPEND _cmake_import_check_targets pxr::tf )
list(APPEND _cmake_import_check_files_for_pxr::tf "${_IMPORT_PREFIX}/pxr-tf/lib/libPxrTf.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
