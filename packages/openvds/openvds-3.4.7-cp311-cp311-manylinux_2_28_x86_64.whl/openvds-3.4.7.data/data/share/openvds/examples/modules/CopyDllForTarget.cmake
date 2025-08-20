function(copyDllForTarget target)
    if (WIN32 OR APPLE)
      get_target_property(is_imported openvds::openvds IMPORTED)
      if (is_imported)
        get_target_property(openvds_location_debug openvds::openvds IMPORTED_LOCATION_DEBUG)
        get_target_property(openvds_location_relwithdebinfo openvds::openvds IMPORTED_LOCATION_RELWITHDEBINFO)
        get_target_property(openvds_location_release openvds::openvds IMPORTED_LOCATION_RELEASE)

        if (openvds_location_relwithdebinfo)
          set(optimized_location_file ${openvds_location_relwithdebinfo})
        elseif(openvds_location_release)
          set(optimized_location_file ${openvds_location_release})
        endif()

        if (optimized_location_file)
            get_filename_component(optimized_location ${optimized_location_file} DIRECTORY)
        endif()
        get_filename_component(debug_location ${openvds_location_debug} DIRECTORY)

        file(GLOB runtime_release "${optimized_location}/*.dll")
        file(GLOB runtime_debug "${debug_location}/*.dll")
        add_custom_command(TARGET ${target}
          POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<$<NOT:$<CONFIG:Debug>>:${runtime_release}>" "$<$<CONFIG:Debug>:${runtime_debug}>" "$<SHELL_PATH:$<TARGET_FILE_DIR:${target}>>"
          COMMAND_EXPAND_LISTS
          )
      else()
        get_property(runtime_libs GLOBAL PROPERTY OPENVDS_RUNTIME_LIBS)

	list(APPEND runtime_libs "$<TARGET_FILE:openvds>")
	list(APPEND runtime_libs "$<TARGET_FILE:segyutils>")

        add_custom_command(TARGET ${target}
          POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_if_different "${runtime_libs}" "$<SHELL_PATH:$<TARGET_FILE_DIR:${target}>>"
          COMMAND_EXPAND_LISTS
          )
      endif()
    endif()
endfunction()
