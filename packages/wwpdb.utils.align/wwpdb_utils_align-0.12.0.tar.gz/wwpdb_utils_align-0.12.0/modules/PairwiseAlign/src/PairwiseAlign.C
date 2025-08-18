/** @file PairwiseAlign.C
 *
 *   File:  PairwiseAlign.C
 *   Date:  Dec 28, 2009 JDW 
 *
 *  Implementation of local pairwise alignment utilties.
 *  Adapts the particular code from Smith-Waterman local alignment algorithm 
 *  from RCSB Maxit (Z. Feng).  A simplified binary scoring function is used
 *  to address the problem of aligning reference, author supplied and coordinate
 *  sequences. 
 *
 *  Methods are provided to manage and align multiple pairwise alignments from
 *  to a common reference sequence.
 *
 *
 *  Updated:  Jan 13, 2010  ZF - Back out windowed search and fix memory bug 
 *   
 */

#include "PairwiseAlign.h"
#include <stdio.h>
#include <iostream>
#include <iomanip>

using namespace RCSB;

#ifndef MAX
#define MAX(X, Y)   (((X) > (Y))? (X): (Y))
#endif

static const double _nearZero=0.001;
static const char *a1_a3_code[22][2] = {
        { "A",    "ALA" },
        { "R",    "ARG" },
        { "N",    "ASN" },
        { "D",    "ASP" },
        { "C",    "CYS" },
        { "Q",    "GLN" },
        { "E",    "GLU" },
        { "G",    "GLY" },
        { "H",    "HIS" },
        { "I",    "ILE" },
        { "L",    "LEU" },
        { "K",    "LYS" },
        { "M",    "MET" },
        { "F",    "PHE" },
        { "P",    "PRO" },
        { "S",    "SER" },
        { "T",    "THR" },
        { "W",    "TRP" },
        { "Y",    "TYR" },
        { "V",    "VAL" },
        { "O",    "PYL" },
        { "U",    "SEC" }
};

PairwiseAlign::PairwiseAlign() {
  _init();
  _verbose=false;
  if (_verbose) std::cerr << "++INFO - Initializing PairwiseAlign - with default constructor" << std::endl;
}

void PairwiseAlign::_init() {
  _reset();
  _gapPenalty = 2.0;
  _gapSymbol=".";
  for (int i = 0; i < 20; ++i) {
    _a1_a3_mapping.insert(std::make_pair(a1_a3_code[i][0], a1_a3_code[i][1]));
  }
}

void PairwiseAlign::_reset() {
  _a1_a3_mapping.clear();
  _seqRef.clear();
  _seqRefConsensus.clear();
  _idRef.clear();
  _seqTest.clear();
  _idTestList.clear();

  _seqTestMap.clear();
  _linkageTestMap.clear();
  _rangeTestMap.clear();
  _seqRefMap.clear();
  _alignmentMap.clear();
}

void PairwiseAlign::clear() {
  _reset();
}

void PairwiseAlign::setVerbose(bool verbose) {
  _verbose=verbose;
}

void PairwiseAlign::prAlignment(const std::string & seqName) {
  wrAlignment(std::cout, seqName);
}

void PairwiseAlign::prAlignmentConflicts(const std::string & seqName) {
  wrAlignmentConflicts(std::cout, seqName);
}

void PairwiseAlign::prAlignmentFull() {
  wrAlignmentFull(std::cout);
}

void PairwiseAlign::wrAlignment(std::ostream & io, const std::string & seqName) {
  
  if ( _alignmentMap.find(seqName) != _alignmentMap.end()) {
    io << "Alignment between reference sequence "<< _idRef.c_str() 
       << " and test sequence "<< seqName.c_str() << std::endl;
    std::vector<std::pair<std::string, std::string> >::iterator sIt;
    unsigned int ii;
    for (sIt=_alignmentMap[seqName].begin(), ii=0; sIt != _alignmentMap[seqName].end(); ++sIt,ii++) {
      io << std::setw(8) << ii << " " << std::setw(4) << sIt->first << " " << std::setw(4) << sIt->second << std::endl;
    }
    io.flush();
  }

}

void PairwiseAlign::wrAlignmentFull(std::ostream & io) {
  
  // all alignments must have the same length - so take the first - 
  //
  unsigned int aPos, ii, aLen;
  std::string seqName;
  aLen=_alignmentMap[_idTestList[0]].size();
  //
  io << std::endl;
  io << "Alignment results for reference sequence " << _idRef.c_str() 
     << " with " << _idTestList.size() << " test sequences." << std::endl;
  for (ii=0; ii < _idTestList.size(); ii++) {  // over aligned test sequences  - 
    seqName=_idTestList[ii];
    io << seqName.c_str() << " ";
  }
  io << std::endl;
  io << "Alignment length is " << aLen << std::endl;
  // 

  for (aPos=0; aPos < aLen; aPos++) {  // iterate over residues in the alignment
    io << std::setw(8) << aPos << " " << std::setw(4) << _seqRefConsensus[aPos];
    for (ii=0; ii < _idTestList.size(); ii++) {  // over aligned test sequences  - 
      seqName=_idTestList[ii];
      io << " -  "<< std::setw(4) << _alignmentMap[seqName][aPos].second;
    }
    io << std::endl;
  }
  io.flush();
}


void PairwiseAlign::wrAlignmentConflicts(std::ostream & io, const std::string & seqName) {

  if ( _alignmentMap.find(seqName) != _alignmentMap.end()) {
    io << "Alignment conflicts between reference sequence "<< _idRef.c_str() 
       << " and test sequence "<< seqName.c_str() << std::endl;
    std::vector<std::pair<std::string, std::string> >::iterator sIt;
    unsigned int ii;
    for (sIt=_alignmentMap[seqName].begin(), ii=0; sIt != _alignmentMap[seqName].end(); ++sIt,ii++) {
      if (sIt->first != sIt->second) {
	io << "Conflict at alignment position " << std::setw(8) << ii 
	   << " " << std::setw(4)    << sIt->first << " " << std::setw(4) << sIt->second << std::endl;
      }
    }
    io.flush();
  }
}


void PairwiseAlign::testExample(void) {

  std::vector<std::pair<std::string, std::string> > _align; // 

  // skip the cif parser to read the seq info. 
  std::string seq_seqres = "HHHGARIGLAWIPYFGPAAHHH";
  std::string seq_coord = "(GLY)(ALA)(ALA)(ILE)(GLY)(LEU)(ALA)(TRP)(ILE)(PRO)(PHE)(GLY)(PRO)(ALA)(ALA)";
  
  _get_sequence_array(_seqRef,  seq_seqres);
  _get_sequence_array(_seqTest, seq_coord);
  
  // one letter to three letter conversion
  // only for protein seqeunce
  for (unsigned int i = 0; i < _seqRef.size(); ++i) {
    if (_seqRef[i].size() == 1) {
      std::map<std::string, std::string>::iterator pos = _a1_a3_mapping.find(_seqRef[i]);
      if (pos != _a1_a3_mapping.end()) _seqRef[i] = pos->second;
    }
  }
  _seqRefConsensus=_seqRef;
  std::vector<bool> linkage;
  linkage.clear();
  _alignment(_align, _seqRef, _seqTest, linkage);
  
  printf("SEQRES: ");
  for (unsigned int i = 0; i < _align.size(); ++i) {
    printf("%3s ", _align[i].first.c_str());
  }
  printf("\n");
  
  printf("COORD:  ");
  for (unsigned int i = 0; i < _align.size(); ++i) {
    printf("%3s ", _align[i].second.c_str());
  }
  printf("\n");
  
  //       return 0;
}

void PairwiseAlign::setReferenceSequence(const std::vector<std::string> & sR, const std::string &seqName) {
  _seqRef = sR;
  _seqRefConsensus = sR;
  _idRef=seqName;
}

unsigned int PairwiseAlign::addTestSequenceWithLink(const std::vector<std::string> & sT, const std::string & seqName, const std::vector<int>& linkage)
{
  _idTestList.push_back(seqName);
  _seqTestMap[seqName]=sT;
  if (!linkage.empty() && sT.size() == linkage.size()) {
    std::vector<bool> bLink;
    bLink.clear();
    for (unsigned int i = 0; i< linkage.size(); ++i) {
      if (linkage[i] == 1) {
	bLink.push_back(1);
      } else {
	bLink.push_back(0);	
      }
    }
    _linkageTestMap.insert(std::make_pair(seqName, bLink));
  }
  return _seqTestMap.size();
}

unsigned int PairwiseAlign::addTestSequenceWithLinkAndRange(const std::vector<std::string> & sT, const std::string & seqName,
                                                            const std::vector<int>& linkage, const int& begin, const int& end)
{
  _idTestList.push_back(seqName);
  _seqTestMap[seqName]=sT;
  if (!linkage.empty() && sT.size() == linkage.size()) {
    std::vector<bool> bLink;
    bLink.clear();
    for (unsigned int i = 0; i< linkage.size(); ++i) {
      if (linkage[i] == 1) {
	bLink.push_back(1);
      } else {
	bLink.push_back(0);	
      }
    }
    _linkageTestMap.insert(std::make_pair(seqName, bLink));
  }
  if ((begin < end) /* && ((end - begin + 1) >= (int) sT.size()) */ ) {
    unsigned int b = 0;
    if (begin > 0) b = begin - 1;
    unsigned int e = end;
    if (e >= _seqRefConsensus.size()) e = _seqRefConsensus.size();
    /* if ((e - b + 1) >=  sT.size()) */ _rangeTestMap.insert(std::make_pair(seqName, std::make_pair(b, e)));
  } 
  return _seqTestMap.size();
}

unsigned int PairwiseAlign::addTestSequence(const std::vector<std::string> & sT, const std::string & seqName) {
  _idTestList.push_back(seqName);
  _seqTestMap[seqName]=sT;
  return _seqTestMap.size();
}

std::vector<std::pair<std::string, std::string> > PairwiseAlign::getAlignment(const std::string & seqName) { 
  std::vector<std::pair<std::string, std::string> > myAlignment;
  myAlignment.clear();
  if ( _alignmentMap.find(seqName) != _alignmentMap.end()) {
    myAlignment=  _alignmentMap[seqName];
  }
  return myAlignment;
}

#if 0
// This is currently problematic for Boost. 
void PairwiseAlign::updAlignment(const std::string & seqName, std::vector<std::pair<std::string, std::string> > & align) { 
  //std::vector<std::pair<std::string, std::string> > myAlignment;
  if ( _alignmentMap.find(seqName) != _alignmentMap.end()) {
    align =  _alignmentMap[seqName];
  }
}
#endif

void PairwiseAlign::doAlign() {
  std::vector<bool> linkage;
  std::map<std::string, std::vector<std::string> >::iterator mIt;
  for (mIt = _seqTestMap.begin(); mIt !=_seqTestMap.end(); ++mIt) {
    _seqTest=mIt->second;
    linkage.clear();
    std::map<std::string, std::vector<bool> >::const_iterator
        mpos = _linkageTestMap.find(mIt->first);
    if (mpos != _linkageTestMap.end()) linkage = mpos->second;
    std::map<std::string, std::pair<unsigned int, unsigned int> >::const_iterator
        rpos = _rangeTestMap.find(mIt->first);
    if (rpos != _rangeTestMap.end())
         _alignment(_alignmentMap[mIt->first], _seqRefConsensus, _seqTest, linkage, rpos->second.first, rpos->second.second);
    else _alignment(_alignmentMap[mIt->first], _seqRefConsensus, _seqTest, linkage);
  }
}

unsigned int PairwiseAlign::countGaps(const std::vector<std::string> &seq) {
  std::vector<std::string>::const_iterator sIt;
  unsigned int iCount;
  iCount =0;
  for (sIt = seq.begin(); sIt != seq.end(); ++sIt   ) {
    if (*sIt == _gapSymbol) iCount++;
  }
  return iCount;
}

std::vector<std::string> PairwiseAlign::doAlignConsensus() {
  // Find a consensus pairwise alignment of the reference sequence with each
  // of the test sequences - 
  //
  std::map<std::string, std::vector<std::string> >::iterator mIt;
  std::string seqName;
  unsigned int nGapsR, nGapsT;
  _seqRefConsensus = _seqRef;
  std::vector<bool> linkage;
  for (mIt = _seqTestMap.begin(); mIt !=_seqTestMap.end(); ++mIt) {
    seqName=mIt->first;
    _seqTest=mIt->second;
    _alignmentMap[seqName].clear();
    nGapsR=countGaps(_seqRefConsensus);
    nGapsT=countGaps(_seqTest);
    if (_verbose) {
      std::cerr << "Aligning " << seqName.c_str()  << " len test " << _seqTest.size() << " length consensus sequence " << _seqRefConsensus.size() << std::endl;
      std::cerr << "Aligning " << seqName.c_str()  << " gaps test " << nGapsT  << "  gaps reference " << nGapsR << std::endl;
    }

    linkage.clear();
    std::map<std::string, std::vector<bool> >::const_iterator
        mpos = _linkageTestMap.find(mIt->first);
    if (mpos != _linkageTestMap.end()) linkage = mpos->second;
    std::map<std::string, std::pair<unsigned int, unsigned int> >::const_iterator
        rpos = _rangeTestMap.find(mIt->first);
    if (rpos != _rangeTestMap.end())
         _alignment(_alignmentMap[seqName], _seqRefConsensus, _seqTest, linkage, rpos->second.first, rpos->second.second);
    else _alignment(_alignmentMap[seqName], _seqRefConsensus, _seqTest, linkage);
    if (_verbose) { std::cerr << "Aligned " << seqName.c_str()  << " length of test sequence " << _seqTest.size() 
		       << " length of consensus sequence " << _seqRefConsensus.size() << std::endl;
        for (unsigned int i = 0; i < _seqRefConsensus.size(); ++i) {
             std::cerr << i + 1 << " ( " << _seqRefConsensus.size() << " ) " << _seqRefConsensus[i] << std::endl;
        }
    }
    _extractSequence("reference",seqName,_seqRefConsensus);
    if (_verbose)  std::cerr << "Extracted " << seqName.c_str()  << " length of test sequence " << _seqTest.size() 
			<< " length consensus sequence " << _seqRefConsensus.size() << std::endl;

  }
  if (_verbose)   std::cerr << "Completed alignment pass I" << std::endl;
  // Repeat the alignments with the consensus sequence -
  std::vector<std::string> failedSeq;
  std::vector<std::string> sT;
  failedSeq.clear();
  sT.clear();
  for (mIt = _seqTestMap.begin(); mIt !=_seqTestMap.end(); ++mIt) {
    seqName=mIt->first;
    _seqTest=mIt->second;
    _alignmentMap[seqName].clear();
    if (_verbose)     std::cerr << "Realigning - " << seqName.c_str()  << " length of test sequence " << _seqTest.size() 
			   << " length of consensus sequence " << _seqRefConsensus.size() << std::endl;

    linkage.clear();
    std::map<std::string, std::vector<bool> >::const_iterator
        mpos = _linkageTestMap.find(mIt->first);
    if (mpos != _linkageTestMap.end()) linkage = mpos->second;
    std::map<std::string, std::pair<unsigned int, unsigned int> >::const_iterator
        rpos = _rangeTestMap.find(mIt->first);
    if (rpos != _rangeTestMap.end())
         _alignment(_alignmentMap[seqName], _seqRefConsensus, _seqTest, linkage, rpos->second.first, rpos->second.second);
    else _alignment(_alignmentMap[seqName], _seqRefConsensus, _seqTest, linkage);

    _extractSequence("reference",seqName,sT);
    if (! _compareSequence(_seqRefConsensus,sT) ) {
      failedSeq.push_back(seqName);
    }
  }

  return failedSeq;
}

// Find pairwise alignment of the reference sequence with each of the test sequences using multiple sequence alignment method
std::vector<std::string> PairwiseAlign::doMultipleAlign()
{
       std::vector<std::vector<std::string> > sa;
       sa.clear();
       sa.reserve(_seqRef.size());
       std::vector<std::string> data;
       for (unsigned int i = 0; i < _seqRef.size(); ++i) {
            data.clear();
            data.push_back(_seqRef[i]);
            sa.push_back(data);
       }

       std::vector<std::string> idList;
       idList.clear();
       idList.push_back(_idRef);

       std::vector<std::string> failedSeq;
       failedSeq.clear();
       std::vector<bool> linkage;
       for (std::vector<std::string>::const_iterator pos = _idTestList.begin(); pos != _idTestList.end(); ++pos) {
            std::map<std::string, std::vector<std::string> >::const_iterator mIt = _seqTestMap.find(*pos);
            if (mIt == _seqTestMap.end()) {
                 failedSeq.push_back(*pos);
                 continue;
            }
            idList.push_back(mIt->first);

            linkage.clear();
            std::map<std::string, std::vector<bool> >::const_iterator mpos = _linkageTestMap.find(mIt->first);
            if (mpos != _linkageTestMap.end()) linkage = mpos->second;

            std::map<std::string, std::pair<unsigned int, unsigned int> >::const_iterator rpos = _rangeTestMap.find(mIt->first);
            if (rpos != _rangeTestMap.end())
                 sa = _multiple_alignment(sa, mIt->second, linkage, rpos->second.first, rpos->second.second);
            else sa = _multiple_alignment(sa, mIt->second, linkage);
       }

       _seqRefConsensus.clear();
       _seqRefConsensus.reserve(sa.size());
       for (unsigned int i = 0; i < sa.size(); ++i) {
            _seqRefConsensus.push_back(sa[i][0]);
       }

       std::vector<std::pair<std::string, std::string> > align_pair;
       _alignmentMap.clear();
       for (unsigned int k = 1; k < idList.size(); ++k) {
            std::map<std::string, std::vector<std::string> >::const_iterator mIt = _seqTestMap.find(idList[k]);
            if (mIt == _seqTestMap.end()) continue;

            align_pair.clear();
            for (unsigned int i = 0; i < sa.size(); ++i) {
                 align_pair.push_back(std::make_pair(sa[i][0], sa[i][k]));
            }
            _alignmentMap.insert(std::make_pair(idList[k], align_pair));
       }

       return failedSeq;
}

bool PairwiseAlign::_compareSequence(const std::vector<std::string> &seqVa, const std::vector<std::string> &seqVb) {
  //
  if (seqVa.size() != seqVb.size()) {
    return false;
  }
  unsigned int ii;
  for (ii = 0; ii < seqVa.size(); ii++) {
    if (seqVa[ii] != seqVb[ii]) {
      return false;
    }
  }
  return true;
}

void PairwiseAlign::_extractSequence(const std::string & type, const std::string & seqName, std::vector<std::string> & seqV  ) {
  // Extract the named sequence of type (reference/test) from the current alignment and store this in 
  // in the input string vector. 
  //
  seqV.clear();
  if ( _alignmentMap.find(seqName) != _alignmentMap.end()) {
    std::vector<std::pair<std::string, std::string> >::iterator sIt;
    unsigned int ii;
    if (type == "reference") {
      for (sIt=_alignmentMap[seqName].begin(), ii=0; sIt != _alignmentMap[seqName].end(); ++sIt,ii++) {
	//std::cerr << "Extracting " << seqName.c_str() << " position " << ii << " residue " << sIt->first << std::endl;
	seqV.push_back(sIt->first);
      }
      if (_verbose) std::cerr << "Extracted aligned reference sequence from alignment "<< seqName.c_str() << " sequence length " << seqV.size() << std::endl;
    } else if ( type == "test") {
      for (sIt=_alignmentMap[seqName].begin(), ii=0; sIt != _alignmentMap[seqName].end(); ++sIt,ii++) {
	seqV.push_back(sIt->second);
      }
      if (_verbose) std::cerr << "Extracted aligned test sequence from alignment "<< seqName.c_str() << " sequence length " << seqV.size() << std::endl;
    }
  } else { 
    std::cerr << "Sequence extraction failed for " << seqName.c_str() << std::endl;
  }

}

void PairwiseAlign::_get_sequence_array(std::vector<std::string> &seqs, const std::string &sequence) {
       seqs.clear();
       std::string cs;
       for (unsigned int j = 0; j < sequence.size(); ++j) {
            if (sequence[j] == ' ' || sequence[j] == '\t' ||
                sequence[j] == '\n') continue;
            if (sequence[j] != '(') {
                 cs.clear();
                 cs += sequence[j];
                 seqs.push_back(cs);
            } else {
                 ++j;
                 cs.clear();
                 while (sequence[j] != ')') {
                      if (sequence[j] != ' ' && sequence[j] != '\t' &&
                          sequence[j] != '\n') cs += sequence[j];
                      ++j;
                 }
                 seqs.push_back(cs);
            }
       }
}

int PairwiseAlign::_score(const int k, const int l)
{
       if (_seqRefConsensus[k] == _seqTest[l]) {
            if (_seqRefConsensus[k] == "ALA")
                 return 2;
            else return 5;
       } else if (_seqRefConsensus[k][0] == '-') {
            std::string res = _seqRefConsensus[k].substr(1);
            if (res == _seqTest[l]) {
                 if (res == "ALA")
                      return 1;
                 else return 3;
            }
       }

       return 0;
}
/*
void PairwiseAlign::_alignment(std::vector<std::pair<std::string, std::string> >& align_pair, const std::vector<std::string> &seq_a,
                               const std::vector<std::string> &seq_b, const std::vector<bool>& linkage)
{
       std::vector<std::vector<int> > ss, sa, sb;
       std::vector<int> data;
       sa.clear();
       sa.reserve(seq_a.size());
       for (unsigned int i = 0; i < seq_a.size(); ++i) {
            data.clear();
            data.push_back(i);
            sa.push_back(data);
       }

       sb.clear();
       sb.reserve(seq_b.size());
       for (unsigned int i = 0; i < seq_b.size(); ++i) {
            data.clear();
            data.push_back(i);
            sb.push_back(data);
       }

       ss.clear();
       _alignmentQ(ss, sa, sb, linkage);

       align_pair.clear();
       align_pair.reserve(ss.size());
       for (unsigned int i = 0; i < ss.size(); ++i) {
            if (ss[i][0] >= 0 && ss[i][1] >= 0)
                 align_pair.push_back(std::make_pair(seq_a[ss[i][0]], seq_b[ss[i][1]]));
            else if (ss[i][0] >= 0)
                 align_pair.push_back(std::make_pair(seq_a[ss[i][0]], _gapSymbol));
            else if (ss[i][1] >= 0)
                 align_pair.push_back(std::make_pair(_gapSymbol, seq_b[ss[i][1]]));
       }
}
*/

void PairwiseAlign::_alignment(std::vector<std::pair<std::string, std::string> >& align_pair, const std::vector<std::string> &seq_a,
                                          const std::vector<std::string> &seq_b, const std::vector<bool>& linkage,
                                          const unsigned int& begin_orig, const unsigned int& end_orig)
{
       unsigned int begin = 0 /*, end = seq_a.size() */ ;
       if (begin_orig && end_orig) {
            unsigned int start_num = 0, count = 0;
            if (begin_orig >= 10) start_num = begin_orig - 10;

            bool found_begin = false, found_end = false;
            for (unsigned int i = 0; i < seq_a.size(); ++i) {
                 if (seq_a[i] == _gapSymbol) continue;
                 if (count == start_num) {
                      begin = i;
                      found_begin = true;
                 } else if (count == (end_orig - 1)) {
                      // end = i + 1;
                      found_end = true;
                      if (found_begin) break;
                 }
                 count++;
            }
            if (!found_begin || !found_end) begin = 0;
       }

       std::vector<std::vector<int> > ss, sa, sb;
       std::vector<int> data;
       sa.clear();
       sa.reserve(seq_a.size());
       // for (unsigned int i = begin; i < end; ++i) {
       for (unsigned int i = begin; i < seq_a.size(); ++i) {
            data.clear();
            data.push_back(i);
            sa.push_back(data);
       }

       sb.clear();
       sb.reserve(seq_b.size());
       for (unsigned int i = 0; i < seq_b.size(); ++i) {
            data.clear();
            data.push_back(i);
            sb.push_back(data);
       }

       ss.clear();
       _alignmentQ(ss, sa, sb, linkage);

       align_pair.clear();
       // int length = begin + ss.size() + seq_a.size() - end;
       int length = begin + ss.size();
       align_pair.reserve(length);
       for (unsigned int i = 0; i < begin; ++i) align_pair.push_back(std::make_pair(seq_a[i], _gapSymbol));
       for (unsigned int i = 0; i < ss.size(); ++i) {
            if (ss[i][0] >= 0 && ss[i][1] >= 0)
                 align_pair.push_back(std::make_pair(seq_a[ss[i][0]], seq_b[ss[i][1]]));
            else if (ss[i][0] >= 0)
                 align_pair.push_back(std::make_pair(seq_a[ss[i][0]], _gapSymbol));
            else if (ss[i][1] >= 0)
                 align_pair.push_back(std::make_pair(_gapSymbol, seq_b[ss[i][1]]));
       }
       // for (unsigned int i = end; i < seq_a.size(); ++i) align_pair.push_back(std::make_pair(seq_a[i], _gapSymbol));
}

std::vector<std::vector<std::string> > PairwiseAlign::_multiple_alignment(const std::vector<std::vector<std::string> >& ss_in,
                                                    const std::vector<std::string>& seq_b, const std::vector<bool>& linkage,
                                                    const unsigned int& begin_orig, const unsigned int& end_orig)
{
       _seqTest = seq_b;

       std::vector<std::vector<int> > ss, sa, sb;

       unsigned int begin = _getConsensusSeq(sa, ss_in, begin_orig, end_orig, 10);

       std::vector<int> data;

       sb.clear();
       sb.reserve(seq_b.size());
       for (unsigned int i = 0; i < seq_b.size(); ++i) {
            data.clear();
            data.push_back(i);
            sb.push_back(data);
       }

       ss.clear();
       _alignmentQ(ss, sa, sb, linkage);

       if (begin) {
            unsigned int count = 0;
            for (unsigned int i = 0; i < ss.size(); ++i) {
                 if (ss[i][0] >= 0) break;
                 count++;
            }
            if (count) {
                 begin = _getConsensusSeq(sa, ss_in, begin_orig, end_orig, count + 10);
                 ss.clear();
                 _alignmentQ(ss, sa, sb, linkage);
            }
       }

       std::vector<std::string> seq;

       std::vector<std::vector<std::string> > ss_out;
       ss_out.clear();
       ss_out.reserve(begin + ss.size());
       for (unsigned int i = 0; i < begin; ++i) {
            seq = ss_in[i];
            seq.push_back(_gapSymbol);
            ss_out.push_back(seq);
       }
       for (unsigned int i = 0; i < ss.size(); ++i) {
            if (ss[i][0] >= 0) {
                 seq = ss_in[ss[i][0] + begin];
                 if (ss[i][1] >= 0)
                      seq.push_back(seq_b[ss[i][1]]);
                 else seq.push_back(_gapSymbol);
                 ss_out.push_back(seq);
            } else {
                 seq.clear();
                 for (unsigned int j = 0; j < ss_in[0].size(); ++j) seq.push_back(_gapSymbol);
                 seq.push_back(seq_b[ss[i][1]]);
                 ss_out.push_back(seq);
            }
       }

       return ss_out;
}

unsigned int PairwiseAlign::_getConsensusSeq(std::vector<std::vector<int> >& sa, const std::vector<std::vector<std::string> >& ss_in,
                                             const unsigned int& begin_orig, const unsigned int& end_orig, const unsigned int& extra)
{
       unsigned int begin = 0;
       if (begin_orig && end_orig) {
            unsigned int start_num = 0, count = 0;
            if (begin_orig >= extra) start_num = begin_orig - extra;

            bool found_begin = false, found_end = false;
            for (unsigned int i = 0; i < ss_in.size(); ++i) {
                 if (ss_in[i][0] == _gapSymbol) continue;
                 if (count == start_num) {
                      begin = i;
                      found_begin = true;
                 } else if (count == (end_orig - 1)) {
                      found_end = true;
                      if (found_begin) break;
                 }
                 count++;
            }
            if (!found_begin || !found_end) begin = 0;
       }

       std::vector<int> data;

       sa.clear();
       sa.reserve(ss_in.size() - begin);

       _seqRefConsensus.clear();
       _seqRefConsensus.reserve(ss_in.size() - begin);

       for (unsigned int i = begin; i < ss_in.size(); ++i) {
            data.clear();
            data.push_back(_seqRefConsensus.size());
            sa.push_back(data);

            std::string res = _gapSymbol;
            if (ss_in[i][0] != _gapSymbol)
                 res = ss_in[i][0];
            else {
                 for (unsigned int k = 1; k < ss_in[i].size(); ++k) {
                      if (ss_in[i][k] != _gapSymbol) {
                           res = "-" + ss_in[i][k];
                           break;
                      }
                 }
            }
            _seqRefConsensus.push_back(res);
       }

       return begin;
}

void PairwiseAlign::_alignmentQ(std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& sa,
                                const std::vector<std::vector<int> >& sb, const std::vector<bool>& linkage)
{
       std::vector<SAVE> dr;
       dr.clear();
       int n = 60 * sb.size();
       dr.reserve(n);
       double extendedPenalty = 1.0;
       if (!linkage.empty()) extendedPenalty = 0.0;
       int origin = _dynamic(sa, sb, _gapPenalty, extendedPenalty, dr, linkage);
       _mu_trcback(origin, ss, sa, sb, dr);
}

int PairwiseAlign::_dynamic(const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb, const double& vv,
                            const double& uu, std::vector<SAVE>& dr, const std::vector<bool>& linkage)
{
       int m = sa.size();
       int n = sb.size();

       RECD *dd = new RECD[n + 1];
       RECD *gg = new RECD[n + 1];
       char *dir = new char[m + n + 1];

       int origin = _adr(0, 0, -1, dr);
       for (int i = 0; i < (m + n + 1); i++) dir[i] = 0;
       for (int i = 0; i <= n; i++) {
            dd[i].val = 0; dd[i].ptr = origin;
            gg[i].val = 0; gg[i].ptr = origin;
       }

       double big_vv = 10 * vv;
       int k = 0;
       double x, max_val = 0, maximum = -1.0e38;
       RECD  nd, f, dt, dtt;
       for (int i = 0; i < m; i++) {
            int j  = 0;
            RECD *d = dd + j;
            RECD *g = gg + j;
            d->val = f.val = 0;
            d->ptr = f.ptr = origin;
            int r = j - i + m;
            dt = *d;
            for (d++, g++; j < n; d++, g++, r++, j++) {
                 if ((x = (d-1)->val - big_vv - uu) >= (f.val -= uu)) {
                      f.val = x; f.ptr = (d-1)->ptr;
                 }
                 double vv1 = vv;
                 if (!linkage.empty() && linkage[j]) vv1 = big_vv;
                 if ((x = d->val - vv1 - uu) >= (g->val -= uu)) {
                      g->val = x; g->ptr = d->ptr;
                 }
                 nd.val = maximum;
                 nd.ptr = -1;
                 if (f.val > nd.val) nd = f;
                 if (g->val > nd.val) nd = *g;
                 dt.val += SCORE_FUNCT(sa[i][0], sb[j][0]);
                 dtt = *d;
                 *d = dt;
                 if (nd.val > d->val) {
                      *d = nd;
                      dir[r] = 0;
                 } else if (!dir[r]) {
                      d->ptr = _adr(i, j, d->ptr, dr);
                      dir[r] = 1;
                 }
                 if (d->val > max_val) {
                      max_val = d->val;
                      k = d->ptr;
                 }
                 dt = dtt;
            }
       }

       delete [] dd;
       delete [] gg;
       delete [] dir;

       return (_adr(m, n, k, dr));
}

void PairwiseAlign::_mu_trcback(const int& origin, std::vector<std::vector<int> >& ss,
                                const std::vector<std::vector<int> >& a,
                                const std::vector<std::vector<int> >& b,
                                const std::vector<SAVE>& dr)
{
       ss.clear();

       std::list<std::pair<int, int> > top;
       top.clear();

       int i = origin;
       while (i >= 0) {
            top.push_front(std::make_pair(dr[i].m, dr[i].n));
            i = dr[i].pp;
       }
       if (top.empty()) return;

       int n1 = 0;
       int n2 = 0;
       int j, m, n, r;
       std::list<std::pair<int, int> >::iterator pos = top.begin();
       std::list<std::pair<int, int> >::iterator pos1 = top.begin();
       pos1++;
       while (pos1 != top.end()) {
	    if ((i = pos->first) - (j = pos->second) > 
                (m = pos1->first) - (n = pos1->second) && 
                (r = m - i + j) != j) {
                 n1 += (n - r); 
                 top.insert(pos1, std::make_pair(m, r));
            } else if ((i = pos->first) - (j = pos->second) < 
               (m = pos1->first) - (n = pos1->second) && 
               (r = n + i - j) != i) {
                 n2 += (m - r); 
                 top.insert(pos1, std::make_pair(r, n));
            }
            pos = pos1;
            pos1++;
       }

       m = a.size() + n1;
       n = b.size() + n2;
       int n9 = MAX(m, n);
       ss.reserve(n9);
       std::vector<int> data;
       data.clear();
       data.push_back(-1);
       data.push_back(-1);
       for (i = 0; i < n9; ++i) ss.push_back(data);

       _track(ss, top, a, b);
}

void PairwiseAlign::_track(std::vector<std::vector<int> >& aa, std::list<std::pair<int, int> >& top,
                const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb)
{
       int x, y, m, n, r;

       r = 0;
       std::list<std::pair<int, int> >::iterator pos = top.begin();
       std::list<std::pair<int, int> >::iterator pos1 = top.begin();
       pos1++;
       while (pos1 != top.end()) {
	    if ((x = pos->first) - (y = pos->second) == 
                (m = pos1->first) - (n = pos1->second)) {
		 for (int i = 0; i < m - x; ++i) {
                      aa[i + r][0] = sa[x + i][0];
                      aa[i + r][1] = sb[y + i][0];
		 }
		 r += (m - x);
	    } else if(x - y < m - n) {
		 for (int i = 0; i < m - x; ++i) {
                      aa[i + r][0] = sa[x + i][0];
		 }
		 r += (m - x);
	    } else {
		 for (int i = 0; i < n - y; ++i) {
                      aa[i + r][1] = sb[y + i][0];
		 }
		 r += (n - y);
	    }
            pos = pos1;
            pos1++;
       }
}

int PairwiseAlign::_adr(const int& m, const int& n, const int& pp, std::vector<SAVE>& dr)
{
       int i_record = dr.size();

       SAVE s;
       s.m = m;
       s.n = n;
       s.pp = pp;
       dr.push_back(s);  

       return (i_record);
}
