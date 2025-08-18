add_library(pyGf SHARED
    module.cpp
    wrapBBox3d.cpp
    wrapCamera.cpp
    wrapColor.cpp
    wrapColorSpace.cpp
    wrapDualQuatd.cpp
    wrapDualQuatf.cpp
    wrapDualQuath.cpp
    wrapFrustum.cpp
    wrapGamma.cpp
    wrapHalf.cpp
    wrapHomogeneous.cpp
    wrapInterval.cpp
    wrapLimits.cpp
    wrapLine.cpp
    wrapLineSeg.cpp
    wrapMath.cpp
    wrapMatrix2d.cpp
    wrapMatrix2f.cpp
    wrapMatrix3f.cpp
    wrapMatrix3d.cpp
    wrapMatrix4f.cpp
    wrapMatrix4d.cpp
    wrapMultiInterval.cpp
    wrapPlane.cpp
    wrapQuaternion.cpp
    wrapQuatd.cpp
    wrapQuatf.cpp
    wrapQuath.cpp
    wrapRange1d.cpp
    wrapRange1f.cpp
    wrapRange2d.cpp
    wrapRange2f.cpp
    wrapRange3d.cpp
    wrapRange3f.cpp
    wrapRay.cpp
    wrapRect2i.cpp
    wrapRotation.cpp
    wrapSize2.cpp
    wrapSize3.cpp
    wrapTransform.cpp
    wrapVec2d.cpp
    wrapVec2f.cpp
    wrapVec2h.cpp
    wrapVec2i.cpp
    wrapVec3d.cpp
    wrapVec3f.cpp
    wrapVec3h.cpp
    wrapVec3i.cpp
    wrapVec4d.cpp
    wrapVec4f.cpp
    wrapVec4h.cpp
    wrapVec4i.cpp
)

set_target_properties(pyGf
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME _gf
        RUNTIME_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Gf"
        LIBRARY_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Gf"
        ARCHIVE_OUTPUT_DIRECTORY "$<CONFIG>/pxr/Gf"
        POSITION_INDEPENDENT_CODE ON
)

target_include_directories(pyGf
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(pyGf
    PUBLIC
        gf
        pxr::boost-python
)

if(SKBUILD AND NOT WIN32)
    set(_rpath_prefix "$ORIGIN")
    if(APPLE)
        set(_rpath_prefix "@loader_path")
    endif()
    set_target_properties(pyGf
        PROPERTIES
            INSTALL_RPATH "${_rpath_prefix}/../.libs"
            INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endif()

if(WIN32)
    set_target_properties(pyGf PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(pyGf PROPERTIES SUFFIX ".so")
endif()

target_compile_definitions(
    pyGf
    PRIVATE
        BOOST_BIND_GLOBAL_PLACEHOLDERS
        BOOST_PYTHON_NO_PY_SIGNATURES
        MFB_PACKAGE_MODULE=Gf
        MFB_PACKAGE_NAME=gf
        MFB_ALT_PACKAGE_NAME=gf
)

file(
    GENERATE
    OUTPUT "$<TARGET_FILE_DIR:pyGf>/__init__.py"
    INPUT "__init__.py"
)

install(
    TARGETS pyGf EXPORT ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Gf
    RUNTIME DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Gf
)
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_PYTHON_LIBDIR}/pxr/Gf
)
