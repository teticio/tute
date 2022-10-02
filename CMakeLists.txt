cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(tute)

# Set default build type.
set(BUILD_TYPE $ENV{BUILD_TYPE})

if(NOT BUILD_TYPE)
  set(BUILD_TYPE Release)
endif()

message("Current build type is: ${BUILD_TYPE}")

include(ExternalProject)

# Download, build and add OpenSpiel
ExternalProject_Add(open_spiel
  GIT_REPOSITORY https://github.com/deepmind/open_spiel.git
  GIT_TAG master
  SOURCE_DIR ${CMAKE_BINARY_DIR}/open_spiel
  PATCH_COMMAND
  OPEN_SPIEL_BUILD_WITH_LIBTORCH=ON
  OPEN_SPIEL_BUILD_WITH_LIBTORCH_DOWNLOAD_URL=https://download.pytorch.org/libtorch/cu116/libtorch-cxx11-abi-shared-with-deps-1.12.1%2Bcu116.zip
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
ExternalProject_Get_Property(open_spiel SOURCE_DIR BINARY_DIR)

# Add this project as an external project to ensure dependencies have been built.
ExternalProject_Add(tute
  DEPENDS open_spiel
  SOURCE_DIR ${CMAKE_SOURCE_DIR}/open_spiel
  CONFIGURE_COMMAND
  BUILD_TYPE=${BUILD_TYPE}
  ${CMAKE_COMMAND}
  -DCMAKE_CXX_COMPILER=clang++
  -DCMAKE_CXX_STANDARD=17
  -DOPEN_SPIEL_BINARY_DIR=${BINARY_DIR}
  -DOPEN_SPIEL_SOURCE_DIR=${SOURCE_DIR}
  -DTorch_DIR=${SOURCE_DIR}/open_spiel/libtorch/libtorch/share/cmake/Torch
  <SOURCE_DIR>
  INSTALL_COMMAND ""
)
