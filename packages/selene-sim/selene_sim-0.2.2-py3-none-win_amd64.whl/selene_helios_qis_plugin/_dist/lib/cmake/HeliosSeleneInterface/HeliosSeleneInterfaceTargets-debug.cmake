#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "HeliosSeleneInterface::helios_selene_interface" for configuration "Debug"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(HeliosSeleneInterface::helios_selene_interface PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "C"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/helios_selene_interface.lib"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface "${_IMPORT_PREFIX}/lib/helios_selene_interface.lib" )

# Import target "HeliosSeleneInterface::helios_selene_interface_debug" for configuration "Debug"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface_debug APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(HeliosSeleneInterface::helios_selene_interface_debug PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "C"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/helios_selene_interface_debug.lib"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface_debug )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface_debug "${_IMPORT_PREFIX}/lib/helios_selene_interface_debug.lib" )

# Import target "HeliosSeleneInterface::helios_selene_interface_diagnostic" for configuration "Debug"
set_property(TARGET HeliosSeleneInterface::helios_selene_interface_diagnostic APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(HeliosSeleneInterface::helios_selene_interface_diagnostic PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "C"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/helios_selene_interface_diagnostic.lib"
  )

list(APPEND _cmake_import_check_targets HeliosSeleneInterface::helios_selene_interface_diagnostic )
list(APPEND _cmake_import_check_files_for_HeliosSeleneInterface::helios_selene_interface_diagnostic "${_IMPORT_PREFIX}/lib/helios_selene_interface_diagnostic.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
