#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pxr::pyTrace" for configuration "Release"
set_property(TARGET pxr::pyTrace APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::pyTrace PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-trace/lib/python/pxr/Trace/_trace.so"
  IMPORTED_SONAME_RELEASE "@rpath/_trace.so"
  )

list(APPEND _cmake_import_check_targets pxr::pyTrace )
list(APPEND _cmake_import_check_files_for_pxr::pyTrace "${_IMPORT_PREFIX}/pxr-trace/lib/python/pxr/Trace/_trace.so" )

# Import target "pxr::trace" for configuration "Release"
set_property(TARGET pxr::trace APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(pxr::trace PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/pxr-trace/lib/libPxrTrace.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libPxrTrace.dylib"
  )

list(APPEND _cmake_import_check_targets pxr::trace )
list(APPEND _cmake_import_check_files_for_pxr::trace "${_IMPORT_PREFIX}/pxr-trace/lib/libPxrTrace.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
