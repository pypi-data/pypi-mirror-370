# Config file for the multio package
# Defines the following variables:
#
#  multio_FEATURES       - list of enabled features
#  multio_VERSION        - version of the package
#  multio_GIT_SHA1       - Git revision of the package
#  multio_GIT_SHA1_SHORT - short Git revision of the package
#


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was project-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

### computed paths
set_and_check(multio_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib/cmake/multio")
set_and_check(multio_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MULTIO_CMAKE_DIR ${multio_CMAKE_DIR})
  set(MULTIO_BASE_DIR ${multio_BASE_DIR})
endif()

### export version info
set(multio_VERSION           "2.6.1")
set(multio_GIT_SHA1          "581b63c4415ca6e9664400c509d4c7b1ad888bb7")
set(multio_GIT_SHA1_SHORT    "581b63c")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MULTIO_VERSION           "2.6.1" )
  set(MULTIO_GIT_SHA1          "581b63c4415ca6e9664400c509d4c7b1ad888bb7" )
  set(MULTIO_GIT_SHA1_SHORT    "581b63c" )
endif()

### has this configuration been exported from a build tree?
set(multio_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MULTIO_IS_BUILD_DIR_EXPORT ${multio_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${multio_CMAKE_DIR}/multio-import.cmake)
  set(multio_IMPORT_FILE "${multio_CMAKE_DIR}/multio-import.cmake")
  include(${multio_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT multio_BINARY_DIR)
  find_file(multio_TARGETS_FILE
    NAMES multio-targets.cmake
    HINTS ${multio_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(multio_TARGETS_FILE)
    include(${multio_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${multio_CMAKE_DIR}/multio-post-import.cmake)
  set(multio_POST_IMPORT_FILE "${multio_CMAKE_DIR}/multio-post-import.cmake")
  include(${multio_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MULTIO_LIBRARIES         "")
  set(MULTIO_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(multio_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(multio_IMPORT_FILE)
  set(MULTIO_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(MULTIO_IMPORT_FILE)
endif()

### export features and check requirements
set(multio_FEATURES "TESTS;PKGCONFIG;FDB5;ECKIT_CODEC;MIR;FORTRAN;BUILD_TOOLS;MULTIO_BUILD_TOOLS;GRIB1_TO_GRIB2;MULTIO_OUTPUT_MANAGER;WARNINGS;WARNINGS")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(MULTIO_FEATURES ${multio_FEATURES})
endif()
foreach(_f ${multio_FEATURES})
  set(multio_${_f}_FOUND 1)
  set(multio_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(MULTIO_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(multio)
