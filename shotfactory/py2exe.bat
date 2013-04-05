@echo off
del /S /Q build
rmdir build
del /S /Q bin
rmdir bin
python setup.py py2exe
copy thirdparty\*.* bin
