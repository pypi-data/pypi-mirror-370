add_library(pyAr SHARED
    module.cpp
    wrapAsset.cpp
    wrapAssetInfo.cpp
    wrapDefaultResolverContext.cpp
    wrapDefaultResolver.cpp
    wrapNotice.cpp
    wrapPackageUtils.cpp
    wrapResolvedPath.cpp
    wrapResolverContextBinder.cpp
    wrapResolverContext.cpp
    wrapResolverScopedCache.cpp
    wrapResolver.cpp
    wrapTimestamp.cpp
)

set_target_properties(pyAr
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _ar
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ar"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ar"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Ar"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyAr
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyAr
    PUBLIC
        ar
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyAr
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyAr PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyAr PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyAr
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Ar
        MFB_PACKAGE_NAME=ar
        MFB_ALT_PACKAGE_NAME=ar
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyAr>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyAr EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ar
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ar
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Ar
)
