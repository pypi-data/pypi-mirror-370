#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyAr" for configuration "Release"
set_property(TARGET pxr::pyAr APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyAr PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-ar/lib/python/pxr/Ar/_ar.pyd"
  )

list(APPEND _cmake_import_check_targets pxr::pyAr )
list(APPEND _cmake_import_check_files_for_pxr::pyAr "${_IMPORT_PREFIX}/pxr-ar/lib/python/pxr/Ar/_ar.pyd" )

# Import target "pxr::ar" for configuration "Release"
set_property(TARGET pxr::ar APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::ar PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/pxr-ar/lib/PxrAr.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-ar/lib/PxrAr.dll"
  )

list(APPEND _cmake_import_check_targets pxr::ar )
list(APPEND _cmake_import_check_files_for_pxr::ar "${_IMPORT_PREFIX}/pxr-ar/lib/PxrAr.lib" "${_IMPORT_PREFIX}/pxr-ar/lib/PxrAr.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
