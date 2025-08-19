cmake_minimum_required(VERSION 3.31 FATAL_ERROR)

project(mag_cusps)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_PREFIX_PATH "~/local" ${CMAKE_PREFIX_PATH})

include(FetchContent)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON CACHE BOOL "Build with -fPIC" FORCE)

# Declare all dependencies first
find_package(Eigen3 QUIET)
if(NOT Eigen3_FOUND)
    FetchContent_Declare(
        eigen
        GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
        GIT_TAG 3.4.0
        GIT_SHALLOW TRUE
    )
endif()

find_package(absl QUIET)
if(NOT absl_FOUND)
    FetchContent_Declare(
        abseil
        GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git
        GIT_TAG 20240116.2
        GIT_SHALLOW TRUE
    )
endif()

find_package(Ceres QUIET)
if(NOT Ceres_FOUND)
    FetchContent_Declare(
        ceres
        GIT_REPOSITORY https://ceres-solver.googlesource.com/ceres-solver.git
        GIT_TAG 2.2.0
        GIT_SHALLOW TRUE
    )
endif()

find_package(pybind11 QUIET)
if(NOT pybind11_FOUND)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v3.0.0
    )
endif()




find_package(Eigen3 QUIET)
if(NOT Eigen3_FOUND)
    # Configure Eigen to not build BLAS/LAPACK before making it available
    message(STATUS "Configuring Eigen...")
    set(EIGEN_BUILD_PKGCONFIG OFF CACHE BOOL "Don't build pkg-config" FORCE)
    set(BUILD_TESTING OFF CACHE BOOL "Disable all testing" FORCE)
    set(EIGEN_BUILD_TESTING OFF CACHE BOOL "No Eigen tests" FORCE)
    set(EIGEN_BUILD_DOC OFF CACHE BOOL "No docs" FORCE)
    set(EIGEN_BUILD_DEMOS OFF CACHE BOOL "No demos" FORCE)

    # Make Eigen available but try to limit what gets built
    FetchContent_MakeAvailable(eigen)
endif()



# find_package(absl QUIET)
# if(NOT absl_FOUND)
#     # Configure and fetch Abseil
#     message(STATUS "Fetching Abseil...")
#     set(ABSL_ENABLE_INSTALL ON CACHE BOOL "Enable Abseil install" FORCE)
#     set(ABSL_BUILD_TEST_HELPERS OFF CACHE BOOL "Disable Abseil tests" FORCE)
#     set(ABSL_BUILD_TESTING OFF CACHE BOOL "Disable tests" FORCE)
#     set(ABSL_USE_EXTERNAL_GOOGLETEST OFF CACHE BOOL "No gtest" FORCE)
#     set(ABSL_FIND_GOOGLETEST OFF CACHE BOOL "No gtest search" FORCE)
#     set(ABSL_USE_SYSTEM_INCLUDES OFF CACHE BOOL "No system includes" FORCE)
#     set(ABSL_PROPAGATE_CXX_STD ON CACHE BOOL "Don't propagate C++ std" FORCE)

#     set(ABSL_BUILD_DLL OFF CACHE BOOL "" FORCE)
#     set(ABSL_USE_SYSTEM_INCLUDES OFF CACHE BOOL "" FORCE)
    
#     # Try to disable specific component groups
#     set(ABSL_BUILD_MONOLITHIC_SHARED_LIBS OFF CACHE BOOL "" FORCE)

#     FetchContent_MakeAvailable(abseil)
# endif()



find_package(Ceres QUIET)
if(NOT Ceres_FOUND)
    # Configure Ceres options before making it available
    message(STATUS "Configuring Ceres...")
    set(MINIGLOG ON CACHE BOOL "Use Ceres' minimal logging" FORCE)
    set(GLOG OFF CACHE BOOL "No full glog" FORCE)
    set(GFLAGS OFF CACHE BOOL "No gflags" FORCE)

    set(BUILD_TESTING OFF CACHE BOOL "Disable Ceres tests" FORCE)
    set(BUILD_EXAMPLES OFF CACHE BOOL "Disable Ceres examples" FORCE)
    set(BUILD_BENCHMARKS OFF CACHE BOOL "Disable Ceres benchmarks" FORCE)
    set(BUILD_DOCUMENTATION OFF CACHE BOOL "Disable Ceres documentation" FORCE)
    set(PROVIDE_UNINSTALL_TARGET OFF CACHE BOOL "Disable the ceres uninstall creation" FORCE)

    # set(CXSPARSE OFF CACHE BOOL "No CXSparse" FORCE)
    set(ACCELERATESPARSE OFF CACHE BOOL "No Accelerate" FORCE)
    # set(CUDSS OFF CACHE BOOL "No CUDSS" FORCE)
    set(SCHUR_SPECIALIZATIONS OFF CACHE BOOL "Remove Schur specializations" FORCE)
    set(CUDA OFF CACHE BOOL "No CUDA" FORCE)
    set(LAPACK OFF CACHE BOOL "No LAPACK" FORCE)
    set(SUITESPARSE OFF CACHE BOOL "No SuiteSparse" FORCE)
    set(EIGENSPARSE OFF CACHE BOOL "No Eigen sparse" FORCE)

    # Tell Ceres where to find Eigen
    FetchContent_GetProperties(eigen SOURCE_DIR eigen_source_dir)
    set(EIGEN3_INCLUDE_DIR ${eigen_source_dir} CACHE PATH "Eigen include directory" FORCE)
    set(Eigen3_FOUND TRUE CACHE BOOL "Eigen found" FORCE)

    FetchContent_MakeAvailable(ceres)
endif()



find_package(pybind11 QUIET)
if(NOT pybind11_FOUND)
    # Fetch pybind11
    message(STATUS "Fetching pybind11...")
    FetchContent_MakeAvailable(pybind11)
endif()


find_package(OpenMP QUIET)





# Compiler flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Prevent a "command line is too long" failure in Windows.
set(CMAKE_NINJA_FORCE_RESPONSE_FILE "ON" CACHE BOOL "Force Ninja to use response files.")





# Handle the fact that cibuildwheel runs in Docker containers on Linux
# Now that we're running from project root, this should be much simpler
message(STATUS "CMAKE_CURRENT_SOURCE_DIR: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "CMAKE_CURRENT_LIST_DIR: ${CMAKE_CURRENT_LIST_DIR}")

# CMAKE_CURRENT_LIST_DIR should be /project/library_python
# So PROJECT_ROOT should be /project (parent directory)
get_filename_component(PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}" DIRECTORY)

message(STATUS "Calculated PROJECT_ROOT: ${PROJECT_ROOT}")

# Verify that we found the right location
if(NOT EXISTS "${PROJECT_ROOT}/src_cpp" OR NOT EXISTS "${PROJECT_ROOT}/headers_cpp")
    message(STATUS "src_cpp not found at ${PROJECT_ROOT}/src_cpp, trying alternative paths...")
    
    # List what's actually available for debugging
    message(STATUS "Contents of PROJECT_ROOT (${PROJECT_ROOT}):")
    file(GLOB PROJECT_ROOT_CONTENTS "${PROJECT_ROOT}/*")
    foreach(ITEM ${PROJECT_ROOT_CONTENTS})
        message(STATUS "  ${ITEM}")
    endforeach()
    
    # Try other possibilities
    set(SEARCH_ROOTS)
    list(APPEND SEARCH_ROOTS "${PROJECT_ROOT}")
    list(APPEND SEARCH_ROOTS "${CMAKE_CURRENT_LIST_DIR}")
    list(APPEND SEARCH_ROOTS "${CMAKE_CURRENT_SOURCE_DIR}")
    
    set(FOUND_ROOT "")
    foreach(POTENTIAL_ROOT ${SEARCH_ROOTS})
        if(EXISTS "${POTENTIAL_ROOT}/src_cpp" AND EXISTS "${POTENTIAL_ROOT}/headers_cpp")
            set(FOUND_ROOT "${POTENTIAL_ROOT}")
            break()
        endif()
    endforeach()
    
    if(FOUND_ROOT)
        set(PROJECT_ROOT "${FOUND_ROOT}")
        message(STATUS "Found correct PROJECT_ROOT: ${PROJECT_ROOT}")
    else()
        message(FATAL_ERROR "Cannot find src_cpp and headers_cpp directories in any expected location")
    endif()
endif()

message(STATUS "Final PROJECT_ROOT: ${PROJECT_ROOT}")


# Check what's in the parent directory
file(GLOB_RECURSE ALL_CPP_FILES "${PROJECT_ROOT}/src_cpp/*.cpp")
message(STATUS "Found .cpp files: ${ALL_CPP_FILES}")


set(CUSP_POINTS "${PROJECT_ROOT}/src_cpp/points.cpp")
set(CUSP_MATRIX "${PROJECT_ROOT}/src_cpp/matrix.cpp")
set(CUSP_READ_FILE "${PROJECT_ROOT}/src_cpp/read_file.cpp")
set(CUSP_RAYCAST "${PROJECT_ROOT}/src_cpp/raycast.cpp")
set(CUSP_STREAMLINES "${PROJECT_ROOT}/src_cpp/streamlines.cpp")
set(CUSP_MAGNETOPAUSE "${PROJECT_ROOT}/src_cpp/magnetopause.cpp")
set(CUSP_PREPROCESSING "${PROJECT_ROOT}/src_cpp/preprocessing.cpp")
set(CUSP_FIT_TO_ANALYTICAL "${PROJECT_ROOT}/src_cpp/fit_to_analytical.cpp")
set(CUSP_ANALYSIS "${PROJECT_ROOT}/src_cpp/analysis.cpp")

set(CUSP_HEADERS "${PROJECT_ROOT}/headers_cpp")
message(STATUS "Found header directory: ${CUSP_HEADERS}")

set(SOURCES
    ${CUSP_POINTS}
    ${CUSP_MATRIX}
    ${CUSP_READ_FILE}
    ${CUSP_RAYCAST}
    ${CUSP_STREAMLINES}
    ${CUSP_MAGNETOPAUSE}
    ${CUSP_PREPROCESSING}
    ${CUSP_FIT_TO_ANALYTICAL}
    ${CUSP_ANALYSIS}
)



# Create the module
pybind11_add_module(
    mag_cusps 
    library.cpp
    ${SOURCES}
)



# Link libraries
set(LINK_LIBRARIES "")

# Link Ceres
if(TARGET ceres)
    list(APPEND LINK_LIBRARIES ceres)
endif()

# if(TARGET absl::log)
#     list(APPEND LINK_LIBRARIES absl::log absl::log_initialize absl::log_globals)
# endif()

# Link OpenMP if found
# if(OpenMP_CXX_FOUND)
#     list(APPEND LINK_LIBRARIES OpenMP::OpenMP_CXX)
# endif()

target_link_libraries(mag_cusps PRIVATE ${LINK_LIBRARIES})

# Get source directories for include paths
FetchContent_GetProperties(eigen SOURCE_DIR eigen_source_dir)
# FetchContent_GetProperties(absl SOURCE_DIR absl_source_dir)
FetchContent_GetProperties(ceres SOURCE_DIR ceres_source_dir BINARY_DIR ceres_binary_dir)

target_compile_definitions(mag_cusps PUBLIC USE_CUSP_HEADERS=1)
# Include directories
target_include_directories(mag_cusps PRIVATE
    ${CUSP_HEADERS}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    # ${NUMPY_INCLUDE_DIR}
    # ${eigen_source_dir}
    # ${absl_source_dir}
    ${ceres_source_dir}/include
    ${ceres_binary_dir}/include
)

# Compiler-specific options
target_compile_definitions(mag_cusps PRIVATE 
    VERSION_INFO=${EXAMPLE_VERSION_INFO}
)

# Add warning flags
target_compile_options(mag_cusps PRIVATE -Wall -Wextra)

# Set properties for the module
set_target_properties(mag_cusps PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    VISIBILITY_INLINES_HIDDEN YES
)

if (UNIX)
    target_link_options(mag_cusps PUBLIC -pthread)
endif()

install(TARGETS mag_cusps
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .
)
