from cx_Freeze import setup, Executable


exe = Executable(script='main.py',
                 base='Win32Gui')

includefiles = ['resources']
includes = []
excludes = []
packages = []
bin_path_excludes = []

setup(version='0',
      description='A Simple Shooter',
      author='YOU',
      name='ASS',
      options={'build_exe': {'compressed': False,
                             'excludes': excludes,
                             'packages': packages,
                             'include_files': includefiles,
                             'bin_excludes': bin_path_excludes}},
      executables=[exe])
