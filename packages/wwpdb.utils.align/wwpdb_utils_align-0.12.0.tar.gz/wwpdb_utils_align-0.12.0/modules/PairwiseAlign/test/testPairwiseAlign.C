/** @file testPairwiseAlign.C
 *
 *   File:  testPairwiseAlign.C
 *   Date:  Jan 28, 2009 JDW 
 *
 *  Example program illustrating the pairwise sequence alignment and the 
 *  alignment of multiple pairwise alignments with a common reference sequence.
 *  
 *  Updated: Jan 13, 2010 JDW -  Add test cases for the alignment of multiple 
 *                               aligned pairs.
 */

#include <stdio.h>
#include <iostream>

#include "PairwiseAlign.h"
#include "TestSequenceData.h"

#define EMPTY_STRING static_cast<const char *>("")

using namespace RCSB;

int main(int argc, char *argv[])
{
  std::vector<std::string> sRef;
  std::vector<std::string> sTest;

  std::vector<std::pair<std::string, std::string> > align;

  unsigned int i;
  i=0;
  while (RCSB::_refSequenceA[i] != EMPTY_STRING) {
    sRef.push_back(RCSB::_refSequenceA[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authSequenceA[i] != EMPTY_STRING) {
    sTest.push_back(RCSB::_authSequenceA[i]);
    i++;
  };    

  PairwiseAlign pA=PairwiseAlign();
  pA.testExample();

  pA.setReferenceSequence(sRef,"REFA");
  pA.addTestSequence(sTest,"SEQA");
  pA.doAlign();
  align = pA.getAlignment("SEQA");
  std::vector<std::pair<std::string, std::string> >::iterator sIt;
  unsigned int ii;
  for (sIt=align.begin(), ii=0; sIt != align.end(); ++sIt,ii++) {
    std::cout << " Position " << ii << " " << sIt->first << " " << sIt->second << std::endl;
  }
  //
  pA.wrAlignmentConflicts(std::cout,"SEQA");

  //
  //
  std::vector<std::string> r0,t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10;

  i=0;
  while (RCSB::_refASequence[i] != EMPTY_STRING) {
    r0.push_back(RCSB::_refASequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authASequence[i] != EMPTY_STRING) {
    t0.push_back(RCSB::_authASequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT1Sequence[i] != EMPTY_STRING) {
    t1.push_back(RCSB::_authAT1Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT2Sequence[i] != EMPTY_STRING) {
    t2.push_back(RCSB::_authAT2Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT3Sequence[i] != EMPTY_STRING) {
    t3.push_back(RCSB::_authAT3Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT4Sequence[i] != EMPTY_STRING) {
    t4.push_back(RCSB::_authAT4Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT5Sequence[i] != EMPTY_STRING) {
    t5.push_back(RCSB::_authAT5Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT6Sequence[i] != EMPTY_STRING) {
    t6.push_back(RCSB::_authAT6Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT7Sequence[i] != EMPTY_STRING) {
    t7.push_back(RCSB::_authAT7Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT8Sequence[i] != EMPTY_STRING) {
    t8.push_back(RCSB::_authAT8Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT9Sequence[i] != EMPTY_STRING) {
    t9.push_back(RCSB::_authAT9Sequence[i]);
    i++;
  };    

  i=0;
  while (RCSB::_authAT10Sequence[i] != EMPTY_STRING) {
    t10.push_back(RCSB::_authAT10Sequence[i]);
    i++;
  };    


  PairwiseAlign pAC=PairwiseAlign();
  pAC.setReferenceSequence(r0,"REFA");
  pAC.addTestSequence(t0, "AUTH0");
  pAC.addTestSequence(t1, "AUTH1");
  pAC.addTestSequence(t2, "AUTH2");
  pAC.addTestSequence(t3, "AUTH3");
  pAC.addTestSequence(t4, "AUTH4");
  pAC.addTestSequence(t5, "AUTH5");
  pAC.addTestSequence(t6, "AUTH6");
  pAC.addTestSequence(t7, "AUTH7");
  pAC.addTestSequence(t8, "AUTH8");
  pAC.addTestSequence(t9, "AUTH9");
  pAC.addTestSequence(t10,"AUTH10");

  //
  pAC.doAlignConsensus();
  pAC.wrAlignmentFull(std::cout);
  //


  return 0;
}

