pybind11_add_module(core wrapper/wrapper.cpp)

target_link_libraries(core PRIVATE x3cflux-measurement)
target_include_directories(core PRIVATE wrapper)
target_compile_definitions(core PRIVATE VERSION_INFO=${CMAKE_PROJECT_VERSION})

install(TARGETS core DESTINATION lib)