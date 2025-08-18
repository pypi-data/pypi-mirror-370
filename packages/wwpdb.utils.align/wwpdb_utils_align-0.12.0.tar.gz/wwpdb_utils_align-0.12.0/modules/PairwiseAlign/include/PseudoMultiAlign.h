/** @file PseudoMultiAlign.h
 *
 *   File:  PseudoMultiAlign.h
 *   Date:  Sep 03, 2018 ZF
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
 *  AlignUtil.h & AlignUtil.C were directly copied from annotation-pack/utillib module.
 *  PseudoMultiAlign is the modified verion of PseudoMultiAlign class from annotation-pack/utillib module.
 *
 */

#ifndef _H_PSEUDO_MULTI_ALIGN_H_
#define _H_PSEUDO_MULTI_ALIGN_H_

#include <string>
#include <vector>

namespace RCSB {

class PseudoMultiAlign
{
   public:
       PseudoMultiAlign();
       ~PseudoMultiAlign();
       void clear();
       void setPenaltyFactor(const double& value);
       void setRefScore();
       void setAuthScore();
       void setAuthSequence(const std::vector<std::vector<std::string> >& seqs);
       void addAlignSequence(const std::vector<std::vector<std::string> >& seqs);
       void addAlignSequenceWithRange(const std::vector<std::vector<std::string> >& seqs, const unsigned int& begin = 0, const unsigned int& end = 0);
       void addAlignSequenceWithLinkageAndRange(const std::vector<std::vector<std::string> >& seqs, const std::vector<int>& linkage = std::vector<int>(),
                                                const unsigned int& begin = 0, const unsigned int& end = 0);
       std::vector<std::vector<int> > getAlignIndices();
       std::vector<std::vector<std::string> > getAlignSequences();

   private:
       double _factor, _uu, _vv;
       double (*_sfunc)(const int& i, const int& j, void* data);
       std::vector<std::string> _authSeq;
       std::vector<std::vector<int> > _internal_align_indices, _public_align_indices;
       std::vector<std::vector<std::string> > _align_sequences;

       void _get_seq_index_linkage_info(const std::vector<std::vector<std::string> >& input_seqs, std::vector<std::string>& output_seqs,
                                        std::vector<int>& auth_indices, std::vector<int>& embed_linkage, std::vector<int>& relative_numbering);
       void _multiple_alignment(const std::vector<std::string>& seqs, const std::vector<int>& auth_indices, const std::vector<int>& linkage,
                                const std::vector<int>& relative_numbering, const unsigned int& begin_orig = 0, const unsigned int& end_orig = 0);
       unsigned int _getConsensusSeq(std::vector<std::string>& seqs, const unsigned int& begin_orig, const unsigned int& end_orig,
                                     const unsigned int& extra);
       void _check_alignment(void* data, const std::vector<int>& relative_numbering, std::vector<std::vector<int> >& ss);
       bool _find_match_list(void* data, const std::vector<int>& relative_numbering, const std::vector<std::vector<int> >& ss,
                             const std::vector<int>& block_range, const std::vector<int>& loop_range, const std::vector<int>& prev_block,
                             const std::vector<int>& next_block, std::vector<int>& match_list);
};

}   

#endif
