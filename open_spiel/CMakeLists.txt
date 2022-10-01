cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(tute_game)
enable_testing()

set (BUILD_TYPE $ENV{BUILD_TYPE})
if(${BUILD_TYPE} STREQUAL "Debug")
  # Basic build for debugging (default).
  # -Og enables optimizations that do not interfere with debugging.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Og")
endif()

set(OPEN_SPIEL_LIB ${OPEN_SPIEL_BINARY_DIR}/libopen_spiel.so)
set(DQN_DIR ${OPEN_SPIEL_BINARY_DIR}/algorithms/dqn_torch/CMakeFiles/dqn_torch.dir)
set(DQN_OBJS ${DQN_DIR}/dqn.cc.o ${DQN_DIR}/simple_nets.cc.o)
set(TORCH_DIR ${OPEN_SPIEL_SOURCE_DIR}/open_spiel/libtorch/libtorch)

include_directories(${OPEN_SPIEL_SOURCE_DIR}
  ${OPEN_SPIEL_SOURCE_DIR}/open_spiel/abseil-cpp
  ${TORCH_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/..)

# Tute
add_subdirectory(games)

list(APPEND CMAKE_PREFIX_PATH ${TORCH_DIR})
find_package(Torch REQUIRED)

add_executable(tute_game tute_game.cc)
target_link_libraries(tute_game ${TORCH_LIBRARIES} ${OPEN_SPIEL_LIB} ${DQN_OBJS})
