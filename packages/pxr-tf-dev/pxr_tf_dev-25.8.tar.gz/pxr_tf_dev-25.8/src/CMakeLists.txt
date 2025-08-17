configure_file(
    pxr/tf/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/tf/pxr.h
    @ONLY
)

add_library(tf
    pxr/tf/anyWeakPtr.cpp
    pxr/tf/atomicOfstreamWrapper.cpp
    pxr/tf/atomicRenameUtil.cpp
    pxr/tf/bigRWMutex.cpp
    pxr/tf/bits.cpp
    pxr/tf/compressedBits.cpp
    pxr/tf/debug.cpp
    pxr/tf/debugCodes.cpp
    pxr/tf/debugNotice.cpp
    pxr/tf/diagnostic.cpp
    pxr/tf/diagnosticBase.cpp
    pxr/tf/diagnosticHelper.cpp
    pxr/tf/diagnosticMgr.cpp
    pxr/tf/dl.cpp
    pxr/tf/enum.cpp
    pxr/tf/envSetting.cpp
    pxr/tf/error.cpp
    pxr/tf/errorMark.cpp
    pxr/tf/errorTransport.cpp
    pxr/tf/exception.cpp
    pxr/tf/expiryNotifier.cpp
    pxr/tf/fastCompression.cpp
    pxr/tf/fileUtils.cpp
    pxr/tf/getenv.cpp
    pxr/tf/hash.cpp
    pxr/tf/initConfig.cpp
    pxr/tf/mallocTag.cpp
    pxr/tf/notice.cpp
    pxr/tf/noticeRegistry.cpp
    pxr/tf/nullPtr.cpp
    pxr/tf/pathUtils.cpp
    pxr/tf/patternMatcher.cpp
    pxr/tf/pxrDoubleConversion/bignum-dtoa.cc
    pxr/tf/pxrDoubleConversion/bignum.cc
    pxr/tf/pxrDoubleConversion/cached-powers.cc
    pxr/tf/pxrDoubleConversion/double-to-string.cc
    pxr/tf/pxrDoubleConversion/fast-dtoa.cc
    pxr/tf/pxrDoubleConversion/fixed-dtoa.cc
    pxr/tf/pxrDoubleConversion/string-to-double.cc
    pxr/tf/pxrDoubleConversion/strtod.cc
    pxr/tf/pxrLZ4/lz4.cpp
    pxr/tf/pyLock.cpp
    pxr/tf/pyObjWrapper.cpp
    pxr/tf/pyTracing.cpp
    pxr/tf/refBase.cpp
    pxr/tf/refPtr.cpp
    pxr/tf/refPtrTracker.cpp
    pxr/tf/regTest.cpp
    pxr/tf/registryManager.cpp
    pxr/tf/safeOutputFile.cpp
    pxr/tf/scopeDescription.cpp
    pxr/tf/setenv.cpp
    pxr/tf/singleton.cpp
    pxr/tf/smallVector.cpp
    pxr/tf/spinMutex.cpp
    pxr/tf/spinRWMutex.cpp
    pxr/tf/stackTrace.cpp
    pxr/tf/stl.cpp
    pxr/tf/stopwatch.cpp
    pxr/tf/stringUtils.cpp
    pxr/tf/templateString.cpp
    pxr/tf/token.cpp
    pxr/tf/type.cpp
    pxr/tf/typeNotice.cpp
    pxr/tf/unicodeCharacterClasses.cpp
    pxr/tf/unicodeUtils.cpp
    pxr/tf/weakBase.cpp
)

target_include_directories(tf
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(tf
    PUBLIC
        pxr::arch
        TBB::tbb
)

if (WIN32)
    target_link_libraries(tf PUBLIC Shlwapi.lib)
endif()

if(BUILD_PYTHON_BINDINGS)
    target_sources(tf
        PRIVATE
            pxr/tf/moduleDeps.cpp
            pxr/tf/makePyConstructor.cpp
            pxr/tf/pyArg.cpp
            pxr/tf/pyCallContext.cpp
            pxr/tf/pyEnum.cpp
            pxr/tf/pyError.cpp
            pxr/tf/pyErrorInternal.cpp
            pxr/tf/pyExceptionState.cpp
            pxr/tf/pyIdentity.cpp
            pxr/tf/pyInterpreter.cpp
            pxr/tf/pyInvoke.cpp
            pxr/tf/pyModule.cpp
            pxr/tf/pyModuleNotice.cpp
            pxr/tf/pyNoticeWrapper.cpp
            pxr/tf/pyObjectFinder.cpp
            pxr/tf/pyOverride.cpp
            pxr/tf/pySingleton.cpp
            pxr/tf/pyUtils.cpp
            pxr/tf/pyWrapContext.cpp
            pxr/tf/scriptModuleLoader.cpp
            pxr/tf/wrapTypeHelpers.cpp
    )

    target_link_libraries(tf
        PUBLIC
            pxr::boost-python
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(tf
        PRIVATE
            pxr/tf/pch.h
    )
endif()

set_target_properties(tf
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrTf"
)

target_compile_definitions(tf
    PRIVATE
        TF_EXPORTS=1
        MFB_PACKAGE_MODULE=Tf
        MFB_PACKAGE_NAME=tf
        MFB_ALT_PACKAGE_NAME=tf
)

target_sources(tf
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/tf/pxr.h
            pxr/tf/pxrCLI11/CLI11.h
            pxr/tf/pxrTslRobinMap/robin_growth_policy.h
            pxr/tf/pxrTslRobinMap/robin_hash.h
            pxr/tf/pxrTslRobinMap/robin_map.h
            pxr/tf/pxrTslRobinMap/robin_set.h
            pxr/tf/anyUniquePtr.h
            pxr/tf/anyWeakPtr.h
            pxr/tf/api.h
            pxr/tf/atomicOfstreamWrapper.h
            pxr/tf/bigRWMutex.h
            pxr/tf/bits.h
            pxr/tf/bitUtils.h
            pxr/tf/compressedBits.h
            pxr/tf/callContext.h
            pxr/tf/cxxCast.h
            pxr/tf/debug.h
            pxr/tf/debugNotice.h
            pxr/tf/declarePtrs.h
            pxr/tf/delegatedCountPtr.h
            pxr/tf/denseHashMap.h
            pxr/tf/denseHashSet.h
            pxr/tf/diagnostic.h
            pxr/tf/diagnosticBase.h
            pxr/tf/diagnosticHelper.h
            pxr/tf/diagnosticLite.h
            pxr/tf/diagnosticMgr.h
            pxr/tf/dl.h
            pxr/tf/enum.h
            pxr/tf/envSetting.h
            pxr/tf/error.h
            pxr/tf/errorMark.h
            pxr/tf/errorTransport.h
            pxr/tf/exception.h
            pxr/tf/expiryNotifier.h
            pxr/tf/fastCompression.h
            pxr/tf/fileUtils.h
            pxr/tf/functionRef.h
            pxr/tf/functionTraits.h
            pxr/tf/getenv.h
            pxr/tf/hash.h
            pxr/tf/hashmap.h
            pxr/tf/hashset.h
            pxr/tf/instantiateSingleton.h
            pxr/tf/instantiateStacked.h
            pxr/tf/instantiateType.h
            pxr/tf/iterator.h
            pxr/tf/mallocTag.h
            pxr/tf/meta.h
            pxr/tf/notice.h
            pxr/tf/nullPtr.h
            pxr/tf/ostreamMethods.h
            pxr/tf/pathUtils.h
            pxr/tf/patternMatcher.h
            pxr/tf/pointerAndBits.h
            pxr/tf/preprocessorUtilsLite.h
            pxr/tf/pyLock.h
            pxr/tf/pyObjWrapper.h
            pxr/tf/pyTracing.h
            pxr/tf/refBase.h
            pxr/tf/refPtr.h
            pxr/tf/refPtrTracker.h
            pxr/tf/regTest.h
            pxr/tf/registryManager.h
            pxr/tf/safeOutputFile.h
            pxr/tf/safeTypeCompare.h
            pxr/tf/scopeDescription.h
            pxr/tf/scoped.h
            pxr/tf/setenv.h
            pxr/tf/singleton.h
            pxr/tf/smallVector.h
            pxr/tf/span.h
            pxr/tf/spinMutex.h
            pxr/tf/spinRWMutex.h
            pxr/tf/stackTrace.h
            pxr/tf/stacked.h
            pxr/tf/staticData.h
            pxr/tf/staticTokens.h
            pxr/tf/status.h
            pxr/tf/stl.h
            pxr/tf/stopwatch.h
            pxr/tf/stringUtils.h
            pxr/tf/templateString.h
            pxr/tf/tf.h
            pxr/tf/token.h
            pxr/tf/type.h
            pxr/tf/typeFunctions.h
            pxr/tf/typeInfoMap.h
            pxr/tf/typeNotice.h
            pxr/tf/type_Impl.h
            pxr/tf/unicodeUtils.h
            pxr/tf/warning.h
            pxr/tf/weakBase.h
            pxr/tf/weakPtr.h
            pxr/tf/weakPtrFacade.h

)

if(BUILD_PYTHON_BINDINGS)
    target_sources(tf
        PUBLIC
            FILE_SET public_headers
            TYPE HEADERS
            BASE_DIRS
                ${CMAKE_CURRENT_SOURCE_DIR}
            FILES
                pxr/tf/makePyConstructor.h
                pxr/tf/py3Compat.h
                pxr/tf/pyAnnotatedBoolResult.h
                pxr/tf/pyArg.h
                pxr/tf/pyCall.h
                pxr/tf/pyCallContext.h
                pxr/tf/pyClassMethod.h
                pxr/tf/pyContainerConversions.h
                pxr/tf/pyEnum.h
                pxr/tf/pyError.h
                pxr/tf/pyExceptionState.h
                pxr/tf/pyFunction.h
                pxr/tf/pyIdentity.h
                pxr/tf/pyInterpreter.h
                pxr/tf/pyInvoke.h
                pxr/tf/pyModule.h
                pxr/tf/pyModuleNotice.h
                pxr/tf/pyNoticeWrapper.h
                pxr/tf/pyObjectFinder.h
                pxr/tf/pyOptional.h
                pxr/tf/pyOverride.h
                pxr/tf/pyPolymorphic.h
                pxr/tf/pyPtrHelpers.h
                pxr/tf/pyResultConversions.h
                pxr/tf/pySafePython.h
                pxr/tf/pySignatureExt.h
                pxr/tf/pySingleton.h
                pxr/tf/pyStaticTokens.h
                pxr/tf/pyUtils.h
                pxr/tf/pyWrapContext.h
                pxr/tf/scriptModuleLoader.h
                pxr/tf/wrapTypeHelpers.h
    )
endif()

install(
    TARGETS tf EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-tf-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-tf
)
