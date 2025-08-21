@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    	 Postprocessing 4 Jenkins on Windows 7/10 (x64)                     %     
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Command script to run release PyXMake jobs on Jenkins (FA-STM).
@REM Created on 21.01.2020
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - 
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
@SETLOCAL EnableDelayedExpansion

@TITLE %~nx0
@REM This script is mostly executed on the Jenkins test server.
@IF %COMPUTERNAME% == FA-JENKINS2 (
@SET USERNAME=f_testpa
@SET USERPROFILE=C:\Users\%USERNAME%
@SET STM_POST=py36_stmlab
@SET "PATH=C:\Miniforge_envs;%PATH%"
)

@REM Activate postprocessing environment
@IF NOT DEFINED STM_POST SET "STM_POST=py36"

@REM Activate powershell scripts for the current active user.
@CALL powershell -c "Set-ExecutionPolicy Unrestricted -Scope CurrentUser" >> nul

@REM Release workspace to help Jenkins free SVN connection
@RD /S /Q %CD%\build >nul 2>nul
@RD /S /Q %CD%\Beos >nul 2>nul
@RD /S /Q %CD%\BoxBeam >nul 2>nul
@RD /S /Q %CD%\PyXMake >nul 2>nul
@RD /S /Q %CD%\PyCODAC >nul 2>nul
@RD /S /Q %CD%\MCODAC >nul 2>nul

@REM Define process name to be terminated.
@SET STM_PROCESS='ssh.exe'
@ECHO wmic process where "name=%STM_PROCESS%" delete >> STM_KILL.ps1
@CALL powershell %CD%\STM_KILL.ps1 >nul 2>nul
@DEL %CD%\STM_KILL.ps1

@REM Store pristine paths
@SET pristine_workspace=%CD% 

@REM Get current batch script file and crop final backslash
CD %~dp0 && CD ..
@SET Service=%CD%
CD %pristine_workspace%

@REM Activate local conda environment
@CALL conda deactivate
@CALL conda activate %STM_POST%
@CALL python %Service%\stm_post.py
@CALL conda deactivate

@SET ERRORLEVEL=0
@EXIT /B %ERRORLEVEL%