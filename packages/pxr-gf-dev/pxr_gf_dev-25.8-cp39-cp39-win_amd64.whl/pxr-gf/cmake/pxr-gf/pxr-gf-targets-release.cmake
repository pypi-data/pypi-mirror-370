#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyGf" for configuration "Release"
set_property(TARGET pxr::pyGf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyGf PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-gf/lib/python/pxr/Gf/_gf.pyd"
  )

list(APPEND _cmake_import_check_targets pxr::pyGf )
list(APPEND _cmake_import_check_files_for_pxr::pyGf "${_IMPORT_PREFIX}/pxr-gf/lib/python/pxr/Gf/_gf.pyd" )

# Import target "pxr::gf" for configuration "Release"
set_property(TARGET pxr::gf APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::gf PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/pxr-gf/lib/PxrGf.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-gf/lib/PxrGf.dll"
  )

list(APPEND _cmake_import_check_targets pxr::gf )
list(APPEND _cmake_import_check_files_for_pxr::gf "${_IMPORT_PREFIX}/pxr-gf/lib/PxrGf.lib" "${_IMPORT_PREFIX}/pxr-gf/lib/PxrGf.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
