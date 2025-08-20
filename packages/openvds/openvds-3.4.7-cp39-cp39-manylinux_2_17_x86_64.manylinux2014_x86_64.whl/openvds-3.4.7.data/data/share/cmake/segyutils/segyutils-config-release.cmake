#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "segyutils::segyutils" for configuration "Release"
set_property(TARGET segyutils::segyutils APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(segyutils::segyutils PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libsegyutils.so.3.4.7"
  IMPORTED_SONAME_RELEASE "libsegyutils.so.3"
  )

list(APPEND _cmake_import_check_targets segyutils::segyutils )
list(APPEND _cmake_import_check_files_for_segyutils::segyutils "${_IMPORT_PREFIX}/lib64/libsegyutils.so.3.4.7" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
