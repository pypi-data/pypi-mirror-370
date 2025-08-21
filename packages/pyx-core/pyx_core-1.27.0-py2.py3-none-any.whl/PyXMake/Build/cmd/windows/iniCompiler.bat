@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                             Initialization of Intel FORTRAN compiling environment (x64) on Windows                   %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Intel Fortran Win64 Initialization allowing access via PyDev - Eclipse
@REM Created on 20.03.2018	
@REM 
@REM ------------------------------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - Commented out:                                                                                 // mg 26.03.2018 
@REM 		@REM Set C++ Compiler Environment
@REM 		CALL "%CPPPATH%\vcvarsall.bat" %pyx_proc%
@REM 		FOR /f "skip=21 delims=" %%G IN (%LogPath%Paths.log) DO IF NOT DEFINED CPPPATH SET CPPPATH=%%G
@REM
@REM     @author: garb_ma                                                                           [DLR-SY,STM Braunschweig]
@REM ------------------------------------------------------------------------------------------------------------------------
@ECHO OFF
@REM Only execute this part when environment is not set. Attempt search for Paths.log
@SET CURRENTPATH=%cd%
@CD /d %~dp0..
@CD ..\..
@SET LogPath=%cd%\
@REM Get paths from Paths.log 
IF NOT DEFINED pyx_environment ( 
@FOR /f "skip=20 delims=" %%G IN (%LogPath:~0,-1%\Paths.log) DO ( 
IF NOT DEFINED IFORTPATH SET IFORTPATH=%%G)
)
@CD /d %CURRENTPATH% 
@REM Set C++ & Intel Fortran Compiler Environment on Windows
IF NOT DEFINED pyx_environment SET pyx_environment=%IFORTPATH%\bin\ifortvars.bat
IF EXIST "%pyx_environment%" @CALL "%pyx_environment%" %pyx_intel% %pyx_msvsc% 
@REM Execute build command
@CALL %*