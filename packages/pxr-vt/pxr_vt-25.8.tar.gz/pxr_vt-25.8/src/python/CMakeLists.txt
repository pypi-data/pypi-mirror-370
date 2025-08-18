add_library(pyVt SHARED
    module.cpp
    wrapArrayBase.cpp
    wrapArrayDualQuaternion.cpp
    wrapArrayFloat.cpp
    wrapArrayIntegral.cpp
    wrapArrayMatrix.cpp
    wrapArrayQuaternion.cpp
    wrapArrayRange.cpp
    wrapArrayString.cpp
    wrapArrayToken.cpp
    wrapArrayVec.cpp
    wrapDictionary.cpp
    wrapValue.cpp
)

set_target_properties(pyVt
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _vt
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Vt"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Vt"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Vt"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyVt
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyVt
    PUBLIC
        vt
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyVt
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyVt PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyVt PROPERTIES SUFFIX ".so")
endif()

if(MSVC)
    target_compile_options(pyVt PRIVATE /bigobj)
endif()

target_compile_definitions(
    pyVt
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Vt
        MFB_PACKAGE_NAME=vt
        MFB_ALT_PACKAGE_NAME=vt
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyVt>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyVt EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Vt
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Vt
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Vt
)
