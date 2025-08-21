# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                 Build script for PyXMake                     %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Build script to create a platfrom and Python independent wheel.
 
@note: PyXMake build script                 
Created on 06.02.2024    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   

@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

import os, sys, site

def build(*args, **kwargs):
    """
    This is the build script used by poetry.
    """
    # Add internal build dependency resolver to current path
    site.addsitedir(site.getusersitepackages())
    # Import build tools
    try: from PyXMake import Command
    except: raise ImportError("Cannot import PyXMake. Skipping compilation")
    # Execute custom build command
    Command.build(*args, exclude_source_files= True, python_tag="py2.py3", **kwargs)
    pass
    
def main(): 
    """
    This is the main entry point.
    """
    return build()
    
if __name__ == "__main__":
    main(); sys.exit() 