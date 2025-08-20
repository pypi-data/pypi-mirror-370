import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import imp
import networkx as nx
import numpy as np

from rdkit import Chem
from rdkit.Chem import Descriptors, rdFMCS
from rdkit.DataStructs import TanimotoSimilarity
from rdkit.Chem import rdFingerprintGenerator
import rdkit.Chem.QED as QED

import coma.sascorer as sascorer


def get_kekuleSmiles(smi):
    mol = Chem.MolFromSmiles(smi)
    smi_rdkit = Chem.MolToSmiles(
                    mol,
                    isomericSmiles=False,   # modified because this option allows special tokens (e.g. [125I])
                    kekuleSmiles=True,      # modified for downstream analysis with rdkit
                    rootedAtAtom=-1,        # default
                    canonical=True,         # default
                    allBondsExplicit=False, # default
                    allHsExplicit=False     # default
                )
    return smi_rdkit


def rdkit_kekulize_handling(original_fn):
    def wrapper_fn(*args, **kwargs):
        try:
            score = original_fn(*args, **kwargs)
        except Chem.rdchem.KekulizeException:
            score = 0.
        finally:
            return score
    return wrapper_fn


@rdkit_kekulize_handling
def qed(s):
    if s is None:
        return 0.
    else:
        try:
            mol = Chem.MolFromSmiles(s)
            if mol is None:
                return 0.
            else:
                return QED.qed(mol)
        except:
            return 0.


# Modified from https://github.com/bowenliu16/rl_graph_generation
def penalized_logp(s):
    if s is None: return -100.0
    mol = Chem.MolFromSmiles(s)
    if mol is None: return -100.0

    logP_mean = 2.4570953396190123
    logP_std = 1.434324401111988
    SA_mean = -3.0525811293166134
    SA_std = 0.8335207024513095
    cycle_mean = -0.0485696876403053
    cycle_std = 0.2860212110245455

    ## logp
    log_p = Descriptors.MolLogP(mol)
    ## synthetic accessiblity
    SA = -sascorer.calculateScore(mol)
    ## cycle score
    cycle_list = nx.cycle_basis(nx.Graph(Chem.rdmolops.GetAdjacencyMatrix(mol)))
    cycle_length = max([len(j) for j in cycle_list]) if len(cycle_list) > 0 else 0
    cycle_score = min(0, 6 - cycle_length)

    normalized_log_p = (log_p - logP_mean) / logP_std
    normalized_SA = (SA - SA_mean) / SA_std
    normalized_cycle = (cycle_score - cycle_mean) / cycle_std
    return normalized_log_p + normalized_SA + normalized_cycle


def similarity(a, b):
    if a is None or b is None: 
        return 0.0
    amol = Chem.MolFromSmiles(a)
    bmol = Chem.MolFromSmiles(b)
    if amol is None or bmol is None:
        return 0.0
    else:
        mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=False)
        fp1 = mfpgen.GetFingerprint(amol)
        fp2 = mfpgen.GetFingerprint(bmol)
        return TanimotoSimilarity(fp1, fp2) 


def mcs_similarity(a, b):
    if a is None or b is None: 
        return 0.0
    amol = Chem.MolFromSmiles(a)
    bmol = Chem.MolFromSmiles(b)
    if amol is None or bmol is None:
        return 0.0
    else:
        mcs = rdFMCS.FindMCS([amol, bmol], completeRingsOnly=True)
        sim_atom = 2 * mcs.numAtoms / (amol.GetNumAtoms() + bmol.GetNumAtoms())
        sim_bond = 2 * mcs.numBonds / (amol.GetNumBonds() + bmol.GetNumBonds())
        return 0.5 * (sim_atom + sim_bond)


class FastTanimotoOneToBulk:
    def __init__(self, bs):
        self.bs = bs
        self.mfpgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=False)
        self.b_fps = np.vstack([self._fingerprints_from_smi(smi) for smi in self.bs])
        
    def __call__(self, a):
        a_fp = self._fingerprints_from_smi(a)
        return (a_fp&self.b_fps).sum(axis=1) / (a_fp|self.b_fps).sum(axis=1)
        
    def _fingerprints_from_smi(self, smi):
        mol = Chem.MolFromSmiles(smi)
        #fp = self.mfpgen.GetFingerprint(mol)
        #nfp = np.array([b=='1' for b in fp.ToBitString()])
        nfp = self.mfpgen.GetFingerprintAsNumPy(mol).astype(bool)
        return nfp


if __name__ == "__main__":
    ex = 'COC1=NOC(C(=O)NC2=CC=CC=C2OC2=CC=CC=C2)=C1'
    print(qed(ex))
    print(penalized_logp(ex))
    
    bulks = ['COC1=CC=C(Br)C=C1NC(=O)C1=CC(C(C)C)=NO1',
             'COC1=CC=CC=C1NC(=O)C1=NOC(C(C)C)=C1',
             'O=C(CN1C(=O)C(=CC2=CC=CO2)SC1=S)NCCC1=CNC2=CC=CC=C12',
             'CC1=CC=C(CN(C)CN2C(=O)NC3(CCCCC3C)C2=O)C=C1',
             'O=C(NC1CC1)C1CCN(C2=NC=CC=N2)CC1',
             'CC(=O)C1=CC=C(OCC(=O)N2CCN(C3=CC=CC=C3F)CC2)C=C1',
             'O=C(CSC1=NC=CN1C1CC1)N1CCN(C2=CC=CC(C(F)(F)F)=C2)CC1']
    
    max_sim = 0.
    for b in bulks:
        max_sim = max(max_sim, similarity(ex, b))
    print(max_sim)
    
    for sim in FastTanimotoOneToBulk(bulks)(ex):
        print(sim)
