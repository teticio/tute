cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(dqn_torch_test)
enable_testing()

# Set default build type.
set (BUILD_TYPE $ENV{BUILD_TYPE})
if(NOT BUILD_TYPE)
   set(BUILD_TYPE Release)
endif()
message("${BoldYellow}Current build type is: ${BUILD_TYPE}${ColourReset}")

if(${BUILD_TYPE} STREQUAL "Debug")
  # Basic build for debugging (default).
  # -Og enables optimizations that do not interfere with debugging.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Og")
endif()

# download, build and add OpenSpiel
include(ExternalProject)
ExternalProject_Add(open_spiel_lib
  GIT_REPOSITORY https://github.com/deepmind/open_spiel.git
  GIT_TAG master
  SOURCE_DIR ${CMAKE_BINARY_DIR}/open_spiel
  PATCH_COMMAND
  OPEN_SPIEL_BUILD_WITH_LIBTORCH=ON
  OPEN_SPIEL_BUILD_WITH_LIBNOP=ON
  ./install.sh
  CONFIGURE_COMMAND
  BUILD_TYPE=${BUILD_TYPE}
  BUILD_SHARED_LIB=ON
  OPEN_SPIEL_BUILD_WITH_LIBTORCH=ON
  OPEN_SPIEL_ENABLE_PYTORCH=ON
  OPEN_SPIEL_BUILD_WITH_LIBNOP=ON
  ${CMAKE_COMMAND}
  -DCMAKE_CXX_COMPILER=clang++
  <SOURCE_DIR>/open_spiel
  BUILD_COMMAND make -j$(nproc) open_spiel dqn_torch
  INSTALL_COMMAND ""
)
ExternalProject_Get_Property(open_spiel_lib SOURCE_DIR BINARY_DIR)

# Add this project as an external project to ensure dependencies have been built.
include(ExternalProject)
ExternalProject_Add(tute
  DEPENDS open_spiel_lib
  SOURCE_DIR ${CMAKE_SOURCE_DIR}/open_spiel
  CONFIGURE_COMMAND
  BUILD_TYPE=${BUILD_TYPE}
  OPEN_SPIEL_LIB=${OPEN_SPIEL_LIB}
  DQN_DIR=${DQN_DIR}
  TORCH_DIR=${TORCH_DIR}
  ${CMAKE_COMMAND}
  -DCMAKE_CXX_COMPILER=clang++
  -DCMAKE_CXX_STANDARD=17
  -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  -DOPEN_SPIEL_BINARY_DIR=${BINARY_DIR}
  -DOPEN_SPIEL_SOURCE_DIR=${SOURCE_DIR}
  <SOURCE_DIR>
  INSTALL_COMMAND ""
)
