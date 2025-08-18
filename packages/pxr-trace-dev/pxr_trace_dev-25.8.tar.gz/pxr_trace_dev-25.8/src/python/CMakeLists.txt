add_library(pyTrace SHARED
    module.cpp
    wrapAggregateNode.cpp
    wrapAggregateTree.cpp
    wrapCollector.cpp
    wrapReporter.cpp
    wrapTestTrace.cpp
)

set_target_properties(pyTrace
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _trace
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Trace"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Trace"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Trace"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyTrace
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyTrace
    PUBLIC
        trace
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyTrace
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyTrace PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyTrace PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyTrace
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Trace
        MFB_PACKAGE_NAME=trace
        MFB_ALT_PACKAGE_NAME=trace
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyTrace>/__init__.py"
    INPUT "__init__.py"
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyTrace>/__main__.py"
    INPUT "__main__.py"
)

install(
    TARGETS pyTrace EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Trace
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Trace
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Trace
)
install(
    FILES __main__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Trace
)
