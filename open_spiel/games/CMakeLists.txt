add_library(tute OBJECT
  tute.h
  tute.cc
)

target_include_directories(tute PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(tute_test tute_test.cc $<TARGET_OBJECTS:tute>)
add_dependencies(tute_test open_spiel)
add_test(tute_test tute_test)

target_link_libraries(tute_test PUBLIC open_spiel)
