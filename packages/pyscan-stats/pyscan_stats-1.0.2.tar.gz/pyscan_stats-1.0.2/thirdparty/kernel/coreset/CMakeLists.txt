cmake_minimum_required(VERSION 3.5)

project(coreset LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCE_FILES
    appext.cpp
    generator.cpp
    myinc.cpp
)

# Create shared library
add_library(appext SHARED ${SOURCE_FILES})

# So it finds libann.so
set_target_properties(appext PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

# Include directories
target_include_directories(appext PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include               # for appext.h and myinc.h
    # ${CMAKE_CURRENT_SOURCE_DIR}                       # for same-folder cpp/h includes
    ${CMAKE_SOURCE_DIR}/thirdparty/kernel/ANN/include # for ANN/ANN.h
)

# Link to ANN library
target_link_libraries(appext PRIVATE ann)