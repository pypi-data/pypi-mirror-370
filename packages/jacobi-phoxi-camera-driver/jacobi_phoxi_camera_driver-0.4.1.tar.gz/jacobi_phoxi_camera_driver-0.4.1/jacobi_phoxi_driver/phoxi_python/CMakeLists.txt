cmake_minimum_required(VERSION 3.15)
include(FetchContent)


project(phoxi-sensor)


find_package(PhoXi REQUIRED CONFIG PATHS "$ENV{PHOXI_CONTROL_PATH}")

FetchContent_Declare(pybind11 GIT_REPOSITORY https://github.com/pybind/pybind11.git GIT_TAG v2.13.5)
FetchContent_MakeAvailable(pybind11)


add_library(phoxi-sensor src/phoxi_sensor.cpp)
target_link_libraries(phoxi-sensor PUBLIC
  ${PHOXI_LIBRARY}
  $<$<PLATFORM_ID:Linux>:rt>
)
target_include_directories(phoxi-sensor PUBLIC include ${PHOXI_INCLUDE_DIRS})
set_target_properties(phoxi-sensor PROPERTIES POSITION_INDEPENDENT_CODE ON)


pybind11_add_module(python_phoxi_sensor
  src/python_phoxi_sensor.cpp
)
target_include_directories(python_phoxi_sensor PUBLIC include ${PHOXI_INCLUDE_DIRS})
target_link_libraries(python_phoxi_sensor PUBLIC phoxi-sensor ${PHOXI_LIBRARY})


install(TARGETS python_phoxi_sensor LIBRARY DESTINATION .)
