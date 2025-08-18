#include <pybind11/stl.h>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h> //https://people.duke.edu/~ccc14/cspy/18G_C++_Python_pybind11.html#Using-the-C++-eigen-library-to-calculate-matrix-inverse-and-determinant
#include "Alpha.hpp"
namespace py = pybind11;



void init_Alpha(py::module &m) {

     py::class_<petls::Alpha, petls::Complex>(m, "Alpha")
     .def(py::init<const char* , int>()) // Alpha(const char* filename, int max_dim); // .OFF file 
     .def(py::init<std::vector<std::tuple<double,double,double>>, int>());// Alpha(std::vector<std::tuple<double,double,double>> &points, int max_dim); // coordinantes

}
