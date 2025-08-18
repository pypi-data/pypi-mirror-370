#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyVt" for configuration "Release"
set_property(TARGET pxr::pyVt APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyVt PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-vt/lib/python/pxr/Vt/_vt.pyd"
  )

list(APPEND _cmake_import_check_targets pxr::pyVt )
list(APPEND _cmake_import_check_files_for_pxr::pyVt "${_IMPORT_PREFIX}/pxr-vt/lib/python/pxr/Vt/_vt.pyd" )

# Import target "pxr::vt" for configuration "Release"
set_property(TARGET pxr::vt APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::vt PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/pxr-vt/lib/PxrVt.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-vt/lib/PxrVt.dll"
  )

list(APPEND _cmake_import_check_targets pxr::vt )
list(APPEND _cmake_import_check_files_for_pxr::vt "${_IMPORT_PREFIX}/pxr-vt/lib/PxrVt.lib" "${_IMPORT_PREFIX}/pxr-vt/lib/PxrVt.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
