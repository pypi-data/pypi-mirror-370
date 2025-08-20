import os
import sys
import warnings

import pytest

try:
    from qtpy import PYSIDE2, PYSIDE6
except Exception:
    PYSIDE2 = PYSIDE6 = False

from glue.config import CFG_DIR as CFG_DIR_ORIG

try:
    import objgraph
except ImportError:
    OBJGRAPH_INSTALLED = False
else:
    OBJGRAPH_INSTALLED = True


STDERR_ORIGINAL = sys.stderr

ON_APPVEYOR = os.environ.get('APPVEYOR', 'False') == 'True'


def pytest_runtest_teardown(item, nextitem):
    sys.stderr = STDERR_ORIGINAL
    global start_dir
    os.chdir(start_dir)


def pytest_addoption(parser):
    parser.addoption("--no-optional-skip", action="store_true", default=False,
                     help="don't skip any tests with optional dependencies")


start_dir = None


def pytest_configure(config):

    global start_dir
    start_dir = os.path.abspath('.')

    os.environ['GLUE_TESTING'] = 'True'

    from glue._mpl_backend import set_mpl_backend
    set_mpl_backend()

    if config.getoption('no_optional_skip'):
        from glue.tests import helpers
        from glue_qt.tests import helpers as qt_helpers
        for attr in helpers.__dict__:
            if attr.startswith('requires_'):
                # The following line replaces the decorators with a function
                # that does nothing, effectively disabling it.
                setattr(helpers, attr, lambda f: f)
        for attr in qt_helpers.__dict__:
            if attr.startswith('requires_'):
                setattr(qt_helpers, attr, lambda f: f)

    # Make sure we don't affect the real glue config dir
    import tempfile
    from glue import config
    config.CFG_DIR = tempfile.mkdtemp()

    # Start up QApplication, if the Qt code is present
    from glue_qt.utils import get_qapp
    get_qapp()

    # Force loading of plugins
    from glue.main import load_plugins
    load_plugins()


def pytest_unconfigure(config):

    os.environ.pop('GLUE_TESTING')

    # Reset configuration directory to original one
    from glue import config
    config.CFG_DIR = CFG_DIR_ORIG

    # Remove reference to QApplication to prevent segmentation fault on PySide
    from glue_qt.utils import app
    app.qapp = None

    if OBJGRAPH_INSTALLED and not ON_APPVEYOR:

        # Make sure there are no lingering references to GlueApplication
        obj = objgraph.by_type('GlueApplication')
        if len(obj) > 0:
            objgraph.show_backrefs(objgraph.by_type('GlueApplication'))
            warnings.warn('There are {0} remaining references to GlueApplication'.format(len(obj)))

        # Uncomment when checking for memory leaks
        # objgraph.show_most_common_types(limit=100)


# With PySide2/6, tests can fail in a non-deterministic way on a teardown error
# or with the following error:
#
#   AttributeError: 'PySide2.QtGui.QStandardItem' object has no attribute '...'
#
# Until this can be properly debugged and fixed, we xfail any test that fails
# with one of these exceptions.

if PYSIDE2 or PYSIDE6:
    QTSTANDARD_EXC = "QtGui.QStandardItem' object has no attribute "
    QTSTANDARD_ATTRS = ["'connect'", "'item'", "'triggered'"]

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup():
        try:
            outcome = yield
            return outcome.get_result()
        except AttributeError:
            exc = str(outcome.excinfo[1])
            for attr in QTSTANDARD_ATTRS:
                if QTSTANDARD_EXC + attr in exc:
                    pytest.xfail(f'Known issue {exc}')

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call():
        try:
            outcome = yield
            return outcome.get_result()
        # excinfo seems only to be preserved through a single hook
        except (AttributeError, ValueError):
            exc = str(outcome.excinfo[1])
            if "No net viewers should be created in tests" in exc:
                pytest.xfail(f'Known issue {exc}')
            for attr in QTSTANDARD_ATTRS:
                if QTSTANDARD_EXC + attr in exc:
                    pytest.xfail(f'Known issue {exc}')
