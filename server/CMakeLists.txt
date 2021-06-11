cmake_minimum_required(VERSION 3.10)

# set the project name and version
# set the env_var PROJECT_NAME to the version given here
project(bench VERSION 1.0)

# add thread library, which has to be linked at compile time
find_package(Threads)

### building make for gtests ###

configure_file(CMakeLists.txt.in
        googletest-download/CMakeLists.txt)
execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-download )
execute_process(COMMAND ${CMAKE_COMMAND} --build .
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-download )

add_subdirectory(${CMAKE_BINARY_DIR}/googletest-src
        ${CMAKE_BINARY_DIR}/googletest-build)

enable_testing()
add_subdirectory(test)

### building make for executable ###

# add the executable
add_executable(server ${PROJECT_SOURCE_DIR}/src/chat.c)

# link the thread library with executable
target_link_libraries(server ${CMAKE_THREAD_LIBS_INIT})

# path to function definition
target_sources(server PUBLIC ${PROJECT_SOURCE_DIR}/src/queue.c)

# path to search for include files
include_directories(PUBLIC ${PROJECT_SOURCE_DIR}/inc)

# include compiler flags for better release/debug compilation
add_compile_options(-Wall -Wpedantic -Wextra -g)
