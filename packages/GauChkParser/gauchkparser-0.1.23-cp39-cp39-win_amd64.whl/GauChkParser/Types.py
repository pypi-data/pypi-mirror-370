from enum import auto, IntEnum, unique
from dataclasses import dataclass, field
import numpy as np
from typing import List 

@unique
class GenDef(IntEnum):
    """ Gen Array index in enum type, such as use genarr[GenDef.VirialRatio] 
    """
    VirialRatio = 0              #: Virial ratio.
    ElecX = auto()               #: X Component of applied electric field
    ElecY = auto()               #: Y Component of applied electric field
    ElecZ = auto()               #: Z Component of applied electric field
    Scf2E = auto()               #: 2e SCF energy
    ScrfGf = auto()              #: SCRF g-factor
    ScrfA0 = auto()              #: SCRF a0
    ThermalEne = auto()          #: Thermal Energy
    ECiCcQciBd = auto()          #: E(CI/CC/QCI/BD)
    Eccd = auto()                #: E(CCD+ST4(CCD)/QCISD(T)/BD(T)/CI+Davidson)
    Evar1 = auto()               #: E(VAR1)
    ZeroPointEne = auto()        #: Zero-point energy
    MultiStepEne = auto()        #: Multi-step (G1, G2, etc.) energy
    NimagFreq = auto()           #: Number of imaginary frequencies.
    Dpuhf = auto()               #: D(PUHF)
    Epuhf = auto()               #: EPUHF
    Ecbs2 = auto()               #: ECBS2
    Ecbsi = auto()               #: ECBSI
    Epmp20 = auto()              #: EPMP2-0
    Epmp30 = auto()              #: EPMP3-0
    Rmsdopt = auto()             #: ROOT-MEAN-SQUARED FORCE OF OPTIMIZED PARAMETERS
    EcisMP2 = auto()             #: E(CIS-MP2)
    RmsError = auto()            #: RMS ERROR IN DENSITY MATRIX
    S2 = auto()                  #: S**2 after annihilation of first contaminant.
    CisEne = auto()              #: CIS energy
    Ump4d = auto()               #: UMP4D (=UMP4DQ - E4(R+Q))
    RefBdEne = auto()            #: Reference energy for BD
    MP5 = auto()                 #: MP5
    S4SD = auto()                #: S4SD, computed in ANNIL in L502, used by PSCF spin projection routines
    ForzenEne = auto()           #: Frozen-core part of total energy
    Tau = auto()                 #: 'TAU' FROM SCFDM
    ScfEne = auto()              #: SCF ENERGY.
    UMP2Ene = auto()             #: UMP2 ENERGY.
    UMP3Ene = auto()             #: UMP3 ENERGY.
    UMP4Ene = auto()             #: UMP4(SDTQ) ENERGY.
    CbsOIii = auto()             #: CBS OIii
    TotEneRF = auto()            #: Total energy with RF from L116
    MP4EDQEne = auto()           #: MP4DQ ENERGY
    MP4SDQEne = auto()           #: MP4SDQ ENERGY
    L116 = auto()                #: Set in L116 for some reason
    NucRepEne = auto()           #: NUCLEAR REPULSION ENERGY
    LenRefDet = auto()           #: T (LENGTH OF CORRECTION OF REFERENCE DETERMINANT)
    UpdateEne = auto()           #: UPDATED ENERGY FOR OPTIMIZATIONS
    S2Scf = auto()               #: <S**2> OF SCF WAVE FUNCTION
    S2FirstOrder = auto()        #: <S**2> CORRECTED TO FIRST ORDER (AFTER DOUBAR)
    S2Doubles = auto()           #: <S**2> CORRECTED FOR DOUBLES (NOT IMPLEMENTED)
    A0 = auto()                  #: A0
    Dummy = auto()               #: Unused in G16
    TempTher = auto()            #: Temperature for thermochemistry
    PressTher = auto()           #: Pressure for thermochemistry
    ScalFactorFreqTher = auto()  #: Scale factor for frequencies in thermochemistry
    NucRep = auto()              #: Nuclear repulsion contribution from inactive atom pairs
    SingE2ToRomp2 = auto()       #: Singles contribution to E2 in ROMP2
    E2 = auto()                  #: E(2) with current orbitals for extrapolation
    NucRF = auto()               #: Nuclear term in the reaction field energy
    ElecRF = auto()              #: Electronic term in the reaction field energy
    CurProFreq = auto()          #: Curvature from projected frequency jobs
    ReacCoord = auto()           #: Reaction coordinate for single-points along IRCs
    FlagExt = auto()             #: Flag for status from external programs; see RunExt
    ScfEneFirstIter = auto()     #: SCF energy at first iteration
    JobStat = auto()             #: Job status, -1 = in progress, 0 = undefined/old chk file, 1 = finished successfully, 2 = step in mult i-step job completed successfully, 3 = job terminated with error
    HighestOrder = auto()        #: Highest order of nuclear coordinate derivatives available
    NIterMostRecSCF = auto()     #: Number of iterations in most recent SCF
    NucRepEneNoExf = 63          #: Nuclear repulsion energy without external field contribution

@unique
class DensDef(IntEnum):
   """ Density matrix definition in enum type, such as use totdens[DensDef.DensSCF], return empty list if not exists
   """
   DensSCF = 0              #: SCF Density
   DensPSI = auto()         #: Psi(1) Density
   DensMP2 = auto()         #: MP2 Density
   DensMP3 = auto()         #: MP3 Density
   DensMP4 = auto()         #: MP4 Density
   DensCIRho = auto()       #: CI Rho(1) Density
   DensCI = auto()          #: CI Density
   DensCC = auto()          #: CC Density
   Dens2ndOrder = auto()    #: 2nd Order Density


@dataclass
class Mol:
    """ A mol dataclass for storing molecule data

    Attributes:
        natoms: number of atoms
        totchg (int): total charge
        ne: number of electrons
        nae: number of alpha electrons
        nbe: number of beta electrons
        nbasis: number of basis functions
        nbsuse: number of independent functions
        ndim: number of translation vectors (0-3 dim)
        multiplicity: multiplicity
        names: atom element name
        coords: atomic coords (N*3), unit is Angstrom
        hessian: hessian matrix (3N*3N)
        gradient: cartesian gradient (N*3 list)
        aoene: alpha orbital energies
        boene: beta orbital energies
        amocoeff: alpha MO coefficients
        bmocoeff: beta MO coefficients
        orthbasis: orthogonal basis
        cell: cell size (3*3) of molecule, unit is Angstrom
        primexp: primitives exponents
        concoeff: contraction coefficients
        spconcoeff: P(S=P) Contraction coefficients
        cshell: Coordinates of each shell, unit is Angstrom
        nucchg: nuclear charges
        shelltypes: shell types
        shellnprim: number of primitives in each shell
        shell2map: shell to map
        orblabels: each atom orbital labels
        totdens: total density matrix, nine types see DensDef, such as Total SCF Density
        spindens: spin density matrix, nine types see DensDef, such as Spin SCF Density
    """
    natoms:         int = 0
    totchg:         int = 0
    ne:             int = 0
    nae:            int = 0
    nbe:            int = 0
    nbasis:         int = 0
    nbsuse:         int = 0
    ndim:           int = 0
    multiplicity:   int = 0
    names:          List[str] = field(default_factory=list)
    atomicnums:     List[int] = field(default_factory=list)
    coords:         np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float64))
    gradient:       List[float] = field(default_factory=list)
    hessian:        np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float64))
    aoene:          List[float] = field(default_factory=list)
    boene:          List[float] = field(default_factory=list)
    amocoeff:       List[float] = field(default_factory=list)
    bmocoeff:       List[float] = field(default_factory=list)
    orthbasis:      List[float] = field(default_factory=list)
    cell:           np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float64))
    primexp:        List[float] = field(default_factory=list)
    concoeff:       List[float] = field(default_factory=list)
    spconcoeff:     List[float] = field(default_factory=list)
    cshell:         np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float64))
    nucchg:         List[float] = field(default_factory=list)
    shelltypes:     List[int] = field(default_factory=list)
    shellnprim:     List[int] = field(default_factory=list)
    shell2map:      List[int] = field(default_factory=list)
    orblabels:      List[str] = field(default_factory=list)
    totdens:        List[List[float]] = field(default_factory=lambda: [[] for _ in range(9)])
    spindens:       List[List[float]] = field(default_factory=lambda: [[] for _ in range(9)])

@dataclass
class ChkParams:
    """ A chk parameters dataclass

    Attributes:
        mol: The mol structure dataclass
        route: The route string
        gauver: The gaussian version description
        title: The title section description
        jobtype: job type, such as SP, Freq, etc.
        method: method, such as RHF, MP4, etc.
        baset: basis set, such as def2SVP, 6-31G, etc
        viratio: virtual ratio
        scfene: scf energy
        totene: total energy
        info1_9: The scalar data of Info1-9, size=9
        genarr: The scalar data of the calculation (Gen array), size=1000
    """
    mol: Mol = field(default_factory=Mol)
    route: str = None
    gauver: str = None
    title: str = None
    jobtype: str = None
    method: str = None
    baset: str = None
    viratio: float = 0  
    scfene: float = 0    
    totene: float = 0   
    info1_9: List[int] = field(default_factory=list)
    genarr: List[float] = field(default_factory=list)

