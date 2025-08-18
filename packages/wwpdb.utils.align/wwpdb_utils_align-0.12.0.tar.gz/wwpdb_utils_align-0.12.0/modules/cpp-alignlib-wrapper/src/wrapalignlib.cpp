// File: ./src/wrapalignlib.cpp
// Date: 2018-10-15
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
using namespace pybind11::literals;

void wrapPairwiseAlign(py::module &);
void wrapPseudoMultiAlign(py::module &);

PYBIND11_MODULE(alignlib, m) {
wrapPairwiseAlign(m);
wrapPseudoMultiAlign(m);
}
