# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                          ErrorHandling Module - Classes and Functions                                                    %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Collection of custom errors and exceptions.
 
@note: PyXMake module                   
Created on 20.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.Tools.ErrorHandling
# Error handling module.
## @author 
# Marc Garbade
## @date
# 20.03.2018
## @par Notes/Changes
# - Added documentation // mg 29.03.2018
try:
    from builtins import Exception
except ImportError:
    pass
from ..Tools import  Utility

## @class PyXMake.Tools.ErrorHandling.Error
# Parent class inherited from built-in exception.
class Error(Exception, Utility.AbstractBase): # pragma: no cover
    """
    Base class for all exceptions in this module.
    """
    pass

## @class PyXMake.Tools.ErrorHandling.InputError
# Base class for all input errors. Inherited from Error.
class InputError(Error): # pragma: no cover
    """
    Exception raised for errors in the input.

    Attributes:
    Expression -- Input expression in which the error occurred
    """
    def __init__(self, Expression):
        """
        Low-level initialization of input error class.
        """        
        ## Input expression in which the error occurred. This is the internal error code.
        self.Expression = Expression
        
        # Errors associated with the make module.
        if self.Expression == 0:
            raise InputError('The temporary input file does not end with *cpd.')
        if self.Expression == 1:
            raise InputError('Material dictionary is not given. Please define a material.')        
        if self.Expression == 2:
            raise InputError('Skin list is empty. Please define the skin geometry of the panel.')
        if self.Expression == 3:
            raise NameError('Unknown mesh classification flag. Valid flags are: Structured, Unstructured or Hybrid.')  
        if self.Expression == 4:
            raise InputError('MeshImplementation list is empty. Please define the mesh discretization.')
        if self.Expression == 5:
            raise InputError('No impact points are given.')         
        if self.Expression == 6:
            raise InputError('An unknown boundary condition is defined. Valid flags are: ENCASTRE or PINNED.')               
        if self.Expression == 7:
            raise NameError('Unknown API. Only Abaqus, Salome and Gmsh can be used for mesh generation.')  
        
        # Errors associated with the build module. 
        if self.Expression == 10:
            raise NameError('Unknown Solver. Only Abaqus, Calculix and Marc are supported. Please use a different solver.')       
        
        # Errors associated with the VTL module. 
        if self.Expression == 20:
            raise NameError('Import Error. Function is executed as a plug-in, but cannot load a required dependency')     
        if self.Expression == 21:
            raise NameError('Import Error. Mismatch between source code uploaded and requested. Please check content of your input.')                                            

## @class PyXMake.Tools.ErrorHandling.TransitionError
# Base class for all transition errors. Inherited from Error.
class TransitionError(Error): # pragma: no cover
    """
    Raised when an operation attempts a state transition that's not allowed.

    Attributes:
    Previous -- State at beginning of transition
    Following -- Attempted new state
    Message -- Explanation of why the specific transition is not allowed
    """
    def __init__(self, Previous, Following, Message):
        """
        Low-level initialization of transition error class.
        """                
        ## State at beginning of transition.
        self.Previous = Previous
        ## Attempted new state.
        self.Following = Following
        ## Explanation of why the specific transition is not allowed.
        self.Message = Message

if __name__ == '__main__':
    pass        