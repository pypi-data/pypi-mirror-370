#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "openvds::openvds" for configuration "Release"
set_property(TARGET openvds::openvds APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(openvds::openvds PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libopenvds.so.3.4.7"
  IMPORTED_SONAME_RELEASE "libopenvds.so.3"
  )

list(APPEND _cmake_import_check_targets openvds::openvds )
list(APPEND _cmake_import_check_files_for_openvds::openvds "${_IMPORT_PREFIX}/lib64/libopenvds.so.3.4.7" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
