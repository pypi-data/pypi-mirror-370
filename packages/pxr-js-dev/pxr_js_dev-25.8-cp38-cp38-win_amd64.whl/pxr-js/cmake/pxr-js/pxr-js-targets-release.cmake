#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::js" for configuration "Release"
set_property(TARGET pxr::js APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::js PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/pxr-js/lib/PxrJs.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-js/lib/PxrJs.dll"
  )

list(APPEND _cmake_import_check_targets pxr::js )
list(APPEND _cmake_import_check_files_for_pxr::js "${_IMPORT_PREFIX}/pxr-js/lib/PxrJs.lib" "${_IMPORT_PREFIX}/pxr-js/lib/PxrJs.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
