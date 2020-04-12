cmake_minimum_required(VERSION 3.10)

# set the project name and version
# set the env_var PROJECT_NAME to the version given here
project(bench VERSION 1.0)

# not mandatory
enable_language(C)

# set hosting system and processor
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

# set the right compiler for cross-compilation to ARM architecture
set(CMAKE_C_COMPILER /usr/bin/arm-linux-gnueabi-gcc)

# add the executable
add_executable(bench src/client.c)

# path to search for include files
# target_source_directories(socket "${PROJECT_SOURCE_DIR}/src")
include_directories(bench PUBLIC "${PROJECT_SOURCE_DIR}/client/inc")
