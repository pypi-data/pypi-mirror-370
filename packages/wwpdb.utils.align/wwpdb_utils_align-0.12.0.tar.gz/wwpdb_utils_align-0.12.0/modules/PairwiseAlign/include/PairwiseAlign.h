/** @file PairwiseAlign.h
 *
 *   File:  PairwiseAlign.h
 *   Date:  Dec 24, 2009 JDW
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
 */

#ifndef PAIRWISEALIGN_H
#define PAIRWISEALIGN_H

#include <string>
#include <ostream>
#include <list>
#include <vector>
#include <map>
#include <utility>

#define SCORE_FUNCT _score

namespace RCSB {

  class PairwiseAlign {

    typedef struct {
      int  m,  n;
      int  pp;
    } SAVE;
    
    typedef struct {
      double val;
      int    ptr;
    } RECD;
    
  private:
    double _gapPenalty;
    std::string  _gapSymbol;
    bool _verbose;
    std::map<std::string, std::string> _a1_a3_mapping;


    std::vector<std::string> _seqRef;            // starting  reference sequence
    std::vector<std::string> _seqRefConsensus;   // consensus reference sequence -- used in calculation!
    std::string _idRef;                          // identifier for reference sequence

    std::vector<std::string> _seqTest;     // current test sequence
    std::vector<std::string> _idTestList; // list of test sequence identifiers


    std::map<std::string, std::vector<std::string> >  _seqTestMap;
    std::map<std::string, std::vector<bool> > _linkageTestMap;
    std::map<std::string, std::pair<unsigned int, unsigned int> > _rangeTestMap;
    std::map<std::string, std::vector<std::string> >  _seqRefMap;
    std::map<std::string, std::vector< std::pair<std::string, std::string> > >  _alignmentMap;

    void _init();
    void _reset();

    void _get_sequence_array(std::vector<std::string> &seqs, const std::string &sequence);
    int  _score(const int k, const int l);

    int _dynamic(const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb, const double& vv,
                 const double& uu, std::vector<SAVE>& dr, const std::vector<bool>& linkage);
    void _mu_trcback(const int& origin, std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& a,
                     const std::vector<std::vector<int> >& b, const std::vector<SAVE>& dr);
    void _track(std::vector<std::vector<int> >& aa, std::list<std::pair<int, int> >& top,
                const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb);
    int _adr(const int& m, const int& n, const int& pp, std::vector<SAVE>& dr);

    void _alignmentQ(std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& sa,
                     const std::vector<std::vector<int> >& sb, const std::vector<bool>& linkage);
/*
    void _alignment(std::vector<std::pair<std::string, std::string> > & align_pair,
		   const std::vector<std::string> & seq_a, const std::vector<std::string> & seq_b,
                   const std::vector<bool>& linkage);
*/
    void _alignment(std::vector<std::pair<std::string, std::string> >& align_pair, const std::vector<std::string> &seq_a,
                    const std::vector<std::string> &seq_b, const std::vector<bool>& linkage,
                    const unsigned int& begin_orig = 0, const unsigned int& end_orig = 0);
    std::vector<std::vector<std::string> > _multiple_alignment(const std::vector<std::vector<std::string> >& ss_in, const std::vector<std::string>& seq_b,
                                                 const std::vector<bool>& linkage, const unsigned int& begin_orig = 0, const unsigned int& end_orig = 0);
    unsigned int _getConsensusSeq(std::vector<std::vector<int> >& sa, const std::vector<std::vector<std::string> >& ss_in,
                                  const unsigned int& begin_orig, const unsigned int& end_orig, const unsigned int& extra);
    void _extractSequence(const std::string & type, const std::string & seqName, std::vector<std::string> & seqV  );
    bool _compareSequence(const std::vector<std::string> &seqVa, const std::vector<std::string> &seqVb);
  public:
    PairwiseAlign();
    ~PairwiseAlign() {
      _reset();
    }
    void clear();
    void setVerbose(bool verbose);
    void setReferenceSequence(const std::vector<std::string> & sR, const std::string & seqName);
    unsigned int addTestSequence(const std::vector<std::string> & sR, const std::string & seqName);

    unsigned int addTestSequenceWithLink(const std::vector<std::string> & sR, const std::string & seqName,
					 const std::vector<int>& linkage = std::vector<int>());

    unsigned int addTestSequenceWithLinkAndRange(const std::vector<std::string> & sR, const std::string & seqName,
					         const std::vector<int>& linkage = std::vector<int>(),
                                                 const int& begin = 0, const int& end = 0);

    std::vector<std::pair<std::string, std::string> > getAlignment(const std::string & seqName);

    void prAlignment(const std::string & seqName);
    void wrAlignment(std::ostream & io, const std::string & seqName);


    void prAlignmentConflicts(const std::string & seqName);
    void wrAlignmentConflicts(std::ostream & io, const std::string & seqName);

    void prAlignmentFull();
    void wrAlignmentFull(std::ostream & io);

    void doAlign();
    void testExample(void);
    std::vector<std::string> doAlignConsensus();
    std::vector<std::string> doMultipleAlign();
    unsigned int countGaps(const std::vector<std::string> &seq);
  };

}   

#endif
