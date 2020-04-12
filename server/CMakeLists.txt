cmake_minimum_required(VERSION 3.10)

# set the project name and version
# set the env_var PROJECT_NAME to the version given here
project(bench VERSION 1.0)

# configure header file to pass the version number
# configure_file(TutorialConfig.h.in TutorialConfig.h)

# add the executable
add_executable(bench src/chat.c)

# path to search for include files
# target_source_directories(socket "${PROJECT_SOURCE_DIR}/src")
include_directories(bench PUBLIC "${PROJECT_SOURCE_DIR}/server/inc")
