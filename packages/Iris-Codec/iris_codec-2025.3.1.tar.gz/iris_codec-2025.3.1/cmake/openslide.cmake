include(FindPkgConfig)
pkg_check_modules(OPENSLIDE openslide)
if (OPENSLIDE_FOUND)
    # Best case: .pc loaded and gives up the package vars
    find_library (OPENSLIDE_LIB openslide PATHS  ${OPENSLIDE_LIBDIR})
    set (OPENSLIDE_DIR ${OPENSLIDE_INCLUDE_DIRS})
else ()
    # Maybe the pc didn't work but we can try to just find the files
    find_library (OPENSLIDE_LIB openslide)
    find_path(OPENSLIDE_DIR openslide/openslide.h)
endif()

# Okay unsurprisingly cmake couldn't load the .pc package config. 
# Pull the precompiled binaries for OpenSlide. I hate this solution but it's the best available at the moment.
# Compiling OpenSlide with Meson has proven both really buggy and frustrating so I'm just not going to support that.
if (NOT OPENSLIDE_LIB OR NOT OPENSLIDE_DIR)
message(STATUS "FAILED to find OpenSlide on your system. We will pull precompiled binaries for openslide - it cannot be built into the system.")
message(WARNING "Downloading OpenSlide precompiled binaries. It is up to you to ENSURE the numerous openslide dependencies are present at runtime.")
    if (WIN32)
        message(STATUS "Downloading https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.6-windows-x64.zip...")
        file (DOWNLOAD https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.6-windows-x64.zip ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.zip)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E tar -xf ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.zip
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/_deps/
            RESULT_VARIABLE extract_success 
        )
        find_library (OPENSLIDE_LIB openslide HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.6-windows-x64/lib)
        find_path(OPENSLIDE_DIR openslide/openslide.h HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.6-windows-x64/include)
    elseif(UNIX)
        if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
            message(STATUS "Downloading https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.6-macos-arm64-x86_64.tar.xz...")
            file (DOWNLOAD https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.6-macos-arm64-x86_64.tar.xz ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz)
            execute_process(
                COMMAND ${CMAKE_COMMAND} -E tar -xf ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz 
                WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/_deps/
                RESULT_VARIABLE extract_success
            )
            find_library (OPENSLIDE_LIB openslide HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.6-macos-arm64-x86_64/lib)
            find_path(OPENSLIDE_DIR openslide/openslide.h PATHS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.6-macos-arm64-x86_64/include)
        else()
            if (${CMAKE_SYSTEM_PROCESSOR} MATCHES "aarch64" OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "ARM64")
                message(STATUS "Downloading https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.5-linux-aarch64.tar.xz...")
                file (DOWNLOAD https://github.com/openslide/openslide-bin/releases/download/v4.0.0.5/openslide-bin-4.0.0.5-linux-aarch64.tar.xz ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz)
                execute_process(
                    COMMAND ${CMAKE_COMMAND} -E tar -xf ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz 
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/_deps/
                    RESULT_VARIABLE extract_success
                )
                find_library (OPENSLIDE_LIB openslide HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.5-linux-aarch64/lib)
                find_path(OPENSLIDE_DIR openslide/openslide.h PATHS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.5-linux-aarch64/include)
            elseif (${CMAKE_SYSTEM_PROCESSOR} MATCHES "x86_64" OR (${CMAKE_SYSTEM_PROCESSOR} MATCHES "AMD64"))
                message(STATUS "Downloading https://github.com/openslide/openslide-bin/releases/download/v4.0.0.6/openslide-bin-4.0.0.5-linux-x86_64.tar.xz...")
                file(DOWNLOAD https://github.com/openslide/openslide-bin/releases/download/v4.0.0.5/openslide-bin-4.0.0.5-linux-x86_64.tar.xz ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz)
                execute_process(
                    COMMAND ${CMAKE_COMMAND} -E tar -xf ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide.tar.xz 
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/_deps/
                    RESULT_VARIABLE extract_success 
                )
                find_library (OPENSLIDE_LIB openslide HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.5-linux-x86_64/lib)
                find_path(OPENSLIDE_DIR openslide/openslide.h HINTS ${CMAKE_CURRENT_BINARY_DIR}/_deps/openslide-bin-4.0.0.5-linux-x86_64/include)
            endif()
        endif()
    endif()
endif(NOT OPENSLIDE_LIB OR NOT OPENSLIDE_DIR)
if (NOT OPENSLIDE_LIB)
    message(FATAL_ERROR "Failed to find OpenSlide. Disable encoder functionality (-DIRIS_BUILD_ENCODER=OFF) to skip OpenSlide requirement.")
endif()