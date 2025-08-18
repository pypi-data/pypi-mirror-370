configure_file(
    pxr/trace/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/trace/pxr.h
    @ONLY
)

add_library(trace
    pxr/trace/aggregateTree.cpp
    pxr/trace/aggregateTreeBuilder.cpp
    pxr/trace/aggregateNode.cpp
    pxr/trace/category.cpp
    pxr/trace/collection.cpp
    pxr/trace/collectionNotice.cpp
    pxr/trace/collector.cpp
    pxr/trace/counterAccumulator.cpp
    pxr/trace/dataBuffer.cpp
    pxr/trace/dynamicKey.cpp
    pxr/trace/event.cpp
    pxr/trace/eventContainer.cpp
    pxr/trace/eventData.cpp
    pxr/trace/eventList.cpp
    pxr/trace/eventNode.cpp
    pxr/trace/eventTree.cpp
    pxr/trace/eventTreeBuilder.cpp
    pxr/trace/jsonSerialization.cpp
    pxr/trace/key.cpp
    pxr/trace/reporter.cpp
    pxr/trace/reporterBase.cpp
    pxr/trace/reporterDataSourceBase.cpp
    pxr/trace/reporterDataSourceCollection.cpp
    pxr/trace/reporterDataSourceCollector.cpp
    pxr/trace/serialization.cpp
    pxr/trace/staticKeyData.cpp
    pxr/trace/threads.cpp
)

target_include_directories(trace
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(trace
    PUBLIC
        pxr::arch
        pxr::js
        pxr::tf
        TBB::tbb
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(trace
        PRIVATE
            pxr/trace/moduleDeps.cpp
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(trace
        PRIVATE
            pxr/trace/pch.h
    )
endif()

set_target_properties(trace
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrTrace"
)

target_compile_definitions(trace
    PRIVATE
        TRACE_EXPORTS=1
        MFB_PACKAGE_MODULE=Trace
        MFB_PACKAGE_NAME=trace
        MFB_ALT_PACKAGE_NAME=trace
)

target_sources(trace
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/trace/pxr.h
            pxr/trace/aggregateTree.h
            pxr/trace/aggregateNode.h
            pxr/trace/api.h
            pxr/trace/category.h
            pxr/trace/collection.h
            pxr/trace/collectionNotice.h
            pxr/trace/collector.h
            pxr/trace/concurrentList.h
            pxr/trace/counterAccumulator.h
            pxr/trace/dataBuffer.h
            pxr/trace/dynamicKey.h
            pxr/trace/event.h
            pxr/trace/eventContainer.h
            pxr/trace/eventData.h
            pxr/trace/eventList.h
            pxr/trace/eventNode.h
            pxr/trace/eventTree.h
            pxr/trace/key.h
            pxr/trace/reporter.h
            pxr/trace/reporterBase.h
            pxr/trace/reporterDataSourceBase.h
            pxr/trace/reporterDataSourceCollection.h
            pxr/trace/reporterDataSourceCollector.h
            pxr/trace/serialization.h
            pxr/trace/staticKeyData.h
            pxr/trace/stringHash.h
            pxr/trace/threads.h
            pxr/trace/trace.h
)

install(
    TARGETS trace EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-trace-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-trace
)
