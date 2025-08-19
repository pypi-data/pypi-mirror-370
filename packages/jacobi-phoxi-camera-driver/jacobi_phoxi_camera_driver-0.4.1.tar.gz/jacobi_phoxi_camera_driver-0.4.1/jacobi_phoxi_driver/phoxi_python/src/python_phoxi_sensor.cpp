#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

#include <phoxi_sensor.h>


namespace py = pybind11;
using namespace pybind11::literals; // to bring in the `_a` literal


PYBIND11_MODULE(python_phoxi_sensor, m) {
    m.doc() = "Photoneo PhoXi driver";

    py::class_<PhoXiSensor> sensor(m, "PhoXiSensor");

    py::class_<std::shared_future<bool>>(m, "FutureBool")
        .def("get", &std::shared_future<bool>::get)
        .def("wait", &std::shared_future<bool>::wait)
        .def("__await__", [](const std::shared_future<bool>& self) { return self; })
        .def("__next__", [](const std::shared_future<bool>& self) {
            const bool has_finished = self.wait_for(std::chrono::seconds(0)) == std::future_status::ready;
            if (has_finished) {
                py::object o = py::cast(self.get());
                PyErr_SetObject(PyExc_StopIteration, o.ptr());
                throw py::error_already_set();
            }
            return py::none();
        });

    py::class_<PhoXiSensor::Intrinsics>(sensor, "Intrinsics")
        .def_readwrite("fx", &PhoXiSensor::Intrinsics::fx)
        .def_readwrite("fy", &PhoXiSensor::Intrinsics::fy)
        .def_readwrite("cx", &PhoXiSensor::Intrinsics::cx)
        .def_readwrite("cy", &PhoXiSensor::Intrinsics::cy)
        .def_readwrite("distortion_coefficients", &PhoXiSensor::Intrinsics::distortion_coefficients)
        .def("__repr__", [](const PhoXiSensor::Intrinsics& self) {
            std::cout << "<Intrinsics fx=" << self.fx << " fy=" << self.fy << " cx=" << self.cx << " cy=" << self.cy << ">";
        });

    sensor
        .def(py::init<const std::string&>(), "device_name"_a)
        .def("start", &PhoXiSensor::start)
        .def("stop", &PhoXiSensor::stop)
        .def("connect", &PhoXiSensor::connect)
        .def("frames", &PhoXiSensor::frames)
        .def("frames_async", &PhoXiSensor::frames_async)
        .def("save_last_frame", &PhoXiSensor::save_last_frame, "path"_a)
        .def("get_depth_map", &PhoXiSensor::get_depth_map)
        .def("get_texture", &PhoXiSensor::get_texture)
        .def_readonly("intrinsics", &PhoXiSensor::intrinsics);
}
