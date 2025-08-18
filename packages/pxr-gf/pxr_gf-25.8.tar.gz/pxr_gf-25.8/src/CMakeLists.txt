configure_file(
    pxr/gf/pxr.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/pxr/gf/pxr.h
    @ONLY
)

add_library(gf
    pxr/gf/nc/nanocolor.c
    pxr/gf/bbox3d.cpp
    pxr/gf/camera.cpp
    pxr/gf/color.cpp
    pxr/gf/colorSpace.cpp
    pxr/gf/dualQuatd.cpp
    pxr/gf/dualQuatf.cpp
    pxr/gf/dualQuath.cpp
    pxr/gf/frustum.cpp
    pxr/gf/gamma.cpp
    pxr/gf/half.cpp
    pxr/gf/homogeneous.cpp
    pxr/gf/ilmbase_half.cpp
    pxr/gf/interval.cpp
    pxr/gf/line.cpp
    pxr/gf/line2d.cpp
    pxr/gf/lineSeg.cpp
    pxr/gf/lineSeg2d.cpp
    pxr/gf/math.cpp
    pxr/gf/matrixData.cpp
    pxr/gf/matrix2d.cpp
    pxr/gf/matrix2f.cpp
    pxr/gf/matrix3f.cpp
    pxr/gf/matrix3d.cpp
    pxr/gf/matrix4f.cpp
    pxr/gf/matrix4d.cpp
    pxr/gf/multiInterval.cpp
    pxr/gf/ostreamHelpers.cpp
    pxr/gf/plane.cpp
    pxr/gf/quatd.cpp
    pxr/gf/quatf.cpp
    pxr/gf/quath.cpp
    pxr/gf/quaternion.cpp
    pxr/gf/range1d.cpp
    pxr/gf/range1f.cpp
    pxr/gf/range2d.cpp
    pxr/gf/range2f.cpp
    pxr/gf/range3d.cpp
    pxr/gf/range3f.cpp
    pxr/gf/ray.cpp
    pxr/gf/rect2i.cpp
    pxr/gf/rotation.cpp
    pxr/gf/size2.cpp
    pxr/gf/size3.cpp
    pxr/gf/transform.cpp
    pxr/gf/vec2d.cpp
    pxr/gf/vec2f.cpp
    pxr/gf/vec2h.cpp
    pxr/gf/vec2i.cpp
    pxr/gf/vec3d.cpp
    pxr/gf/vec3f.cpp
    pxr/gf/vec3h.cpp
    pxr/gf/vec3i.cpp
    pxr/gf/vec4d.cpp
    pxr/gf/vec4f.cpp
    pxr/gf/vec4h.cpp
    pxr/gf/vec4i.cpp
)

target_include_directories(gf
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(gf
    PUBLIC
        pxr::arch
        pxr::tf
)
 
if(BUILD_PYTHON_BINDINGS)
    target_sources(gf
        PRIVATE
            pxr/gf/moduleDeps.cpp
            pxr/gf/pyBufferUtils.cpp
    )

    target_link_libraries(gf
        PUBLIC
            pxr::boost-python
    )

    add_subdirectory(python)
endif()

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(gf
        PRIVATE
            "$<$<COMPILE_LANGUAGE:CXX>:pxr/gf/pch.h>"
    )
endif()

set_target_properties(gf
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrGf"
)

target_compile_definitions(gf
    PRIVATE
        GF_EXPORTS=1
        MFB_PACKAGE_MODULE=Gf
        MFB_PACKAGE_NAME=gf
        MFB_ALT_PACKAGE_NAME=gf
)

target_sources(gf
    PUBLIC
        FILE_SET public_headers
        TYPE HEADERS
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}
        FILES
            ${CMAKE_CURRENT_BINARY_DIR}/pxr/gf/pxr.h
            pxr/gf/api.h
            pxr/gf/bbox3d.h
            pxr/gf/camera.h
            pxr/gf/color.h
            pxr/gf/colorSpace.h
            pxr/gf/declare.h
            pxr/gf/dualQuatd.h
            pxr/gf/dualQuatf.h
            pxr/gf/dualQuath.h
            pxr/gf/frustum.h
            pxr/gf/gamma.h
            pxr/gf/half.h
            pxr/gf/homogeneous.h
            pxr/gf/ilmbase_half.h
            pxr/gf/ilmbase_halfLimits.h
            pxr/gf/interval.h
            pxr/gf/limits.h
            pxr/gf/line.h
            pxr/gf/line2d.h
            pxr/gf/lineSeg.h
            pxr/gf/lineSeg2d.h
            pxr/gf/math.h
            pxr/gf/matrixData.h
            pxr/gf/matrix2d.h
            pxr/gf/matrix2f.h
            pxr/gf/matrix3f.h
            pxr/gf/matrix3d.h
            pxr/gf/matrix4f.h
            pxr/gf/matrix4d.h
            pxr/gf/multiInterval.h
            pxr/gf/numericCast.h
            pxr/gf/plane.h
            pxr/gf/quatd.h
            pxr/gf/quatf.h
            pxr/gf/quath.h
            pxr/gf/quaternion.h
            pxr/gf/range1d.h
            pxr/gf/range1f.h
            pxr/gf/range2d.h
            pxr/gf/range2f.h
            pxr/gf/range3d.h
            pxr/gf/range3f.h
            pxr/gf/ray.h
            pxr/gf/rect2i.h
            pxr/gf/rotation.h
            pxr/gf/size2.h
            pxr/gf/size3.h
            pxr/gf/traits.h
            pxr/gf/transform.h
            pxr/gf/vec2d.h
            pxr/gf/vec2f.h
            pxr/gf/vec2h.h
            pxr/gf/vec2i.h
            pxr/gf/vec3d.h
            pxr/gf/vec3f.h
            pxr/gf/vec3h.h
            pxr/gf/vec3i.h
            pxr/gf/vec4d.h
            pxr/gf/vec4f.h
            pxr/gf/vec4h.h
            pxr/gf/vec4i.h
)

if(BUILD_PYTHON_BINDINGS)
    target_sources(gf
        PUBLIC
            FILE_SET public_headers
            TYPE HEADERS
            BASE_DIRS
                ${CMAKE_CURRENT_SOURCE_DIR}
            FILES
                pxr/gf/pyBufferUtils.h
    )
endif()

install(
    TARGETS gf EXPORT ${PROJECT_NAME}
    FILE_SET public_headers
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-gf-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-gf
)
