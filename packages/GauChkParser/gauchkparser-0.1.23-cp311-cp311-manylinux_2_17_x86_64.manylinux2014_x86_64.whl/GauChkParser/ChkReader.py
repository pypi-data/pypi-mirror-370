from GauChkParser_ import ChkReader_
from GauChkParser.Types import ChkParams 
from typing import List


class ChkReader:
    """ A class for reading .chk file generaged by Gaussian 09/16 x64 version """
    def __init__(self, fname:str):
        self.fname = fname
        self.__chk = ChkReader_(self.fname)

    @property
    def params(self) -> ChkParams:
        """ Return ChkParams dataclass """
        return self.__chk.params
    
    @property
    def ilsw(self) -> List[int]:
        """ Return ILSW array (size=100) """
        return self.__chk.ilsw
    
    @property
    def rlsw(self) -> List[float]:
        """ Return RLSW array (size=ilsw[57]) """
        return self.__chk.rlsw

    def write_gjf(self, fname:str):
        """ Write a gjf file based on the information of .chk

        Args:
            fname: the output gjf file name
        """
        self.__chk.write_gjf(fname)

    def write_fchk(self, fname:str):
        """ Write a formatted checkpoint file based on the partial information of .chk

        Note:
            The generated .fchk file is not as complete as one created using `formchk`.
            However, it contains enough information to be used by [Multiwfn](http://sobereva.com/multiwfn).

        Args:
            fname: the output fchk file name
        """
        self.__chk.write_fchk(fname)
