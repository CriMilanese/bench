cmake_minimum_required(VERSION 3.10)

# set the project name and version
# set the env_var PROJECT_NAME to the version given here
project(bench VERSION 1.0)

# add thread library, which has to be linked at compile time
find_package(Threads)

# add the executable
add_executable(server ${PROJECT_SOURCE_DIR}/src/chat.c)

# link the thread library with executable
target_link_libraries(server ${CMAKE_THREAD_LIBS_INIT})

# path to function definition
target_sources(server PUBLIC ${PROJECT_SOURCE_DIR}/inc/queue.c)

# path to search for include files
include_directories(PUBLIC ${PROJECT_SOURCE_DIR}/inc)

# include compiler flags for better release/debug compilation
add_compile_options(-Wall -Wpedantic -Wextra -g)
