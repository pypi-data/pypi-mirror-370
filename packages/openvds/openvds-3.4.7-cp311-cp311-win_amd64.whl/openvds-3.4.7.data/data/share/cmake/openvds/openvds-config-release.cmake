#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "openvds::openvds" for configuration "Release"
set_property(TARGET openvds::openvds APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(openvds::openvds PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/openvds.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/openvds.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS openvds::openvds )
list(APPEND _IMPORT_CHECK_FILES_FOR_openvds::openvds "${_IMPORT_PREFIX}/lib/openvds.lib" "${_IMPORT_PREFIX}/bin/openvds.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
