cmake_minimum_required(VERSION 3.10)

# set the project name and version
# set the env_var PROJECT_NAME to the version given here
project(bench VERSION 1.0)

# add the executable
add_executable(client ${PROJECT_SOURCE_DIR}/src/client.c)

# creates a shared library for implementation in python code
add_library(lclient SHARED ${PROJECT_SOURCE_DIR}/src/client.c)

# path to search for include files
include_directories(PUBLIC ${PROJECT_SOURCE_DIR}/inc)

# include compiler flags for better release/debug compilation
add_compile_options(-Wall -Wpedantic -Wextra -g)
