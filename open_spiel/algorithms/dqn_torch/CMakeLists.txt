# To enable C++ Torch DQN, you will need to set OPEN_SPIEL_BUILD_WITH_LIBTORCH.
if(OPEN_SPIEL_BUILD_WITH_LIBTORCH)
  add_library(_dqn_torch OBJECT
    dqn.h
    dqn.cc
    simple_nets.h
    simple_nets.cc
  )
  target_include_directories(_dqn_torch PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

  add_executable(_dqn_torch_test dqn_torch_test.cc
    $<TARGET_OBJECTS:_dqn_torch> $<TARGET_OBJECTS:tests>)
  add_dependencies(_dqn_torch_test open_spiel)
  add_test(_dqn_torch_test _dqn_torch_test)

  target_link_libraries(_dqn_torch ${TORCH_LIBRARIES})
  target_link_libraries(_dqn_torch_test PUBLIC open_spiel ${TORCH_LIBRARIES})
endif()
