#@+leo-ver=5-thin
#@+node:ekr.20240322173731.1: * @file ../scripts/pip_uninstall_all.py
"""
pip_uninstall_leo.py: Uninstall *all* installed files.

Don't use this script unless you know what you are doing!

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""
import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
    f"{python} -m pip freeze > temp_requirements.txt",
    f"{python} -m pip uninstall -r temp_requirements.txt -y --verbose",
    f"{python} -m pip list",

]:
    print('')
    print(command)
    print('')
    subprocess.Popen(command, shell=True).communicate()

if os.path.exists('temp_requirements.txt'):
    print('')
    print('remove temp_requirements.txt')
    os.remove('temp_requirements.txt')

# cd to the leo-editor directory.
os.chdir(leo_editor_dir)
#@-leo
