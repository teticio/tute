cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(tute_game)
enable_testing()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-everything")

set(BUILD_TYPE $ENV{BUILD_TYPE})
set(OPEN_SPIEL_BUILD_WITH_LIBTORCH $ENV{OPEN_SPIEL_BUILD_WITH_LIBTORCH})

if(${BUILD_TYPE} STREQUAL "Debug")
  # Basic build for debugging (default).
  # -Og enables optimizations that do not interfere with debugging.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Og")
endif()

# OpenSpiel
add_subdirectory(${OPEN_SPIEL_SOURCE_DIR}/open_spiel
  ${OPEN_SPIEL_BINARY_DIR} EXCLUDE_FROM_ALL)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/..
  ${OPEN_SPIEL_SOURCE_DIR}
  ${OPEN_SPIEL_SOURCE_DIR}/open_spiel/abseil-cpp)

# Torch
find_package(Torch REQUIRED)
include_directories(${TORCH_INCLUDE_DIRS})

# Tute
add_subdirectory(games)

# DQN
add_subdirectory(algorithms)

# Tute game
add_executable(tute_game tute_game.cc)
target_link_libraries(tute_game
  tute
  absl::flags # Have to link absl::flags and absl::flags_parse separately.
  absl::flags_parse
  _dqn_torch
  open_spiel
  ${TORCH_LIBRARIES})
