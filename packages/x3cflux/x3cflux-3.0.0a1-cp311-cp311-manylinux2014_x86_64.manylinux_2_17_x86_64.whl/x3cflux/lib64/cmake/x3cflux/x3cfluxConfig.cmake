
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was x3cfluxConfig.cmake.in                            ########

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

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PACKAGE_PREFIX_DIR}/lib64/cmake/x3cflux)

include(CMakeFindDependencyMacro)
find_dependency(Boost 1.65 COMPONENTS log date_time)
find_dependency(Eigen3 3.3)
find_package(SUNDIALS 6.6 REQUIRED)

if(NOT TARGET x3cflux::x3cflux)
    include("${CMAKE_CURRENT_LIST_DIR}/x3cfluxTargets.cmake")
endif()

check_required_components(x3cflux)
