#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "segyutils::segyutils" for configuration "Release"
set_property(TARGET segyutils::segyutils APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(segyutils::segyutils PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/segyutils.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/segyutils.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS segyutils::segyutils )
list(APPEND _IMPORT_CHECK_FILES_FOR_segyutils::segyutils "${_IMPORT_PREFIX}/lib/segyutils.lib" "${_IMPORT_PREFIX}/bin/segyutils.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
