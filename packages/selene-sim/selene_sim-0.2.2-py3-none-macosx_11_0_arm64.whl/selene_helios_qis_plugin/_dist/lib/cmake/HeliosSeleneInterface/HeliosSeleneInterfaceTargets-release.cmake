#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "HeliosSeleneInterface::helios_selene_interface" for configuration "Release"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HeliosSeleneInterface::helios_selene_interface PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libhelios_selene_interface.a"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface "${_IMPORT_PREFIX}/lib/libhelios_selene_interface.a" )

# Import target "HeliosSeleneInterface::helios_selene_interface_debug" for configuration "Release"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface_debug APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HeliosSeleneInterface::helios_selene_interface_debug PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libhelios_selene_interface_debug.a"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface_debug )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface_debug "${_IMPORT_PREFIX}/lib/libhelios_selene_interface_debug.a" )

# Import target "HeliosSeleneInterface::helios_selene_interface_diagnostic" for configuration "Release"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface_diagnostic APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HeliosSeleneInterface::helios_selene_interface_diagnostic PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libhelios_selene_interface_diagnostic.a"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface_diagnostic )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface_diagnostic "${_IMPORT_PREFIX}/lib/libhelios_selene_interface_diagnostic.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
