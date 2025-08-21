import numpy
import numpy.typing
import typing

class BasisFunc:
    c: float
    identifier: int
    m: int
    numC: int
    x0: float
    z0: float
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def H(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], d: typing.SupportsInt, full: bool) -> numpy.typing.NDArray[numpy.float64]:
        """H(self: BF.BasisFunc, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], d: typing.SupportsInt, full: bool) -> numpy.typing.NDArray[numpy.float64]


                        Compute basis function matrix.

                        Parameters:
                        x: Points (1D numpy array)
                        d: Derivative order
                        full: Whether to return full matrix (not removing nC columns)

                        Returns:
                        mOut x nOut NumPy array.
            
        """
    @property
    def xlaCapsule(self) -> object:
        """(arg0: BF.BasisFunc) -> object"""
    @property
    def xlaGpuCapsule(self) -> str:
        """(arg0: BF.BasisFunc) -> str"""

class CP(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.CP, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class ELM(BasisFunc):
    b: numpy.typing.NDArray[numpy.float64]
    w: numpy.typing.NDArray[numpy.float64]
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""

class ELMReLU(ELM):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.ELMReLU, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class ELMSigmoid(ELM):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.ELMSigmoid, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class ELMSin(ELM):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.ELMSin, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class ELMSwish(ELM):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.ELMSwish, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class ELMTanh(ELM):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.ELMTanh, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class FS(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.FS, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class HoPphy(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.HoPphy, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class HoPpro(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.HoPpro, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class LaP(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.LaP, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class LeP(BasisFunc):
    def __init__(self, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.LeP, x0: typing.SupportsFloat, xf: typing.SupportsFloat, nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nBasisFunc(BasisFunc):
    c: numpy.typing.NDArray[numpy.float64]
    dim: int
    numBasisFunc: int
    numBasisFuncFull: int
    z0: float
    zf: float
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def H(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], d: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], full: bool) -> numpy.typing.NDArray[numpy.float64]:
        """H(self: BF.nBasisFunc, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], d: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], full: bool) -> numpy.typing.NDArray[numpy.float64]


                        Compute basis function matrix.

                        Parameters:
                        x: Points (1D numpy array)
                        d: Derivative order
                        full: Whether to return full matrix (not removing nC columns)

                        Returns:
                        mOut x nOut NumPy array.
            
        """

class nCP(nBasisFunc):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nCP, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (2D numpy array)
                    min: Number of basis functions to use
        
        """

class nELM(nBasisFunc):
    b: numpy.typing.NDArray[numpy.float64]
    w: numpy.typing.NDArray[numpy.float64]
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""

class nELMReLU(nELM):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nELMReLU, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain (1D numpy array)
                    xf: End of domain (1D numpy array)
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nELMSigmoid(nELM):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nELMSigmoid, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain (1D numpy array)
                    xf: End of domain (1D numpy array)
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nELMSin(nELM):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nELMSin, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain (1D numpy array)
                    xf: End of domain (1D numpy array)
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nELMSwish(nELM):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nELMSwish, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain (1D numpy array)
                    xf: End of domain (1D numpy array)
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nELMTanh(nELM):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nELMTanh, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain (1D numpy array)
                    xf: End of domain (1D numpy array)
                    nC: Array of indices to remove (1D numpy array)
                    min: Number of basis functions to use
        
        """

class nFS(nBasisFunc):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nFS, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (2D numpy array)
                    min: Number of basis functions to use
        
        """

class nLeP(nBasisFunc):
    def __init__(self, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None:
        """__init__(self: BF.nLeP, x0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xf: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], nC: typing.Annotated[numpy.typing.ArrayLike, numpy.int32], min: typing.SupportsInt) -> None


                    Constructor.

                    Parameters:
                    x0: Start of domain
                    xf: End of domain
                    nC: Array of indices to remove (2D numpy array)
                    min: Number of basis functions to use
        
        """
