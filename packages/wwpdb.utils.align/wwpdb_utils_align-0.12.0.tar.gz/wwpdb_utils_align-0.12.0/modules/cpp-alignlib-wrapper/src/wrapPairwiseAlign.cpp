// File: ./src/wrapPairwiseAlign.cpp
// Date: 2018-10-15
//

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <ostream>
#include <list>
#include <vector>
#include <map>
#include <utility>
#include "PairwiseAlign.h"
namespace py = pybind11;
using namespace pybind11::literals;

using namespace RCSB;

void wrapPairwiseAlign(py::module &m) {
   m.doc() = "Wrapper for header file PairwiseAlign.h";

   {
    py::class_<PairwiseAlign, std::shared_ptr<PairwiseAlign>> cls(m, "PairwiseAlign", "Wrapper for class PairwiseAlign");
   
     cls.def(py::init<>());
     cls.def("clear", &PairwiseAlign::clear,"");
     cls.def("setVerbose", &PairwiseAlign::setVerbose,"",py::arg("verbose"));
     cls.def("setReferenceSequence", &PairwiseAlign::setReferenceSequence,"",py::arg("sR"), py::arg("seqName"));
     cls.def("addTestSequence", &PairwiseAlign::addTestSequence,"",py::arg("sR"), py::arg("seqName"));
     cls.def("addTestSequenceWithLink", &PairwiseAlign::addTestSequenceWithLink,"",py::arg("sR"), py::arg("seqName"), py::arg("linkage"));
     cls.def("addTestSequenceWithLinkAndRange", &PairwiseAlign::addTestSequenceWithLinkAndRange,"",py::arg("sR"), py::arg("seqName"), py::arg("linkage"), py::arg("begin"), py::arg("end"));
     cls.def("getAlignment", &PairwiseAlign::getAlignment,"",py::arg("seqName"));
     cls.def("prAlignment", &PairwiseAlign::prAlignment,"",py::arg("seqName"));
     cls.def("prAlignmentConflicts", &PairwiseAlign::prAlignmentConflicts,"",py::arg("seqName"));
     cls.def("prAlignmentFull", &PairwiseAlign::prAlignmentFull,"");
     cls.def("doAlign", &PairwiseAlign::doAlign,"");
     cls.def("testExample", &PairwiseAlign::testExample,"");
     cls.def("doAlignConsensus", &PairwiseAlign::doAlignConsensus,"");
     cls.def("doMultipleAlign", &PairwiseAlign::doMultipleAlign,"");
     cls.def("countGaps", &PairwiseAlign::countGaps,"",py::arg("seq"));
   }

}