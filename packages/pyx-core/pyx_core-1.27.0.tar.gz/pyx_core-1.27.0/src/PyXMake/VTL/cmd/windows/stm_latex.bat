@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                                             Modified Latex Initialization                                            %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM General Latex Win64 Initialization allowing access via PyDev - Eclipse
@REM Created on 27.08.2020	
@REM 
@REM Version: 2020
@REM ------------------------------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - 
@REM
@REM     @author: garb_ma                                  				        		       [DLR-FA,STM Braunschweig]
@REM ------------------------------------------------------------------------------------------------------------------------
@ECHO OFF 
@SETLOCAL EnableDelayedExpansion
@REM Store pristine paths
@SET pristine_workspace=%CD% 
@REM Get current workspace and crop final backslash for convenience.
CD %~dp0 && CD ..\..
@SET pyx_bin_directory=%CD%\Build\bin
@SET pyx_config_directory=%CD%\Build\config
CD %pristine_workspace%
@REM Set additional search paths
@SET PATH=%pyx_bin_directory%\perl\perl\site\bin;%pyx_bin_directory%\perl\perl\bin;%pyx_bin_directory%\perl\c\bin;%pyx_bin_directory%\miktex\texmfs\install\miktex\bin\x64;%PATH%
@SET TEXINPUTS=%pyx_config_directory%;%TEXINPUTS%
@REM Run initialization commands
@CALL texworks.exe
@REM No need to keep this script active
@EXIT 0