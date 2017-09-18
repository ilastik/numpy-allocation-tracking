REM Build the alloc_hook extension module
cd numpy\tools\allocation_tracking
"%PYTHON%" setup.py build_ext

REM Copy into a single directory
del README.md
copy *.* "%SRC_DIR%\numpy_allocation_tracking\"

cd build\lib*
copy alloc_hook.*.pyd "%SRC_DIR%\numpy_allocation_tracking\"

REM Install
del "%SRC_DIR%\numpy_allocation_tracking\setup.py"
xcopy "%SRC_DIR%\numpy_allocation_tracking" "%SP_DIR%\numpy_allocation_tracking\" /s
