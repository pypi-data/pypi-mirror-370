add_library(pyTf SHARED
    module.cpp
    pyWeakObject.cpp
    wrapAnyWeakPtr.cpp
    wrapCallContext.cpp
    wrapDebug.cpp
    wrapDiagnostic.cpp
    wrapDiagnosticBase.cpp
    wrapEnum.cpp
    wrapEnvSetting.cpp
    wrapError.cpp
    wrapException.cpp
    wrapFileUtils.cpp
    wrapFunction.cpp
    wrapMallocTag.cpp
    wrapNotice.cpp
    wrapPathUtils.cpp
    wrapPyContainerConversions.cpp
    wrapPyModuleNotice.cpp
    wrapPyObjWrapper.cpp
    wrapPyOptional.cpp
    wrapRefPtrTracker.cpp
    wrapScopeDescription.cpp
    wrapScriptModuleLoader.cpp
    wrapSingleton.cpp
    wrapStackTrace.cpp
    wrapStatus.cpp
    wrapStopwatch.cpp
    wrapStringUtils.cpp
    wrapTemplateString.cpp
    wrapTestPyAnnotatedBoolResult.cpp
    wrapTestPyContainerConversions.cpp
    wrapTestPyStaticTokens.cpp
    wrapTestTfPyOptional.cpp
    wrapTestTfPython.cpp
    wrapToken.cpp
    wrapType.cpp
    wrapWarning.cpp
)

set_target_properties(pyTf
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _tf
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Tf"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Tf"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Tf"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyTf
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyTf
    PUBLIC
        tf
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyTf
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyTf PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyTf PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyTf
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Tf
        MFB_PACKAGE_NAME=tf
        MFB_ALT_PACKAGE_NAME=tf
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyTf>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyTf EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Tf
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Tf
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Tf
)
