// File: ./src/wrapPseudoMultiAlign.cpp
// Date: 2018-10-15
//

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include "PseudoMultiAlign.h"
namespace py = pybind11;
using namespace pybind11::literals;

using namespace RCSB;

void wrapPseudoMultiAlign(py::module &m) {
   m.doc() = "Wrapper for header file PseudoMultiAlign.h";

   {
    py::class_<PseudoMultiAlign, std::shared_ptr<PseudoMultiAlign>> cls(m, "PseudoMultiAlign", "Wrapper for class PseudoMultiAlign");
   
     cls.def(py::init<>());
     cls.def("clear", &PseudoMultiAlign::clear,"");
     cls.def("setPenaltyFactor", &PseudoMultiAlign::setPenaltyFactor,"",py::arg("value"));
     cls.def("setRefScore", &PseudoMultiAlign::setRefScore,"");
     cls.def("setAuthScore", &PseudoMultiAlign::setAuthScore,"");
     cls.def("setAuthSequence", &PseudoMultiAlign::setAuthSequence,"",py::arg("seqs"));
     cls.def("addAlignSequence", &PseudoMultiAlign::addAlignSequence,"",py::arg("seqs"));
     cls.def("addAlignSequenceWithRange", &PseudoMultiAlign::addAlignSequenceWithRange,"",py::arg("seqs"), py::arg("begin"), py::arg("end"));
     cls.def("addAlignSequenceWithLinkageAndRange", &PseudoMultiAlign::addAlignSequenceWithLinkageAndRange,"",py::arg("seqs"), py::arg("linkage"), py::arg("begin"), py::arg("end"));
     cls.def("getAlignIndices", &PseudoMultiAlign::getAlignIndices,"");
     cls.def("getAlignSequences", &PseudoMultiAlign::getAlignSequences,"");
   }

}