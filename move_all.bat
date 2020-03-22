REM be very careful when you use this file :D
REM set current directory to a variable

SET curdir = %cd%

REM ECHO %cd%

REM The following line deletes the files with the extensions after the del command.
for /f "tokens=1* delims=" %%a in ('date /T') do set datestr=%%a

mkdir %curdir%+%datestr%
ECHO %curdir%+%datestr%
