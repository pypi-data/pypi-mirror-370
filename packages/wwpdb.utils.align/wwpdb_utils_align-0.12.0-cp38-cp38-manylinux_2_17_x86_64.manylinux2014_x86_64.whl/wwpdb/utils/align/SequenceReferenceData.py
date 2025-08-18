"""
File:  SequenceReferenceData.py
Date:  22-Dec-2009
Version: .001 jdw
 Sequence reference data -f

"""


class SequenceReferenceData(object):
    """This class contains reference data for identifying standard polymer types and
    mapping residue nomenclature.
    """

    _polymerEntityTypes = [
        "polypeptide(D)",
        "polypeptide(L)",
        "polydeoxyribonucleotide",
        "polyribonucleotide",
        "polysaccharide(D)",
        "polysaccharide(L)",
        "polydeoxyribonucleotide/polyribonucleotide hybrid",
        "cyclic-pseudo-peptide",
        "other",
    ]

    _entityTypes = ["polymer", "non-polymer", "macrolide", "water"]

    _monDict3 = {
        "ALA": "A",
        "ARG": "R",
        "ASN": "N",
        "ASP": "D",
        "ASX": "B",
        "CYS": "C",
        "GLN": "Q",
        "GLU": "E",
        "GLX": "Z",
        "GLY": "G",
        "HIS": "H",
        "ILE": "I",
        "LEU": "L",
        "LYS": "K",
        "MET": "M",
        "PHE": "F",
        "PRO": "P",
        "SER": "S",
        "THR": "T",
        "TRP": "W",
        "TYR": "Y",
        "VAL": "V",
        "DA": "A",
        "DC": "C",
        "DG": "G",
        "DT": "T",
        "DU": "U",
        "DI": "I",
        "A": "A",
        "C": "C",
        "G": "G",
        "I": "I",
        "T": "T",
        "U": "U",
        "UNK": "X",
    }

    _monDict1 = {
        "A": "ALA",
        "R": "ARG",
        "N": "ASN",
        "D": "ASP",
        "B": "ASX",
        "C": "CYS",
        "Q": "GLN",
        "E": "GLU",
        "Z": "GLX",
        "G": "GLY",
        "H": "HIS",
        "I": "ILE",
        "L": "LEU",
        "K": "LYS",
        "M": "MET",
        "F": "PHE",
        "P": "PRO",
        "S": "SER",
        "T": "THR",
        "W": "TRP",
        "Y": "TYR",
        "V": "VAL",
    }
