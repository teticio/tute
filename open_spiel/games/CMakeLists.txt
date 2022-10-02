add_library(tute OBJECT
  tute.h
  tute.cc
)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../..)
add_executable(tute_test tute_test.cc $<TARGET_OBJECTS:tute>)
add_dependencies(tute_test open_spiel)
target_link_libraries(tute_test PUBLIC open_spiel)
add_test(tute_test tute_test)
