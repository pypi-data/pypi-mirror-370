#!/usr/bin/env python
# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Custom input filter script for Doxygen                                                %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Input filter script for Doxygen to replace any lines before the first docstring with 
blanks. This is a mandatory preprocessing step for Python files documented with 
Doxygen. These lines can contain encoding information and/or preset commands 
initializing the python environment, which are not handled correctly by Doxygen.

@note: PyXMake input filter script.
Created on 28.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @namespace PyXMake.Build.config
# Configuration files for PyXMake, containing primarily Doxygen files.
## @author 
# Marc Garbade
## @date
# 30.04.2020
## @par Notes/Changes
# - Added documentation // mg 30.04.2020

## @package PyXMake.Build.config.stm_pyfilter
# Input filter script for Python files processed with Doxygen.
## @author 
# Marc Garbade
## @date
# 28.03.2018
## @par Notes/Changes
# - Added documentation // mg 29.03.2018

import sys

## File to be processed
filename = sys.argv[1]
## Output location for data stream
outfile = sys.stdout 
## Flag whether the initial docstring has been found or not.
InitialDocString = False

with open(filename, encoding="utf-8") as cfile:
        for line in cfile:          
            if line[:3] == '"""' or line[:3] == "'''":
                InitialDocString = True
            if not InitialDocString:
                outfile.write(" "+"\n")  
            else:        
                outfile.write(line)