function (openvds_target_compile_options target scope)
  target_compile_options(${target} ${scope}
    "$<$<COMPILE_LANGUAGE:CUDA>:SHELL:-Xcompiler \"${ARGN}\">"
    "$<$<COMPILE_LANGUAGE:CXX>:${ARGN}>")
endfunction()

function(setCompilerFlagsForTarget target)
  if (MSVC)
    if (MSVC_VERSION GREATER_EQUAL 1910 AND NOT OpenMP_CXX_FOUND)
      openvds_target_compile_options(${target} PRIVATE /permissive-)
    endif()
#    if(MSVC_VERSION GREATER_EQUAL 1915)
#      openvds_target_compile_options(${target} PRIVATE $<$<NOT:$<CONFIG:Release>>:/JMC>)
#    endif()
  else()
    set_target_properties(${target} PROPERTIES LINK_FLAGS_RELEASE -s)
  endif()
  
  if (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    openvds_target_compile_options(${target} PRIVATE /MP)
  else()
    openvds_target_compile_options(${target} PRIVATE -Werror=return-type)
  endif()

  if(ENABLE_ASAN)
    if(MSVC)
      openvds_target_compile_options(${target} PUBLIC /fsanitize=address)
    else()
      openvds_target_compile_options(${target} PUBLIC -fsanitize=address)
      target_link_options(${target} PUBLIC -fsanitize=address)
    endif()
  endif()

  if (NOT MSVC AND NOT APPLE AND NOT EMSCRIPTEN)
    target_link_options(${target} PUBLIC -Wl,--exclude-libs=ALL)
    target_link_options(${target} PUBLIC -Wl,--no-export-dynamic)
  endif()

endfunction()
