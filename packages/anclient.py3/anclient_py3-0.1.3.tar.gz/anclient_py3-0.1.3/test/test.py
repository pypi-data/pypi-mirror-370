import os
import unittest

# project_root = os.path.abspath(os.path.dirname(__file__))
# if project_root in sys.path:
#     sys.path.remove(project_root)
#
# site_packages = os.path.join(sys.exec_prefix, 'lib', 'site-packages')
# if site_packages not in sys.path:
#     sys.path.insert(0, site_packages)

from anson.io.odysz.common import Utils

"""
    PyCharm Debug Configuration:
    run as module: test.test
    working folder: py3
"""

def run_script(script_path):
    python = 'py' if Utils.iswindows() else 'python3'
    os.system(f'{python} {script_path}')

test_loader = unittest.TestLoader()
test_suite = test_loader.discover(start_dir='test', pattern='t_*.py')


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite)