add_library(pyPlug SHARED
    module.cpp
    wrapNotice.cpp
    wrapPlugin.cpp
    wrapRegistry.cpp
)

set_target_properties(pyPlug
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _plug
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Plug"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Plug"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Plug"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyPlug
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyPlug
    PUBLIC
        plug
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyPlug
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyPlug PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyPlug PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyPlug
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Plug
        MFB_PACKAGE_NAME=plug
        MFB_ALT_PACKAGE_NAME=plug
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyPlug>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyPlug EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Plug
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Plug
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Plug
)
