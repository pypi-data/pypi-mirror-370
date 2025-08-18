add_library(pyTs SHARED
    module.cpp
    wrapKnot.cpp
    wrapKnotMap.cpp
    wrapRaii.cpp
    wrapRegressionPreventer.cpp
    wrapSpline.cpp
    wrapTangentConversions.cpp
    wrapTypes.cpp
)

set_target_properties(pyTs
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _ts
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ts"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ts"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ts"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyTs
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyTs
    PUBLIC
        ts
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyTs
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyTs PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyTs PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyTs
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Ts
        MFB_PACKAGE_NAME=ts
        MFB_ALT_PACKAGE_NAME=ts
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyTs>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyTs EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ts
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ts
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ts
)
