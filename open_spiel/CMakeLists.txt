cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(tute_game)
enable_testing()

set(BUILD_TYPE $ENV{BUILD_TYPE})

if(${BUILD_TYPE} STREQUAL "Debug")
  # Basic build for debugging (default).
  # -Og enables optimizations that do not interfere with debugging.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Og")
endif()

# OpenSpiel
set(OPEN_SPIEL_LIB ${OPEN_SPIEL_BINARY_DIR}/libopen_spiel.so)
set(DQN_DIR ${OPEN_SPIEL_BINARY_DIR}/algorithms/dqn_torch/CMakeFiles/dqn_torch.dir)
set(DQN_OBJS ${DQN_DIR}/dqn.cc.o ${DQN_DIR}/simple_nets.cc.o)
set(ABSEIL_SOURCE_DIR ${OPEN_SPIEL_SOURCE_DIR}/open_spiel/abseil-cpp)
set(ABSEIL_BINARY_DIR ${OPEN_SPIEL_BINARY_DIR}/abseil-cpp)
add_subdirectory(${ABSEIL_SOURCE_DIR} ${ABSEIL_BINARY_DIR})
include_directories(${OPEN_SPIEL_SOURCE_DIR} ${ABSEIL_SOURCE_DIR})

# Torch
find_package(Torch REQUIRED)
include_directories(${TORCH_INCLUDE_DIRS})

# Tute
add_subdirectory(games)

# Tute game
add_executable(tute_game tute_game.cc)
target_link_libraries(tute_game
  tute
  absl::flags # Have to link absl::flags and absl::flags_parse separately.
  absl::flags_parse
  ${DQN_OBJS}
  ${OPEN_SPIEL_LIB}
  ${TORCH_LIBRARIES})
