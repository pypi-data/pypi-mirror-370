/** @file PseudoMultiAlign.C
 *
 *   File:  PseudoMultiAlign.C
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

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <iostream>
#include <iomanip>

#include "AlignUtil.h"
#include "PseudoMultiAlign.h"

#define VV  2
#define UU  1

using namespace RCSB;

typedef struct {
        std::vector<std::string> seqa;
        std::vector<std::string> seqb;
} _DataContainer;

static std::string gapSymbol = ".";

static double coord_score(const int& i, const int& j, void* data);
static double ref_score(const int& i, const int& j, void* data);
static double auth_score(const int& i, const int& j, void* data);

PseudoMultiAlign::PseudoMultiAlign()
{
       clear();
}

PseudoMultiAlign::~PseudoMultiAlign()
{
       clear();
}

void PseudoMultiAlign::clear()
{
       _factor = 10;
       _uu = 0;
       _vv = VV;
       _sfunc = &coord_score;
       _authSeq.clear();
       _internal_align_indices.clear();
       _public_align_indices.clear();
       _align_sequences.clear();
}

void PseudoMultiAlign::setPenaltyFactor(const double& value)
{
       _factor = value;
}

void PseudoMultiAlign::setRefScore()
{
       _uu = UU;
       _vv = VV;
       _sfunc = &ref_score;
}

void PseudoMultiAlign::setAuthScore()
{
       _uu = 0;
       _vv = 0;
       _sfunc = &auth_score;
}

void PseudoMultiAlign::setAuthSequence(const std::vector<std::vector<std::string> >& seqs)
{
       std::vector<int> index, auth_indices, embed_linkage, relative_numbering;
       std::vector<std::string> seqList;
       _get_seq_index_linkage_info(seqs, _authSeq, auth_indices, embed_linkage, relative_numbering);

       index.clear(); index.push_back(0);
       seqList.clear(); seqList.push_back(gapSymbol);

       for (unsigned int i = 0; i < _authSeq.size(); ++i) {
            index[0] = i;
            _internal_align_indices.push_back(index);

            index[0] = auth_indices[i];
            _public_align_indices.push_back(index);

            seqList[0] = _authSeq[i];
            _align_sequences.push_back(seqList);
       }
}

void PseudoMultiAlign::addAlignSequence(const std::vector<std::vector<std::string> >& seqs)
{
       std::vector<std::string> embed_seqs;
       std::vector<int> auth_indices, embed_linkage, relative_numbering;
       _get_seq_index_linkage_info(seqs, embed_seqs, auth_indices, embed_linkage, relative_numbering);
       _multiple_alignment(embed_seqs, auth_indices, embed_linkage, relative_numbering);
}

void PseudoMultiAlign::addAlignSequenceWithRange(const std::vector<std::vector<std::string> >& seqs, const unsigned int& begin, const unsigned int& end)
{
       std::vector<std::string> embed_seqs;
       std::vector<int> auth_indices, embed_linkage, relative_numbering;
       _get_seq_index_linkage_info(seqs, embed_seqs, auth_indices, embed_linkage, relative_numbering);
       _multiple_alignment(embed_seqs, auth_indices, embed_linkage, relative_numbering, begin, end);
}

void PseudoMultiAlign::addAlignSequenceWithLinkageAndRange(const std::vector<std::vector<std::string> >& seqs, const std::vector<int>& linkage,
                                                           const unsigned int& begin, const unsigned int& end)
{
       std::vector<std::string> embed_seqs;
       std::vector<int> auth_indices, embed_linkage, relative_numbering;
       _get_seq_index_linkage_info(seqs, embed_seqs, auth_indices, embed_linkage, relative_numbering);
       _multiple_alignment(embed_seqs, auth_indices, embed_linkage, relative_numbering, begin, end);
}

std::vector<std::vector<int> > PseudoMultiAlign::getAlignIndices()
{
       return _public_align_indices;
}

std::vector<std::vector<std::string> > PseudoMultiAlign::getAlignSequences()
{
       return _align_sequences;
}

void PseudoMultiAlign::_get_seq_index_linkage_info(const std::vector<std::vector<std::string> >& input_seqs, std::vector<std::string>& output_seqs,
                                                   std::vector<int>& auth_indices, std::vector<int>& embed_linkage, std::vector<int>& relative_numbering)
{
       std::vector<std::string> pdb_numbering;

       output_seqs.clear();
       auth_indices.clear();
       embed_linkage.clear();
       relative_numbering.clear();
       pdb_numbering.clear();
       for (std::vector<std::vector<std::string> >::const_iterator vpos = input_seqs.begin(); vpos != input_seqs.end(); ++vpos) {
            output_seqs.push_back((*vpos)[0]);
            if (vpos->size() >= 2) auth_indices.push_back(atoi((*vpos)[1].c_str()));
            if (vpos->size() >= 3) embed_linkage.push_back(atoi((*vpos)[2].c_str()));
            if (vpos->size() >= 4) pdb_numbering.push_back((*vpos)[3]);
       }

       if (auth_indices.size() != output_seqs.size()) {
            auth_indices.clear();
            for (unsigned int i = 0; i < output_seqs.size(); ++i) auth_indices.push_back(i);
       }

       if (embed_linkage.size() != output_seqs.size()) embed_linkage.clear();

       if (!pdb_numbering.empty() && (pdb_numbering.size() == output_seqs.size())) {
            int start_number = 0;
            std::string prev_number = "";
            std::string prev_inscode = "";
            for (std::vector<std::string>::const_iterator vpos = pdb_numbering.begin(); vpos != pdb_numbering.end(); ++vpos) {
                 std::string curr_number = *vpos;
                 std::string curr_inscode = "";
                 for (unsigned int i = 0; i < vpos->size(); ++i) {
                      if (isalpha((*vpos)[i])) {
                           curr_number = vpos->substr(0, i);
                           curr_inscode = vpos->substr(i);
                           break;
                      }
                 }
                 if (prev_number.empty()) start_number++;
                 else {
                      if (prev_number == curr_number) {
                           if (!curr_inscode.empty()) {
                                char prev_ins = '@';
                                if (!prev_inscode.empty()) prev_ins = prev_inscode[0];
                                char curr_ins = curr_inscode[0];
                                start_number += abs(int(curr_ins) - int(prev_ins));
                           } else start_number++;
                      } else {
                           start_number += abs(atoi(curr_number.c_str()) - atoi(prev_number.c_str()));
                      }
                 }
                 prev_number = curr_number;
                 prev_inscode = curr_inscode;
                 relative_numbering.push_back(start_number);
            }
       }
} 

void PseudoMultiAlign::_multiple_alignment(const std::vector<std::string>& seqb, const std::vector<int>& auth_indices, const std::vector<int>& linkage,
                                           const std::vector<int>& relative_numbering, const unsigned int& begin_orig, const unsigned int& end_orig)
{
       _DataContainer cdata;
       unsigned int begin = _getConsensusSeq(cdata.seqa, begin_orig, end_orig, 10);
       cdata.seqb = seqb;

       std::vector<std::vector<int> > ss, sa, sb;

       AlignUtil::initAssignment(sa, cdata.seqa.size());
       AlignUtil::initAssignment(sb, cdata.seqb.size());

       AlignUtil::Alignment(ss, sa, sb, _vv, _uu, _sfunc, (void*) &cdata, linkage, _factor);

       if (begin) {
            unsigned int count = 0;
            for (unsigned int i = 0; i < ss.size(); ++i) {
                 if (ss[i][0] >= 0) break;
                 count++;
            }
            if (count) {
                 begin = _getConsensusSeq(cdata.seqa, begin_orig, end_orig, count + 10);
                 AlignUtil::Alignment(ss, sa, sb, _vv, _uu, _sfunc, (void*) &cdata, linkage, _factor);
            }
       }

       _check_alignment((void*) &cdata, relative_numbering, ss);

       std::vector<std::vector<int> > result_internal_align_indices, result_public_align_indices;
       result_internal_align_indices.clear();
       result_internal_align_indices.reserve(begin + ss.size());
       result_public_align_indices.clear();
       result_public_align_indices.reserve(begin + ss.size());

       std::vector<std::vector<std::string> > result_align_sequences;
       result_align_sequences.clear();
       result_align_sequences.reserve(begin + ss.size());

       std::vector<int> index, public_index;
       std::vector<std::string> seq;

       for (unsigned int i = 0; i < begin; ++i) {
            index = _internal_align_indices[i];
            index.push_back(-1);
            result_internal_align_indices.push_back(index);

            public_index = _public_align_indices[i];
            public_index.push_back(-1);
            result_public_align_indices.push_back(public_index);

            seq = _align_sequences[i];
            seq.push_back(gapSymbol);
            result_align_sequences.push_back(seq);
       }


       for (unsigned int i = 0; i < ss.size(); ++i) {
            if (ss[i][0] >= 0) {
                 index = _internal_align_indices[ss[i][0] + begin];
                 public_index = _public_align_indices[ss[i][0] + begin];
                 seq = _align_sequences[ss[i][0] + begin];
                 if (ss[i][1] >= 0) {
                      index.push_back(ss[i][1]);
                      public_index.push_back(auth_indices[ss[i][1]]);
                      seq.push_back(seqb[ss[i][1]]);
                 } else {
                      index.push_back(-1);
                      public_index.push_back(-1);
                      seq.push_back(gapSymbol);
                 }
            } else {
                 index.clear();
                 public_index.clear();
                 seq.clear();
                 for (unsigned int j = 0; j < _internal_align_indices[0].size(); ++j) {
                      index.push_back(-1);
                      public_index.push_back(-1);
                      seq.push_back(gapSymbol);
                 }
                 index.push_back(ss[i][1]);
                 public_index.push_back(auth_indices[ss[i][1]]);
                 seq.push_back(seqb[ss[i][1]]);
            }

            result_internal_align_indices.push_back(index);
            result_public_align_indices.push_back(public_index);
            result_align_sequences.push_back(seq);
       }

       _internal_align_indices = result_internal_align_indices;
       _public_align_indices = result_public_align_indices;
       _align_sequences = result_align_sequences;
}


unsigned int PseudoMultiAlign::_getConsensusSeq(std::vector<std::string>& seqs, const unsigned int& begin_orig, const unsigned int& end_orig,
                                                             const unsigned int& extra)
{
       unsigned int begin = 0;
       if (begin_orig && end_orig) {
            unsigned int start_num = 1;
            if (begin_orig > extra) start_num = begin_orig - extra;

            bool found_begin = false, found_end = false;
            for (unsigned int i = 0; i < _public_align_indices.size(); ++i) {
                 if (_public_align_indices[i][0] == ((int) start_num - 1)) {
                      begin = i;
                      found_begin = true;
                 } else if (_public_align_indices[i][0] == ((int) end_orig - 1)) {
                      found_end = true;
                      if (found_begin) break;
                 }
            }
            if (!found_begin || !found_end) begin = 0;
       }

       seqs.clear();
       seqs.reserve(_align_sequences.size() - begin);

       for (unsigned int i = begin; i < _align_sequences.size(); ++i) {
            std::string res = gapSymbol;
            if (_align_sequences[i][0] != gapSymbol)
                 res = _align_sequences[i][0];
            else {
                 for (unsigned int k = 1; k < _align_sequences[i].size(); ++k) {
                      if (_align_sequences[i][k] != gapSymbol) {
                           res = "-" + _align_sequences[i][k];
                           break;
                      }
                 }
            }
            seqs.push_back(res);
       }

       return begin;
}

void PseudoMultiAlign::_check_alignment(void* data, const std::vector<int>& relative_numbering, std::vector<std::vector<int> >& ss)
{
       if (relative_numbering.empty()) return;

       bool found_missing = false;
       for (std::vector<std::vector<int> >::const_iterator pos = ss.begin(); pos != ss.end(); ++pos) {
            if ((*pos)[0] >= 0 && (*pos)[1] < 0) {
                 found_missing = true;
                 break;
            }
       }
       if (!found_missing) return;

       std::vector<int> tmp_vec;
       tmp_vec.clear();
       for (int i = 0; i < 4; ++i) tmp_vec.push_back(0);

       // vector[0]: 1 for block, 0 for loop
       // vector[1]: length of the range
       // vector[2]: begin index of the range
       // vector[3]: end index of the range
       std::vector<std::vector<int> > block_loop_ranges;
       block_loop_ranges.clear();
       int loop_begin = -1;
       int loop_end = -1;
       int block_begin = -1;
       int block_end = -1;
       for (unsigned int i = 0; i < ss.size(); ++i) {
            if (ss[i][0] < 0) continue;
            if (ss[i][1] < 0) {
                 if (block_begin >= 0) {
                      tmp_vec[0] = 1;
                      tmp_vec[1] = block_end - block_begin + 1;
                      tmp_vec[2] = block_begin;
                      tmp_vec[3] = block_end;
                      block_loop_ranges.push_back(tmp_vec);
                 }
                 block_begin = -1;
                 block_end = -1;
                 if (loop_begin < 0) loop_begin = i;
                 loop_end = i;
            } else {
                 if (loop_begin >= 0) {
                      tmp_vec[0] = 0;
                      tmp_vec[1] = loop_end - loop_begin + 1;
                      tmp_vec[2] = loop_begin;
                      tmp_vec[3] = loop_end;
                      block_loop_ranges.push_back(tmp_vec);
                 }
                 loop_begin = -1;
                 loop_end = -1;
                 if (block_begin < 0) block_begin = i;
                 block_end = i;
            }
       }
       if (block_begin >= 0) {
            tmp_vec[0] = 1;
            tmp_vec[1] = block_end - block_begin + 1;
            tmp_vec[2] = block_begin;
            tmp_vec[3] = block_end;
            block_loop_ranges.push_back(tmp_vec);
       }
       if (loop_begin >= 0) {
            tmp_vec[0] = 1;
            tmp_vec[1] = loop_end - loop_begin + 1;
            tmp_vec[2] = loop_begin;
            tmp_vec[3] = loop_end;
            block_loop_ranges.push_back(tmp_vec);
       }

       std::vector<int> match_list, prev_block, next_block;
       for (unsigned int i = 0; i < block_loop_ranges.size(); ++i) {
            if (!block_loop_ranges[i][0]) continue;

            prev_block.clear();
            if ((i >= 2) && block_loop_ranges[i-2][0]) prev_block = block_loop_ranges[i-2];
            next_block.clear();
            if ((i < (block_loop_ranges.size() - 2)) && block_loop_ranges[i+2][0]) next_block = block_loop_ranges[i+2];
            if (prev_block.empty() && next_block.empty()) continue;

            // check with begore loop range
            if ((i >= 1) && !block_loop_ranges[i-1][0] && (block_loop_ranges[i-1][1] > (block_loop_ranges[i][1] + 1)) &&
                _find_match_list(data, relative_numbering, ss, block_loop_ranges[i], block_loop_ranges[i-1], prev_block, next_block, match_list)) {
                 for (unsigned int j = 0; j < match_list.size(); ++j) {
                      ss[match_list[j]][1] = ss[block_loop_ranges[i][2] + j][1];
                      ss[block_loop_ranges[i][2] + j][1] = -1;
                 }
                 block_loop_ranges[i-1][3] = match_list[0] - 1;
                 block_loop_ranges[i-1][1] = block_loop_ranges[i-1][3] - block_loop_ranges[i-1][2] + 1;
                 block_loop_ranges[i][2] = match_list[0];
                 block_loop_ranges[i][3] = match_list[match_list.size() - 1];
                 if ((i < (block_loop_ranges.size() - 1)) && !block_loop_ranges[i+1][0]) {
                      block_loop_ranges[i+1][2] = match_list[match_list.size() - 1] + 1;
                      block_loop_ranges[i+1][1] = block_loop_ranges[i+1][3] - block_loop_ranges[i+1][2] + 1;
                 }
                 continue;
            }

            // check with after loop range
            if ((i < (block_loop_ranges.size() - 1)) && !block_loop_ranges[i+1][0] && (block_loop_ranges[i+1][1] > (block_loop_ranges[i][1] + 1)) &&
                _find_match_list(data, relative_numbering, ss, block_loop_ranges[i], block_loop_ranges[i+1], prev_block, next_block, match_list)) {
                 for (unsigned int j = 0; j < match_list.size(); ++j) {
                      ss[match_list[j]][1] = ss[block_loop_ranges[i][2] + j][1];
                      ss[block_loop_ranges[i][2] + j][1] = -1;
                 }
                 if ((i >= 1) && !block_loop_ranges[i-1][0]) {
                      block_loop_ranges[i-1][3] = match_list[0] - 1;
                      block_loop_ranges[i-1][1] = block_loop_ranges[i-1][3] - block_loop_ranges[i-1][2] + 1;
                 }
                 block_loop_ranges[i][2] = match_list[0];
                 block_loop_ranges[i][3] = match_list[match_list.size() - 1];
                 block_loop_ranges[i+1][2] = match_list[match_list.size() - 1] + 1;
                 block_loop_ranges[i+1][1] = block_loop_ranges[i+1][3] - block_loop_ranges[i+1][2] + 1;
            }
       }
}

bool PseudoMultiAlign::_find_match_list(void* data, const std::vector<int>& relative_numbering, const std::vector<std::vector<int> >& ss,
                                        const std::vector<int>& block_range, const std::vector<int>& loop_range, const std::vector<int>& prev_block,
                                        const std::vector<int>& next_block, std::vector<int>& match_list)
{
       match_list.clear();

       _DataContainer *cdata = (_DataContainer*) data;

       int diff_value = 0;
       if (!prev_block.empty()) {
            diff_value += abs(abs(relative_numbering[ss[block_range[2]][1]] - relative_numbering[ss[prev_block[3]][1]])
                        - abs(ss[block_range[2]][0] - ss[prev_block[3]][0]));
       }
       if (!next_block.empty()) {
            diff_value += abs(abs(relative_numbering[ss[next_block[2]][1]] - relative_numbering[ss[block_range[3]][1]])
                        - abs(ss[next_block[2]][0] - ss[block_range[3]][0]));
       }

       std::vector<int> tmp_match_list;
       for (int i = loop_range[2] + 1; i <= loop_range[3] - block_range[1]; ++i) {
            tmp_match_list.clear();
            for (int j = 0; j < block_range[1]; ++j) {
                 if (cdata->seqa[ss[block_range[2] + j][0]] == cdata->seqa[ss[i + j][0]]) {
                      tmp_match_list.push_back(i + j);
                 }
            }
            if ((int) tmp_match_list.size() == block_range[1]) {
                 int value = 0;
                 if (!prev_block.empty()) {
                      value += abs(relative_numbering[ss[block_range[2]][1]] - relative_numbering[ss[prev_block[3]][1]])
                             - abs(ss[tmp_match_list[0]][0] - ss[prev_block[3]][0]);
                 }
                 if (!next_block.empty()) {
                      value += abs(relative_numbering[ss[next_block[2]][1]] - relative_numbering[ss[block_range[3]][1]])
                             - abs(ss[next_block[2]][0] - ss[tmp_match_list[tmp_match_list.size()-1]][0]);
                 }
                 if (value < diff_value) {
                      diff_value = value;
                      match_list = tmp_match_list;
                 }
            }
       }
       return !match_list.empty();
}

static double coord_score(const int& i, const int& j, void* data)
{
       _DataContainer *cdata = (_DataContainer*) data;

       bool consensusFlag = false;
       std::string resName = cdata->seqa[i];
       if (resName[0] == '-') {
            resName = cdata->seqa[i].substr(1);
            consensusFlag = true;
       }

       if (resName == gapSymbol) return 0;

       if (resName != cdata->seqb[j])
            return 0;
       else if (consensusFlag) {
            if (resName == "ALA")
                 return 1;
            else return 3;
       } else {
            if (resName == "ALA")
                 return 2;
            else return 5;
       }
}

static double ref_score(const int& i, const int& j, void* data)
{
       _DataContainer *cdata = (_DataContainer*) data;

       bool consensusFlag = false;
       std::string resName = cdata->seqa[i];
       if (resName[0] == '-') {
            resName = cdata->seqa[i].substr(1);
            consensusFlag = true;
       }

       if (resName == gapSymbol) return 0;

       if (resName != cdata->seqb[j]) {
            if ((((resName == "M") || (resName == "MET")) && (cdata->seqb[j] == "MSE")) || 
               ((resName == "MSE") && ((cdata->seqb[j] == "M") || (cdata->seqb[j] == "MET"))))
                 return 5;
            else return 0;
       } else if (consensusFlag) {
            if (resName == "ALA")
                 return 1;
            else return 3;
       } else {
            if (resName == "ALA")
                 return 2;
            else return 5;
       }
}

static double auth_score(const int& i, const int& j, void* data)
{
       _DataContainer *cdata = (_DataContainer*) data;

       bool consensusFlag = false;
       std::string resName = cdata->seqa[i];
       if (resName[0] == '-') {
            resName = cdata->seqa[i].substr(1);
            consensusFlag = true;
       }

       if (resName != cdata->seqb[j]) {
            if ((resName == gapSymbol) || (cdata->seqb[j] == gapSymbol))
                 return (-5);
            else return 0;
       } else if (resName == gapSymbol)
            return 0;
       else if (consensusFlag)
            return 3;
       else return 5;
}
