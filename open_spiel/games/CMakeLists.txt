add_library(tute OBJECT
  tute.h
  tute.cc
)
add_executable(tute_test tute_test.cc $<TARGET_OBJECTS:tute>)
target_link_libraries(tute_test PUBLIC ${OPEN_SPIEL_LIB})
add_test(tute_test tute_test)
