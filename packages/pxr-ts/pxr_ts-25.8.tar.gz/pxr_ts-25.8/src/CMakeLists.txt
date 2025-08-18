configure_file(
    pxr/ts/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/ts/pxr.h
    @ONLY
)

add_library(ts
    pxr/ts/binary.cpp
    pxr/ts/debugCodes.cpp
    pxr/ts/eval.cpp
    pxr/ts/knot.cpp
    pxr/ts/knotData.cpp
    pxr/ts/knotMap.cpp
    pxr/ts/raii.cpp
    pxr/ts/regressionPreventer.cpp
    pxr/ts/sample.cpp
    pxr/ts/spline.cpp
    pxr/ts/splineData.cpp
    pxr/ts/tangentConversions.cpp
    pxr/ts/typeHelpers.cpp
    pxr/ts/types.cpp
)

target_include_directories(ts
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(ts
    PUBLIC
        pxr::arch
        pxr::tf
        pxr::vt
        pxr::gf
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(ts
        PRIVATE
            pxr/ts/moduleDeps.cpp
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(ts
        PRIVATE
            pxr/ts/pch.h
    )
endif()

set_target_properties(ts
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrTs"
)

target_compile_definitions(ts
    PRIVATE
        TS_EXPORTS=1
        MFB_PACKAGE_MODULE=Ts
        MFB_PACKAGE_NAME=ts
        MFB_ALT_PACKAGE_NAME=ts
)

target_sources(ts
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/ts/pxr.h
            pxr/ts/api.h
            pxr/ts/binary.h
            pxr/ts/debugCodes.h
            pxr/ts/eval.h
            pxr/ts/knot.h
            pxr/ts/knotData.h
            pxr/ts/knotMap.h
            pxr/ts/raii.h
            pxr/ts/regressionPreventer.h
            pxr/ts/spline.h
            pxr/ts/splineData.h
            pxr/ts/tangentConversions.h
            pxr/ts/typeHelpers.h
            pxr/ts/types.h
            pxr/ts/valueTypeDispatch.h
)

install(
    TARGETS ts EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-ts-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-ts
)
