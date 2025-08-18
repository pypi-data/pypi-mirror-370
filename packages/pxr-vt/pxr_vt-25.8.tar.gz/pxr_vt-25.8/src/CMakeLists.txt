configure_file(
    pxr/vt/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/vt/pxr.h
    @ONLY
)

add_library(vt
    pxr/vt/array.cpp
    pxr/vt/arrayEdit.cpp
    pxr/vt/arrayEditBuilder.cpp
    pxr/vt/arrayEditOps.cpp
    pxr/vt/debugCodes.cpp
    pxr/vt/dictionary.cpp
    pxr/vt/hash.cpp
    pxr/vt/streamOut.cpp
    pxr/vt/types.cpp
    pxr/vt/value.cpp
)

target_include_directories(vt
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(vt
    PUBLIC
        pxr::arch
        pxr::tf
        pxr::gf
        pxr::trace
        TBB::tbb
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(vt
        PRIVATE
            pxr/vt/moduleDeps.cpp
            pxr/vt/arrayPyBuffer.cpp
            pxr/vt/valueFromPython.cpp
            pxr/vt/wrapArray.cpp
    )

    target_link_libraries(vt
        PUBLIC
            pxr::boost-python
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(vt
        PRIVATE
            pxr/vt/pch.h
    )
endif()

if(MSVC)
    target_compile_options(vt PRIVATE /bigobj)
endif()

set_target_properties(vt
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrVt"
)

target_compile_definitions(vt
    PRIVATE
        VT_EXPORTS=1
        MFB_PACKAGE_MODULE=Vt
        MFB_PACKAGE_NAME=vt
        MFB_ALT_PACKAGE_NAME=vt
)

target_sources(vt
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/vt/pxr.h
            pxr/vt/api.h
            pxr/vt/array.h
            pxr/vt/arrayEdit.h
            pxr/vt/arrayEditBuilder.h
            pxr/vt/arrayEditOps.h
            pxr/vt/debugCodes.h
            pxr/vt/dictionary.h
            pxr/vt/hash.h
            pxr/vt/streamOut.h
            pxr/vt/traits.h
            pxr/vt/typeHeaders.h
            pxr/vt/types.h
            pxr/vt/value.h
            pxr/vt/visitValue.h
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(vt
        PUBLIC
            FILE_SET public_headers
            TYPE HEADERS
            BASE_DIRS
                ${CMAKE_CURRENT_SOURCE_DIR}
            FILES
                pxr/vt/arrayPyBuffer.h
                pxr/vt/pyOperators.h
                pxr/vt/valueFromPython.h
                pxr/vt/wrapArray.h
                pxr/vt/wrapArrayEdit.h
    )
endif()

install(
    TARGETS vt EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-vt-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-vt
)
