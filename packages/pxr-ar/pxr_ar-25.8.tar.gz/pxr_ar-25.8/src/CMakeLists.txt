configure_file(
    pxr/ar/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/ar/pxr.h
    @ONLY
)

add_library(ar
    pxr/ar/asset.cpp
    pxr/ar/assetInfo.cpp
    pxr/ar/debugCodes.cpp
    pxr/ar/defaultResolver.cpp
    pxr/ar/defaultResolverContext.cpp
    pxr/ar/definePackageResolver.cpp
    pxr/ar/defineResolver.cpp
    pxr/ar/filesystemAsset.cpp
    pxr/ar/filesystemWritableAsset.cpp
    pxr/ar/inMemoryAsset.cpp
    pxr/ar/notice.cpp
    pxr/ar/packageResolver.cpp
    pxr/ar/packageUtils.cpp
    pxr/ar/resolver.cpp
    pxr/ar/resolverContext.cpp
    pxr/ar/resolverContextBinder.cpp
    pxr/ar/resolverScopedCache.cpp
    pxr/ar/timestamp.cpp
    pxr/ar/writableAsset.cpp
)

target_include_directories(ar
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(ar
    PUBLIC
        pxr::arch
        pxr::tf
        pxr::js
        pxr::plug
        pxr::vt
        TBB::tbb
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(ar
        PRIVATE
            pxr/ar/moduleDeps.cpp
    )

    target_link_libraries(ar
        PUBLIC
            pxr::boost-python
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(ar
        PRIVATE
            pxr/ar/pch.h
    )
endif()

set_target_properties(ar
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrAr"
)

target_compile_definitions(ar
    PRIVATE
        AR_EXPORTS=1
        MFB_PACKAGE_MODULE=Ar
        MFB_PACKAGE_NAME=ar
        MFB_ALT_PACKAGE_NAME=ar
)

if(SKBUILD)
    set(_lib_prefix "../../.libs/")
    set(_build_dir "../pluginfo/ar/resources")
else()
    set(_lib_prefix "../../")
    set(_build_dir "usd/ar/resources")
endif()

set(PLUG_INFO_LIBRARY_PATH "${_lib_prefix}$<TARGET_FILE_NAME:ar>")
configure_file(pxr/ar/plugInfo.json plugInfo.json @ONLY)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:ar>/usd/ar/resources/plugInfo_$<CONFIG>.json"
    INPUT "${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json"
)

install(
    FILES "$<TARGET_FILE_DIR:ar>/usd/ar/resources/plugInfo_$<CONFIG>.json"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/${_build_dir}"
    RENAME plugInfo.json
)

target_sources(ar
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/ar/pxr.h
            pxr/ar/api.h
            pxr/ar/ar.h
            pxr/ar/asset.h
            pxr/ar/assetInfo.h
            pxr/ar/defaultResolver.h
            pxr/ar/defaultResolverContext.h
            pxr/ar/definePackageResolver.h
            pxr/ar/defineResolver.h
            pxr/ar/defineResolverContext.h
            pxr/ar/filesystemAsset.h
            pxr/ar/filesystemWritableAsset.h
            pxr/ar/inMemoryAsset.h
            pxr/ar/notice.h
            pxr/ar/packageResolver.h
            pxr/ar/packageUtils.h
            pxr/ar/resolvedPath.h
            pxr/ar/resolver.h
            pxr/ar/resolverContext.h
            pxr/ar/resolverContextBinder.h
            pxr/ar/resolverScopedCache.h
            pxr/ar/threadLocalScopedCache.h
            pxr/ar/timestamp.h
            pxr/ar/writableAsset.h
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(ar
        PUBLIC
            FILE_SET public_headers
            TYPE HEADERS
            BASE_DIRS
                ${CMAKE_CURRENT_SOURCE_DIR}
            FILES
                pxr/ar/pyResolverContext.h
    )
endif()

install(
    TARGETS ar EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-ar-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-ar
)
