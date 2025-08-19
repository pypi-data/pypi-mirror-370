cmake_minimum_required(VERSION 3.5)

if(APPLE)
    list(APPEND CMAKE_PREFIX_PATH
        /opt/homebrew/opt
        /usr/local/opt
        /Users/${USER}/homebrew/opt
    )
    set(CMAKE_OSX_DEPLOYMENT_TARGET "14.0" CACHE STRING "" FORCE)
endif()

project(pyscan LANGUAGES CXX)

set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
set(Python_LIBRARY "${PYTHON_LIBRARY}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(PYBIND11_FINDPYTHON ON)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_DEBUG   "-fPIC -Wall -Wextra -g -O1 -fno-omit-frame-pointer")
set(CMAKE_C_FLAGS_DEBUG     "-fPIC -Wall -Wextra -g -O1 -fno-omit-frame-pointer")

set(CMAKE_CXX_FLAGS_RELEASE "-fPIC -w -O2 -DNDEBUG")
set(CMAKE_C_FLAGS_RELEASE   "-fPIC -w -O2 -DNDEBUG")

if(NOT APPLE)
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=native")
  set(CMAKE_C_FLAGS_RELEASE   "${CMAKE_C_FLAGS_RELEASE}   -march=native")
endif()

set(CMAKE_CXX_STANDARD_REQUIRED YES)

# Dependencies
if (PYSCAN_BUILD_TESTS)
  find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
else()
  find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
endif()

find_package(pybind11 CONFIG REQUIRED)
find_package(Boost REQUIRED)
find_package(CGAL REQUIRED)
find_package(GSL REQUIRED)

if (APPLE AND Boost_VERSION VERSION_GREATER_EQUAL 108800)
  add_compile_options(-include boost/multiprecision/gmp.hpp)
endif()

# Build the thirdparty libraries
add_subdirectory(thirdparty/discrepancy)
add_subdirectory(thirdparty/kernel/ANN)
add_subdirectory(thirdparty/kernel/coreset)

# Core sources
file(GLOB_RECURSE CPP_SRC CONFIGURE_DEPENDS src/cpp/lib/*.cpp)

add_library(core_obj OBJECT ${CPP_SRC})

target_include_directories(core_obj PUBLIC
    ${CMAKE_SOURCE_DIR}/src/cpp/lib/include
    ${CMAKE_SOURCE_DIR}/thirdparty/discrepancy/include
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/ANN/include
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/coreset/include
    ${Boost_INCLUDE_DIRS}
    ${GSL_INCLUDE_DIRS}
    ${CGAL_INCLUDE_DIRS}
)

target_link_libraries(core_obj PUBLIC CGAL::CGAL)

target_link_libraries(core_obj PRIVATE pybind11::module ${Python3_LIBRARIES})

function(set_loader_path lib)
  if(APPLE)
    set_target_properties(${lib} PROPERTIES
        BUILD_RPATH "@loader_path"
        INSTALL_RPATH "@loader_path")
  else()
    set_target_properties(${lib} PROPERTIES
        BUILD_RPATH "$ORIGIN"
        INSTALL_RPATH "$ORIGIN")
  endif()
endfunction()

set_loader_path(discrepancy)
set_loader_path(ann)
set_loader_path(appext)

pybind11_add_module(libpyscan MODULE
    $<TARGET_OBJECTS:core_obj>
    src/cpp/bindings/libpyscan.cpp
)

target_include_directories(ann PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/ANN/include
)
add_dependencies(libpyscan ann)

# Link libraries
target_link_libraries(libpyscan PRIVATE
    core_obj
    discrepancy
    ann
    appext
    CGAL::CGAL
    GSL::gsl
    GSL::gslcblas
)

set_loader_path(libpyscan)

# Install Python module and dependencies into the `pyscan/` package dir
# install(TARGETS libpyscan LIBRARY DESTINATION pyscan COMPONENT default)
# install(FILES
#     $<TARGET_FILE:discrepancy>
#     $<TARGET_FILE:ann>
#     $<TARGET_FILE:appext>
#     DESTINATION pyscan
#     COMPONENT default
# )
install(TARGETS libpyscan discrepancy ann appext
        LIBRARY DESTINATION pyscan
        COMPONENT default)

option(PYSCAN_BUILD_TESTS "Build tests" OFF)

if(PYSCAN_BUILD_TESTS)

    include(CTest)
    enable_testing()

    message(STATUS "BUILDING TESTS")
    set(THIRDPARTY_LIBRARIES
        discrepancy
        ann
        appext
        CGAL::CGAL
        GSL::gsl
        GSL::gslcblas
    )
    include(FetchContent)
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/release-1.12.1.zip
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
    set(TEST_NAMES
        DiskScan_unittest
        FunctionApprox_unittest
        Halfplane_unittest
        Testing_unittest
        Point_unittest
        RectangleScan_unittest
        trajectory_unittest
    )
    set(TEST_OUTPUT_DIR ${CMAKE_BINARY_DIR}/test)
    file(MAKE_DIRECTORY ${TEST_OUTPUT_DIR})

    foreach(TEST ${TEST_NAMES})
        add_executable(${TEST} test/${TEST}.cpp $<TARGET_OBJECTS:core_obj>)
        set_target_properties(${TEST} PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${TEST_OUTPUT_DIR}
        )
        target_link_libraries(${TEST} PRIVATE
            gtest_main
            pybind11::embed
            ${THIRDPARTY_LIBRARIES}
        )
        # target_include_directories(${TEST} PRIVATE ${CMAKE_SOURCE_DIR}/src/cpp/lib/include)
        # target_include_directories(${TEST} PRIVATE ${Python3_INCLUDE_DIRS})
        target_include_directories(${TEST} PRIVATE
            ${CMAKE_SOURCE_DIR}/src/cpp/lib/include
        )
        # include_directories(${pybind11_INCLUDE_DIRS})
        add_test(NAME ${TEST} COMMAND ${TEST})
        message(STATUS "Adding test: ${TEST} at binary dir ${TEST_OUTPUT_DIR}/${TEST}")
    endforeach()
endif()