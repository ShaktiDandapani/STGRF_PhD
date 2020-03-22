@ECHO off
REM be very careful when you use this file :D
REM set current directory to a variable

SET curdir = %cd%

REM ECHO %cd%

REM The following line deletes the files with the extensions after the del command.
del  *.full *.db *.emat *.mntr *.inp *.BCS *.log *.stat output.txt *.esav *.page *.lock 
del  *.r001 *.rdb *.db *.dbb *.ldhi *.err  *.osav *.rst *.csv *.txt *.dmp *.vtk *.DSP