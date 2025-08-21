# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                   VTL Module - Classes and Functions                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Module containing virtual testing & benchmark scripts.
 
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

## @package PyXMake.VTL
# Module containing virtual testing & benchmark scripts.
## @author 
# Marc Garbade
## @date
# 18.03.2019
## @par Notes/Changes
# - Added documentation  // mg 18.03.2019
# - Renamed VTC with VTL // mg 04.04.2019

import os, sys, platform
import subprocess
import io
import posixpath
import shlex
import inspect
import tempfile
import argparse
import importlib

from ..Tools import Utility

# Define global path definitions before loading subsequent verification example files.
Scratch = tempfile.gettempdir() if getattr(sys,"frozen",False) or Utility.IsDockerContainer() else os.path.join(os.path.dirname(os.path.abspath(__file__)),"scratch")

## @class PyXMake.VTL.Command
# Parent class inherited from built-in exception.
class Command(object):
    """
    Base class for all CLI commands
    """
    def __init__(self, *args, **kwargs):
        """
        Initialization of Command class object.
        """
        super(Command, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.CommandObjectKind = "PyXMake"
        
    @staticmethod
    def alias(*args, **kwargs):
        """
        Provides an aliases for a given script or command to be used in the CLI instead. 
        """
        # Adding predefined aliases
        alias = {"stm_conda_env":"config","stm_cara_software":"cara","py2x":"f2py","app":"pyinstaller"}
        return alias
        
    @classmethod
    def cli(cls, *args, **kwargs):
        """
        Get a tuple of all valid command line options.
        
        @note: Defaults to dropping all company (DLR) related prefixes from the scripts.
        """
        # Get a dictionary of all aliases
        aliases = {v:k for k,v in cls.alias().items()}
        # Verify that the input is a valid method
        directories = [os.path.dirname(os.path.abspath(__file__)),
                                os.path.abspath(os.path.join(Utility.GetPyXMakePath(),"VTL","cmd",Utility.GetPlatform()))]
        methods = [[path] + os.path.basename(y).split(".") for path in directories for y in os.listdir(path) 
                             if os.path.isfile(os.path.join(path,y)) and not y.startswith(("__","."))  ]
        # Remove all predefined prefixes from the command list except those referred to in aliases.
        methods = [ x for x in methods if not x[1].lower().startswith("stm_") or x[1] in list(aliases.values()) ]
        # Return a dictionary containing all valid choices and methods
        return {"choices":[cls.alias().get(x[1],x[1]) for x in methods], "methods":methods }

    @classmethod
    def typer(cls, **kwargs):
        """
        Main entrypoint of PyXMake CLI using typer. Only available when typer is installed
        """
        try: 
            from typer import Typer as _Command, Argument
            from typer import Context, Exit, Option
            from typing import List, Optional #@UnresolvedImport
            from enum import Enum
        except ImportError: pass
        
        try:
            # Collect all available options
            options = cls.cli()
            # Create modern entrypoint using typer
            app = _Command(help=cls.__help__["main"], context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)

            # Create a function to return the current version
            def __version_callback(value):
                # type: (bool) -> None
                """
                Callback function to return the current version
                """
                # Only return value is requested. False by default
                if value:
                    print(cls.__help__["version"])
                    raise Exit()
                pass
        
            # Modified entrypoint for typer interface
            @app.callback()
            def common(ctx,version = Option(None, "--version", "-v", help=cls.__help__["info"], callback=__version_callback, is_eager=True)):
                # Parse command line directly to underlying procedure. Ignore typer in that case 
                if (sum(x in sys.argv for x in set(["run"]+options["choices"])) >= 2): raise RuntimeError

            # Entrypoint to return local system and version information
            @app.command("info",help=cls.__help__["info"])
            def info(): 
                """
                Return local system information
                """
                return __version_callback(True)

            @app.command("run",help=cls.__help__["run"])            
            def run( namespace = Argument(None, metavar="command",case_sensitive=False, help = cls.__help__["method"]) ):
                """
                Return all available runtime options
                """
                Command.run(namespace=str(str(namespace.value).lower()), **options)

            # Version syntax agnostic way to set annotations
            common.__annotations__ = {'ctx': Context, 'version': Optional[bool], 'return': None}
            run.__annotations__ = {'namespace': Enum("MethodObjectKind", {x:x for x in options["choices"]}), 'return': None}
                
            # Modern interface using typer. Overwrite legacy method. Allowed to fail
            return app()
        
        # To not use blank error here (detects a wrong exception state)
        except Exception as _: raise RuntimeError
        pass
    
    @classmethod
    def parse(cls, command, config, args):
        """
        Parse user-supplied TOML file if given and add its arguments to a CLI command.
        """
        # Initial empty command and default delimn
        parsed_command = ""; parsed_data = {}; delimn = " ";
        # Verify that the given method is a valid identifier. Take potential aliases into account
        try: method = next(iter(key for key, value in cls.alias().items() if args.method[0] in value))
        except StopIteration: method = args.method[0]
        # Check if a TOML configuration can be found and no additional CLI commands are given.
        if config and args.method[-1].lower() not in ["-h","--help"] and any(method in Utility.PathLeaf(x) for x in command.split(delimn)):
            print("==================================")
            print("Processing info from %s" % config)
            print("==================================")
            # Required local imports for this method.
            import tomlkit
            import json
            # Collect all info from the TOML file.
            data = tomlkit.parse(open(config).read())["tool"]
            # Get current class instance programmatically
            base = cls().CommandObjectKind
            # Support naming convention in TOML files. Abbreviations for settings should be collected under PyXMake.
            if data.get(base.lower(),{}): data = data[base.lower()].get(args.method[0],{})
            else: data = {}
            # This only happens when PyXMake is not part of the tools dictionary or the method follows the unconventional development scheme.
            if not data: data = tomlkit.parse(open(config).read())["tool"].get(args.method[0],{})
            # Create a list from the command
            command = command.split(delimn)
            # Get index of executable
            index = [n for n, x in enumerate(command, 1) if method in x][0]
            # Complex dictionary might be parsed as a list of single dictionaries. Catch this case.
            for key, value in data.items():
                # Only meaningful when value is a list.
                if isinstance(value,list): 
                    try: 
                        parsed_dict = {}
                        # Check if the dictionary can be merged into one. Required for PyXMake supported methods.
                        for x in value: parsed_dict.update(x)
                        parsed_data[key] = parsed_dict
                        # Continue with next key if successful
                        continue
                    # Fail gracefully
                    except: pass
                # The value is either not a list or not a list of dictionaries. 
                parsed_data[key] = value
            # Loop over all entries and add its values to the CLI command.
            for key, value in parsed_data.items():
                try:
                    # Check if value is a PATH object. Verify compatibility.
                    if os.path.isdir(os.path.normpath(value)) or os.path.isfile(os.path.normpath(value)): 
                        value = os.path.normpath(value)
                # Fail gracefully.
                except: pass
                # Add a new named argument to the CLI command.
                parsed_command += " --%s " % str(key)
                if isinstance(value, str):  parsed_command += "%s" % str(value)
                if isinstance(value, list): parsed_command += delimn.join(["'%s'" % x for x in value])
                if isinstance(value, dict): parsed_command += "'%s'" % json.dumps(value)
            # User input takes precedence, thus parsed settings have to be put in between.
            command.insert(index,parsed_command)
            # Reassemble command
            command = delimn.join(command)
        # Return the command
        return command
    
    @classmethod
    def verify(cls, selection, **kwargs):
        """
        Return command script if verified.
        """
        # Check if an alias is used as a selection identifier.
        aliases = kwargs.get("aliases",{v:k for k, v in cls.alias().items()})
        # If methods are not given, execute CLI script and get the last elements
        methods = kwargs.get("methods",cls.cli()["methods"])
        # Get valid alias for selection if exits. Defaults to proceed with selection.
        identifier = aliases.get(selection,selection)
        found = [str(identifier) in x if len(x) == len(str(identifier)) else False for x in list(zip(*methods))[1]]
        # Unknown option
        if not any(found): raise ValueError("Unknown CLI option %s" % str(selection))
        # Obtain the correct file extension
        path,method,ext = [methods[i] for i,x in enumerate(found) if x][0]
        # This is the command script
        script = os.path.join(path,".".join([str(method),ext]))
        # Return command line script
        return script
    
    @classmethod
    def run(cls, namespace=None, **kwargs):
        """
        Execute command line parser for VTL module.
        """
        # Local CLI function
        def __cli(namespace, **kwargs):
            """
            CLI parser for VTL module.
            """
            commands = [];
            # Verify that the input is a valid method
            script = cls.verify(namespace)
            # Do not process platform scripts here.
            if not script.endswith(".py"): raise ValueError
            # Execute wrapper within this script or parse the command to the script
            argv = " ".join(sys.argv).split(namespace,1)[1].split()
            commands.append(" ".join([sys.executable,script]+argv))
            return commands
        # Local CMD function
        def __cmd(namespace, **kwargs):
            """
            CMD script execution for VTL module.
            """
            commands = []; script = None
            # Check if the namespace is already a valid CLI command
            if Utility.GetExecutable(namespace): script = namespace
            # Check if script is pending
            if not script: 
                # Verify that the input is a valid method
                script = cls.verify(namespace)
                # Execute wrapper within this script or parse the command to the script
                if Utility.GetPlatform() in ["linux"]: commands.append(" ".join(["chmod","u+x",script]))
            # Add command
            argv = " ".join(sys.argv).split(namespace)[1].split()
            commands.append(" ".join([script]+argv))
            return commands
        # Local variables
        delimn = " "
        # Use supplied configuration file. Can be empty. Only from poetry
        config = os.getenv("pyx_poetry_config",os.path.join(os.getcwd(),"pyproject.toml"))
        # No configuration file is given and default path does not exist
        if not os.path.exists(config): config = None
        # Support undocumented user options
        # Collect information from command line. Collect all parameters after '--'.
        try:
            dash_index = sys.argv.index("--")
            dashed_args = sys.argv[dash_index+1:]
            sys.argv = sys.argv[:dash_index]
        except ValueError: dashed_args = []
        ## Get function from parser
        # Check whether the given project ID string coincides with the selected method. 
        # Correctly identify this as a command line parameter and proceed accordingly.
        if not namespace or (namespace and config and namespace in sys.argv[-1] and not namespace in sys.argv[-2]):
            parser, options = cls.main(is_subparser=True)
            # Select method
            args, _ = parser.parse_known_args()
            # Default module execution
            commands = [delimn.join([sys.executable,"-m"] + args.method)]
            # Fetch the correct method. Only if not already defined.
            if not namespace: namespace = str(args.method[0])
        # Function is given directly
        else: commands = []; options = kwargs
        # CLI script is executed from main with configuration file within the current working directory
        if namespace and config: 
            try: 
                _ = args
                # If method contains multiple values, take the latter
                if args.method[0] != args.method[-1]: args.method.pop(0)
                # Only refer to pyproject.toml directly if not values are given
                if len(args.method) != 1: config = None
            ## The upper section has not been executed successfully. 
            # Thus, no values from a configuration file are processed. This is most-likely not an error.
            # Proceed as usual
            except UnboundLocalError: config = None
        # Try both. Raise error if none works
        try: commands = __cli(namespace, **options)
        except ValueError:
            try: commands = __cmd(namespace, **options)
            except: commands = []
        else: pass
        # This should never happen
        if not commands: raise ValueError("Unknown CLI option")
        # Execute all commands in order
        for i, command in enumerate(commands,1):
            # Only the last command in vein is an actual build command
            if i == len(commands): 
                # Add command line options from a supplied TOML file
                if config: command = cls.parse(command,config,args)
                # Add command line options w/o verification after '--'. Can be combined with TOML file or run without
                command = str(delimn.join([command]+dashed_args)).strip()
            # Execute all commands in order. Including preparation commands
            subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]),stderr=sys.stderr, stdout=sys.stdout) 
        pass

    @classmethod
    def main(cls,**kwargs):
        """
        Main entrypoint of PyXMake CLI. All other subparsers are derived from here.
        """
        # Import local version identifier
        from PyXMake import __version__
        # A dictionary of all valid identifiers
        options = cls.cli()
        # Get current class base name programmatically
        base = cls().CommandObjectKind
        # Collect all help messages
        __help__ = {
            "version": "%s (%s)" % (base, __version__),
            "method": 'An option identifier. Unknown arguments are ignored. Allowed values are: '+', '.join(options["choices"]),
            "main": 'CLI wrapper options for %s.' % base, 
            "info": 'Get information about the current version of %s.' % base, 
            "run": 'Run a predefined CLI command.'}
        # Parse all settings to directly to the child 
        setattr(cls, "__help__", __help__)
        # This argument is equal for all callables.
        argument = ["method", {"metavar":'namespace', "type":str, "nargs":argparse.REMAINDER, "choices":options["choices"], "help":__help__["method"]} ]
        # Equal for both methods
        parser = argparse.ArgumentParser(prog=base, description=cls.__help__["main"])
        parser.add_argument('-v', '--version', action='version', version=cls.__help__["version"])
        # Execute as main or return the parser object
        if not kwargs.get("is_subparser",False): 
            # Execute as main 
            subparsers = parser.add_subparsers(dest='namespace')
            # Add run to parser object
            __run = subparsers.add_parser('run', help=cls.__help__["run"])
            __run.add_argument(argument[0],**argument[1])
            # Add info to parser object
            subparsers.add_parser('info', help=cls.__help__["info"])
            try:
                # Try to execute CLI with typer
                cls.typer(**kwargs)
            # Something went wrong. Fall back to legacy implementation
            except RuntimeError:
            # Treat function as CLI command
                args = parser.parse_args()
                if args.namespace in ["run"]: Command.run(namespace=str(args.method[0]), **options)
                elif args.namespace in ["info"]: parser.parse_args(['--version'])
                else: parser.print_help(sys.stdout)
            # Return nothing if called directly.
            return 0
        else: 
            # Return the parser object.
            parser.add_argument(argument[0],**argument[1])
            # Return argparse and options interface
            return parser, options

def GetSourceCode(key_opt=0):
    """
    Get a list of source codes files associated with the build of MCODAC, BoxBeam or BEOS.
    
    @param: key_opt: An integer value representing the source code files. 
    @type: key_opt: integer
    """
    ## Source code files of MCODAC in the correct build order (excluding interface source code file).
    mcd_src_files = ["mcd_data", "mcd_error", "mcd_plugins", "mcd_tools", "mcd_contact", "mcd_material", 
                                   "mcd_load", "mcd_element", "mcd_subbuckling",  "mcd_dmginitiation", 
                                   "mcd_dmgevolution", "mcd_fracture", "mcd_dmginfluence", "mcd_degradation", 
                                   "mcd_dg8", "mcd_dmgtolerance","mcd_iostream", "mcd_fatigue", "mcd_prony",
                                   "mcd_wrapper", "mcd_toplevel", "mcd_main"]
    
    ## Source code files of BoxBeam in the correct build order (excluding interface source code file).
    box_src_files = ["box_data", "box_tools", "box_main"]
    
    ## Source code files of BEOS in the correct build order (excluding interface source code file).
    beos_src_files = ["beos_data","beos_tools","beos_main"]
    
    ## Source code files of MUESLI in the correct build order (excluding interface source code file).
    muesli_src_files = ["material.cpp", "tensor.cpp", "brownmiller.cpp", "jcfailure.cpp", "arrheniustype.cpp",   "arrudaboyce.cpp",   
                                    "finitestrain.cpp", "fisotropic.cpp", "fplastic.cpp", "johnsoncook.cpp", "mooney.cpp", "neohook.cpp", "reducedfinitestrain.cpp", 
                                    "svk.cpp", "yeoh.cpp", "zerilliarmstrong.cpp", "fluid.cpp",   "newtonian.cpp", "thermofinitestrain.cpp", 
                                    "fmechmass.cpp", "interface_abaqus.cpp", "interface_lsdyna.cpp", "mtensor.cpp", "mmatrix.cpp",
                                    "mrealvector.cpp","smallstrain.cpp",   "elastic.cpp", "reducedsmallstrain.cpp", "sdamage.cpp", "splastic.cpp", 
                                    "viscoelastic.cpp", "viscoplastic.cpp", "smallthermo.cpp", "conductor.cpp", "utils.cpp"]
    
    # Source code files of CompDam (NASA's material library) in correct build order (excluding interface source code files).
    compdam_src_files = ["vumatArgs.for","version.for.nogit","forlog.for","matrixUtil.for","matProp.for","stateVar.for","parameters.for", "schapery.for",
                                         "stress.for","strain.for","schaefer.for","plasticity.for","fiberDamage.for","friction.for","cohesive.for","DGD.for"]  
    #"vucharlength.for","vexternaldb.for","CompDam_DGD.for","vumatWrapper.for","UMAT.for"
    
    # Source code files of DispModule
    dispmod_src_files = ["dispmodule.f90","disp_i1mod.f90","disp_i2mod.f90","disp_i4mod.f90","disp_i8mod.f90","disp_l1mod.f90","disp_r16mod.f90"]  
    
    # Source code files of TOMS
    toms_src_files = ["toms790.f","toms661.f90"]
    
    # Source code files of various other libraries
    misc_src_files =["nms.f90","pchip.f90","slatec.f90","interp.f90"]

    # Source code for PyCODAC application
    pyc_src_files = ["__exe__.py"]
    
    # Select correct files for output
    if key_opt==0:
        source = mcd_src_files
    elif key_opt==1:
        source = box_src_files
    elif key_opt==2:
        source = beos_src_files         
    elif key_opt==3:
        source = muesli_src_files       
    elif key_opt==4:
        source = compdam_src_files
    elif key_opt==5:
        source = dispmod_src_files
    elif key_opt==6:
        source = toms_src_files
    elif key_opt==7:
        source = misc_src_files
    elif key_opt==8:
        source = pyc_src_files                     
    else:
        raise NotImplementedError
    # Return list of source code files in correct order.
    return source

def GetPreprocessingCommand(pre_opt=0):
    """
    Return the recommended preprocessor command line.
    
    @param: make_opt: An integer value representing or qualified name the requested  preprocessor
    @type: pre_opt: integer or string
    """           
    delimn = " " 
    # All supported preprocessor
    Supported = ["fpp", "cpp"]
    # Parse both string and integer representation
    PreprocessorDict = {x:y for x, y in enumerate(Supported)}
    # Get string instance
    preprocessor = pre_opt
    if isinstance(pre_opt, int): preprocessor = PreprocessorDict[pre_opt]
    # Raise error if preprocessor is not supported
    if preprocessor not in Supported: raise NotImplementedError
    # Get preprocessing command in dependence of FPP oder CPP
    precmd = [preprocessor ,"-P"]
    if preprocessor in ["fpp"]: precmd.extend(["-e"])
    if preprocessor in ["cpp"]: precmd.extend(["--traditional"])
    # Return assembled
    return delimn.join(precmd)

def GetBuildCommand(make_opt=0, _format="fixed", _arch=Utility.GetArchitecture(), **kwargs):
    """
    Return the recommended command line during the build process for selected make operations.
    
    @param: make_opt: An integer value representing the make operation.
    @type: make_opt: integer
    """
    delimn = " "
    # Some local imports
    from packaging.version import parse
    from numpy.version import version
    # Recover information from cmake to retrieve build settings
    try: 
        with open(os.path.join(os.getcwd(),"build","CMakeCache.txt")) as f:
            sequential = [x.strip().split("=")[-1] for x in f.readlines() if "sequential" in x.lower()][-1]
        multithreading = not Utility.GetBoolean(sequential)
    except: multithreading = True
    
    ## Build command for Java applications under Windows           
    win_java_command = "-nologo -O3 -Qopenmp -Qauto_scalar -Qparallel -Qmkl:parallel -Qopt-matmul -fpp -DDEBUG -recursive \
    -reentrancy:threaded -"+_format+" -extend_source:132 -fpe:0 -heap-arrays1 -iface:cref -libs:static -threads -MT -W1 " 
    
    ## Build command for Fortran applications under Windows  
    win_fortran_command = "-nologo -O3 -QxSSE3 -Qopenmp -Qauto_scalar -Qparallel -Qmkl:parallel -Qopt-matmul -fpp -DDEBUG -recursive \
    -reentrancy:threaded -"+_format+" -extend_source:132 -fpe:0 -fp:precise -traceback -heap-arrays1 -iface:cref -libs:dll -threads -MD -W1"
    
    ## Build command for C++ applications under Windows          
    win_cxx_command =  "-nologo -Os -W0 -MD -TP -EHsc -Qpar -clr:nostdlib -fp:precise -std:c++latest " 
    win_cxx_command +="-FI pyx_muesli_def.h "
    win_cxx_command +="-FI algorithm -FI ctime "
    win_cxx_command +="-FI iso646.h "
    win_cxx_command +="-FI pyx_muesli_undef.h "
    
    ## Build command for Python applications under Windows      
    win_pyd_command = ' -DNO_APPEND_FORTRAN '
    win_pyd_command += ' --f90flags="-'+_format+' -fpe:0 -fp:precise -threads -recursive -Qauto-scalar -Qopenmp -Qmkl:parallel -heap-arrays:1" '  
    win_pyd_command += ' --opt="-O2" --arch="-QaxSSE3 /assume:nounderscore" --quiet --compiler=msvc ' 
    
    ## Build command for Python applications under Linux  
    lin_pyd_command = '--quiet --fcompiler=intelem --opt="-O2" --f90flags="-'+_format+' -fp-model precise -fpe0 -recursive -parallel -auto -qopenmp -qopt-matmul -mkl:parallel"'
    
    ## Build command for Fortran applications under Linux     
    lin_fortran_command = "-fpp -qopenmp -DCLUSTER -DDEBUG -DUSE_MUESLI -fPIC -auto " 
    lin_fortran_command += "-mkl:parallel -extend_source -O2 -"+_format+" -parallel -fpe0 -traceback -recursive "
    lin_fortran_command += "-nostandard-realloc-lhs"
    
    # Build command for ABAQUS applications under windows
    win_abq_command = "ECHO import os >> %ABQ_ENV_FILE% " 
    win_abq_command += "&& ECHO usub_lib_dir=os.getcwd() >> %ABQ_ENV_FILE% " 
    win_abq_command += "&& ( " 
    win_abq_command += "ECHO compile_fortran=compile_fortran[:3] + ["
    win_abq_command += "'/heap-arrays:1', "  
    win_abq_command += "'/O3', " #<-- Optimization level     
    win_abq_command += "'/fpe:0', "  # <-- Floating point exception handling / Prevents division through zero
    win_abq_command += "'/traceback', " # <-- Traceback errors    
    win_abq_command += "'/Qopt-matmul', "
    win_abq_command += "'/threads', "
    ## Some flags are not supported when using the latest Intel Fortran environment
    # Deactivate everything related to multithreading
    if not Utility.GetExecutable("oneapi-cli") or multithreading:
        win_abq_command += "'/MD', " # <-- Multithreading CRT library
        win_abq_command += "'/Qparallel', " # <-- Use multithreading standard libraries
        win_abq_command += "'/Qmkl:parallel', " # <-- Use MKL libraries
        win_abq_command += "'/Qopenmp', " # <-- Use OpenMP library
        win_abq_command += "'/libs:dll', "
    else:
        win_abq_command += "'/Qmkl:sequential', " # <-- Use MKL libraries

    # win_abq_command += "'/warn:all', "
    # win_abq_command += "'/warn:nousage', "
    # win_abq_command += "'/warn:interfaces', "
    # win_abq_command += "'/check:pointer', "
    # win_abq_command += "'/check:uninit', "
    # win_abq_command += "'/check:format', "
    # win_abq_command += "'/check:output_conversion', "
    # win_abq_command += "'/check:arg_temp_created', " 
    # win_abq_command += "'/check:bounds', " # <-- Array boundary check     
    # win_abq_command += "'/debug:extended', " # <-- Debug function information   
    # win_abq_command += "'/debug-parameters:all', " # <-- Debug parameter information
    # win_abq_command += "'/Ob0', " # <-- Function inlining
    # win_abq_command += "'/Zi', " # <-- Debugging # CompLine += "'/watch:all', "

    win_abq_command += "] + compile_fortran[3:] ) >> %ABQ_ENV_FILE% "
    win_abq_command += "&& ( "     
    if not Utility.GetExecutable("oneapi-cli") or multithreading:
        win_abq_command += "ECHO link_sl=link_sl[:3] + [" 
        # Overwrite CRT section in ABQ, since its implementation is flawed (or at least is not modifiable enough for our purposes).
        win_abq_command += "r'/def:"+os.getenv("pyx_abaqus_def","%E")+"', '/INCLUDE:_DllMainCRTStartup', '/FORCE'] + link_sl[3:] + ["
    else: 
        # Remove shared Intel Fortran core library for multithreading
        win_abq_command += "ECHO link_sl=['LINK','/NODEFAULTLIB:LIBCMT.LIB','/FORCE','/dll','/def:%E','/out:%U','%F','%A','%L','%B',"
    # win_abq_command+= "'/DEBUG', " # <-- Debugging 
    # win_abq_command += "'/VERBOSE', " # <-- Show commands
    win_abq_command += "%pyx_libs%] ) >> %ABQ_ENV_FILE% "                       
    win_abq_command += '&& %pyx_abaqus% make -library %pyx_file%'

    lin_per_command = ""; 
    # Fetch startup directory (defaults to user's home directory)
    lin_per_command += 'if [ -z ${HOME+x} ]; then : ; else HOME=${PWD};fi; '
    # Set working directory
    lin_per_command += "WorkDir=$PWD;" 
    lin_per_command += "ZipArchive='peridigm.zip';"
    # The directory where all the magic happens - should not exist in advance
    lin_per_command += 'TempDir=$HOME/"${ZipArchive%.*}"/;' 
    # Internal directory names
    lin_per_command += "builddir='build'; srcdir='src';"
    # File names
    lin_per_command += "file_cmake='cmake.cmake';" 
    lin_per_command += "file_cmake_log='cmake.log';"  
    lin_per_command += "file_make_log='make.log';"  
    lin_per_command += "file_make_install_log='make_install.log';"
    lin_per_command += "file_peridigm_bin='Peridigm';"
    # Number of CPUs for make
    lin_per_command += "make_cpus=$((`nproc`+1));"
    # Folder structure
    lin_per_command += "if [ -d ${TempDir} ]; then"
    lin_per_command += "  echo 'Directory '${TempDir}' already exists. Exit.';"
    lin_per_command += "  exit 0;"
    lin_per_command += "fi;" 
    # Create folder structure
    lin_per_command +="mkdir ${TempDir};" 
    lin_per_command +="cd ${TempDir};"
    lin_per_command +="mkdir ${builddir};" 
    lin_per_command +="mkdir ${srcdir};" 
    lin_per_command +="cd ${srcdir};"
    # Build from ZIP
    lin_per_command +="unzip  -q ../../${ZipArchive} -d . &&" 
    lin_per_command +="mv peridigm-master peridigm 2>/dev/null &&" 
    lin_per_command +="cd ../${builddir};"
    lin_per_command +="cd $WorkDir;" 
    lin_per_command+="mv $ZipArchive $TempDir/ &&" 
    lin_per_command +="cd $TempDir/$builddir;"
    # Create cmake file
    lin_per_command +="echo 'rm -f CMakeCache.txt' >> ${file_cmake};"
    lin_per_command +="echo 'rm -rf CMakeFiles/' >> ${file_cmake};"
    lin_per_command +="echo '' >> ${file_cmake};"
    lin_per_command +=r"echo 'cmake \' >> ${file_cmake};"
    lin_per_command +=r"echo '-D USE_MCODAC:BOOL=TRUE \' >> ${file_cmake};"
    lin_per_command +=r"echo '-D MESH_CONVERTER_DIR:STRING=mesh_converter \' >> ${file_cmake};"
    lin_per_command +=r"echo '-D CMAKE_BUILD_TYPE:STRING=Release \' >> ${file_cmake};"
    lin_per_command +=r"echo '-D CMAKE_INSTALL_PREFIX='${TempDir}${builddir}' \' >> ${file_cmake};"
    lin_per_command +=r"echo '-D CMAKE_CXX_COMPILER:STRING="+'"mpicxx"'+r" \' >> ${file_cmake};"
    lin_per_command+="echo '-D CMAKE_CXX_FLAGS:STRING="+'"-DUSE_MCODAC -O2 -Wall -std=c++11 -pedantic -Wno-long-long -ftrapv -Wno-deprecated"'+r" \' >> ${file_cmake};"
    lin_per_command+="echo '-D CMAKE_EXE_LINKER_FLAGS:STRING="+'"${pyx_per_linking:--L${HOME}/mcodac/bin -lperuser}"'+r" \' >> ${file_cmake};"
    lin_per_command +="echo ${TempDir}${srcdir}'/peridigm/' >> ${file_cmake};"
    # Execute cmake file
    lin_per_command +="chmod u+x ${file_cmake};"
    lin_per_command +="./${file_cmake} > ${file_cmake_log} 2>&1;"
    # Execute make command
    lin_per_command +="make -j ${make_cpus} > ${file_make_log} 2>&1;"
    lin_per_command +="make install > ${file_make_install_log} 2>&1;"
    # Clean up workspace
    lin_per_command +="cd bin;"
    lin_per_command +="cp ${file_peridigm_bin} ${pyx_per_output:-${HOME}}/${file_peridigm_bin};"
    lin_per_command +="cd $WorkDir;"
    lin_per_command +="rm -rf $TempDir;"  

    lin_tri_command = "";     
    lin_tri_command += "cmake "
    lin_tri_command += "-DTPL_LAPACK_LIBRARIES='/sw/MPI/GCC/8.2.0-2.31.1/OpenMPI/3.1.3/ScaLAPACK/2.0.2-OpenBLAS-0.3.5/lib/liblapack.a' "
    lin_tri_command += "-DTPL_ENABLE_HDF5:BOOL=ON -DTPL_ENABLE_Matio=OFF "
    lin_tri_command += "-DTPL_ENABLE_MPI=ON -DTrilinos_ENABLE_ALL_PACKAGES=ON "
    lin_tri_command += "-DCMAKE_INSTALL_PREFIX=${HOME}/mcodac/external/trilinos ${HOME}/trilinos"

    # Architecture dependencies are related to the PYTHON version used in the build process, thus the check is made here.
    if not sys.version_info >= (3,12): 
        # Custom compiler commands for f2py.               
        if ('x86' in _arch): win_pyd_command += " --fcompiler=intelv" 
        # Custom compiler commands for f2py.              
        elif ('x64' in _arch): win_pyd_command += " --fcompiler=intelvem" 

    # Adding support for meson build backend
    if parse(version) >= parse("1.26.4") or sys.version_info >= (3,12) or kwargs.get("backend",""): 
        command = " --backend=%s " % kwargs.get("backend","meson" 
                               if (parse(version) >= parse("1.26.4") and Utility.GetExecutable("meson")) or sys.version_info >= (3,12) 
                               else "distutils")
        win_pyd_command = delimn.join([x if not x.startswith("--f90flags") else command+x for x in win_pyd_command.split(" ")])
        lin_pyd_command = delimn.join([x if not x.startswith("--f90flags") else command+x for x in lin_pyd_command.split(" ")])

    if make_opt==0:
        command = win_pyd_command
    elif make_opt==1:
        command = win_java_command  
    elif make_opt==2:
        command = win_fortran_command 
    elif make_opt==3:
        command = win_cxx_command
    elif make_opt==4:
        command = lin_pyd_command        
    elif make_opt==5:
        command = lin_fortran_command
    # In dependence to 3rd party FE software
    elif make_opt==6:
        command = win_abq_command
    elif make_opt==7:
        command = lin_per_command
    else:
        raise NotImplementedError
    
    return command

def GetIncludeDirectory(base_path, key_opt=0, make_opt=0, architecture="x64"):
    """
    Return all mandatory include directories for the requested make operation in dependence of key_opt. 
    
    @param: key_opt, make_opt: [An integer value representing the source code file (e.g. MCODAC, BoxBeam, BEOS), 
                                                      An integer value representing the make operation.]
    @type: key_opt, make_opt: integer
    """
    ## Source code files of MCODAC in the correct build order (excluding interface source code file).    
    if key_opt == 0 and make_opt in range(6):
        try:
            inc =  list(Utility.PathWalk(os.path.join(base_path,"include",Utility.GetPlatform(),architecture), startswith=(".", "__")))[0][1]
        except IndexError:
            inc = ""
    elif key_opt == 8:
        ## Add base path to overall search path (if valid and existing)
        if os.path.exists(base_path):
            sys.path.append(base_path)
        ## Access required packages
        try:
            # Check for python OCC
            import OCC
            # Get qualified package name
            __occ_name = OCC.__name__
            # Get absolute package paths
            __occ_src_path = OCC.__path__[0]
        except ImportError:
            # OCC is not part of the current environment
            __occ_name = ""; __occ_src_path = ""
        try:
            # Import PyCODAC to build library locally during setup.
            import PyCODAC
            # Get qualified package name
            __pyc_name = PyCODAC.__name__
            # Get absolute package paths
            __pyc_src_path = PyCODAC.PyCODACPath
        except ImportError:
            # This script is not executed as plug-in for PyCODAC
            __pyc_name = ""; __pyc_src_path = ""   
            pass
        ## Add dependencies
        inc = ["six.py", "ipykernel_launcher.py",
                # Add PyCODAC packages
                os.path.join(__pyc_name,"__init__.py"),
                os.path.join(__pyc_name,"Paths.log"),
                os.path.join(__pyc_name,"Tools","__init__.py"),
                os.path.join(__pyc_name,"Tools","Utility.py"),
                os.path.join(__pyc_name,"Core","cmd"),
                # Add compiled binaries
                os.path.join(__pyc_name,"Core","bin",Utility.GetPlatform(),architecture),
                os.path.join(__pyc_name,"Study","bin",architecture),
                os.path.join(__pyc_name,"Study","cmd",Utility.GetPlatform()),
                # Add PyCODAC databases  
                os.path.join(__pyc_name,"Database"),
                # Add JupyterLab configuration and application files
                os.path.join(__pyc_name,"Plugin","JupyterLab","bin", Utility.GetPlatform()),
                os.path.pathsep.join([os.path.join(__pyc_src_path,"Plugin","JupyterLab","config","jupyter_notebook_utils.py"),"."]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,"Plugin","JupyterLab","config"),os.path.join(__pyc_name,"Plugin","JupyterLab","config",".")]),
                # Add configuration file for Smetana
                os.path.join(__pyc_name,"Plugin","Smetana","config","pyc_smetana.config"),
                # Add images directly to executable
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","pyc_lab_icon.png"), os.path.join(__pyc_name,     "GUI", "res",".")]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","pyc_dic_analysis.png"),os.path.join(__pyc_name,     "GUI", "res",".")]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","stmlab_icon.png"), os.path.join(__pyc_name,     "GUI", "res",".")]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","stm_main.png"),os.path.join(__pyc_name,     "GUI", "res",".")]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","stm_lightweight.png"),os.path.join(__pyc_name,     "GUI", "res",".")]),
                os.path.pathsep.join([os.path.join(__pyc_src_path,   "GUI","res","stm_vph.png"), os.path.join(__pyc_name,     "GUI", "res",".")])]
        
        # Added OCC module explicitly
        if os.path.exists(__occ_src_path): inc.insert(3,os.path.pathsep.join([__occ_src_path,os.path.join(__occ_name,".")]))
        
        try: 
            # Compatibility support for latest version of JupyterLab
            from PyCODAC import __hook__
            ## Add named modules in site package explicitly
            imported = set([x for x in dir(__hook__) if not x.startswith("_")]) - set(dir(__builtins__)) - set(["PyCODAC","PyXMake"])
            data = [importlib.import_module(x) for x in imported]
            inc.extend([os.path.pathsep.join([os.path.dirname(x.__file__),os.path.join(x.__name__,".")])  if x.__file__.endswith("__init__.py") else Utility.PathLeaf(x.__file__) for x in data])
            ## Add all metadata information as well (forward compatibility)
            dist_search_paths = set([os.path.abspath(os.path.join(x.__file__, os.path.pardir, os.path.pardir)) if x.__file__.endswith("__init__.py") else os.path.abspath(os.path.join(x.__file__, os.path.pardir)) for x in data])
            inc.extend([os.path.pathsep.join([os.path.join(path,Utility.PathLeaf(y)),os.path.join(Utility.PathLeaf(y),".")]) for path in dist_search_paths for y in os.listdir(path) for found in data if y.startswith(found.__name__) and y.endswith(".dist-info")])
        except Exception as _: pass
    else:
        inc = [] 
    return inc

def GetLinkDependency(key_opt=0, make_opt=0, architecture="x64"):
    """
    Return all mandatory external libraries for the requested make operation in dependence of key_opt. 
    
    @param: key_opt, make_opt: [An integer value representing the source code file (e.g. MCODAC, BoxBeam, BEOS), 
                                                         An integer value representing the make operation.]
    @type: key_opt, make_opt: integer
    """
    ## Source code files of MCODAC in the correct build order (excluding interface source code file).    
    if key_opt == 0 and make_opt in range(6):
        lib = [x + architecture for x in ["interp", "pchip", "bbeam","muesli","dispmodule","toms"]]
    elif key_opt == 8:
        ## Add additional libraries
        lib = [x for x in sorted(set(sys.path), key=lambda x: 'site-packages' in x)]  
    else:
        lib = []   
    return lib

def GetEnvironment(env_opt=0):
    """
    Return predefined source environment to initiate a build process.
    
    @param: env_opt An integer value representing a predefined environment
    @type: env_opt: integer
    """
    if env_opt == 0:
        ## Return Intel Fortran environment (DLR institute cluster)  
        env = [posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d","ifort2016.sh")]
    elif env_opt == 1:
        ## Return Intel Fortran environment & PYTHON 2.7 (DLR institute cluster)  
        env = [posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d","ifort2016.sh"), 
                   posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","python2.7","env.sh")],
    elif env_opt ==2:
        ## Return Intel Fortran environment & PYTHON 3.5 (DLR institute cluster)  
        env = [posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d","ifort2016.sh"), 
                   posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","python3.5","env.sh")],
    elif env_opt ==3:
        ## Return Intel Fortran environment & PYTHON 3.x (DLR institute cluster)  
        env = [posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d","ifort2016.sh"), 
                   posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","mcodac","anaconda","envs","Conda36","env.sh")],
    elif env_opt == 4:
        ## Return Intel Fortran environment & ABAQUS environment (DLR's HPC cluster; CARA)
        # Use a more module environments instead of source files.
        env =["module purge; module load iccifort; module load iimpi; module load ABAQUS/2023"]
    elif env_opt ==5:
        ## Return environment required to build Trilinos on DLR's HPC cluster. 
        # Order is important, since some modules cannot be loaded later.
        env = ["module purge; module load GCC; module load OpenMPI; module load OpenBLAS; module load netCDF; \
                     module load Boost; module load ScaLAPACK; module load GCCcore/8.3.0; module load HDF5; \
                     module load GCCcore/10.2.0; module load CMake/3.18.4;"] 
    else:
        raise NotImplementedError
    return env

## Silently install all dependencies on the first start
if not getattr(sys, 'frozen', False) or all(f.startswith("stm") for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py") and not f.startswith("__")): 
    subprocess.check_call([sys.executable,os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),"__install__.py")])

# Create useful names for import. Each script acts also as a minimum working example.
try:
    # Use lazy import when running as CLI
    if os.isatty(sys.stdout.fileno()) and os.path.exists(os.path.dirname(__file__)): raise RuntimeError
    # Probe import capabilities
    from .doxygen import main as _
except (ImportError, RuntimeError, io.UnsupportedOperation) as _:
    # Register all functions dynamically. 
    for x in os.listdir(os.path.dirname(__file__)):
        if not x.endswith(".py") or x.startswith("_"): continue
        func = x.split(".")[0]
        exec("""def %s(*args, **kwargs): mod = importlib.import_module('.%s',__name__); return mod.main(*args, **kwargs)""" % (func, func))
else:
    # Build documentation
    from .doxygen import main as doxygen
    from .sphinx import main as sphinx
    from .latex import main as latex
    # API builds
    if sys.version_info >= (3,7) and os.path.exists(os.path.join(Utility.GetPyXMakePath(),"API")):
        from .api import main as api
    # Dependency builds
    from .pyreq import main as pyreq
    # Bundle builds
    from .app import main as app
    from .bundle import main as bundle
    from .archive import main as archive
    from .openapi import main as openapi
    # Host builds
    from .abaqus import main as abaqus
    from .cmake import main as cmake
    from .ifort import main as ifort
    from .gfortran import main as gfortran
    from .java import main as java
    from .py2x import main as py2x
    from .cxx import main as cxx
    # Remote builds
    from .ssh_ifort import main as ssh_ifort
    from .ssh_f2py import main as ssh_f2py
    from .ssh_make import main as ssh_make
    # Utilities
    from .stm_svn2git import main as svn2git
    # Unit testing
    from .coverage import main as coverage

## Collect compatibility alias from 3rd party extensions module
try: from PyXMake.Plugin import bdist_wheel as build #@UnresolvedImport
except: pass 

## Adding compatibility alias for f2py. py2x as a name is deprecated in future releases.
# It remains solely for backwards compatibility.
try: setattr(sys.modules[__name__],"f2py", getattr(sys.modules[__name__],"py2x"))
except: pass

## Backwards compatibility for function calls
setattr(sys.modules[__name__],"run", getattr(Command,"run"))
setattr(sys.modules[__name__],"main",getattr(Command,"main"))

if __name__ == '__main__':
    pass