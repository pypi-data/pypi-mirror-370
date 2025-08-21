"""
application core constants, helper functions and base classes
=============================================================

this module declares app-specific core constants, helper functions and base classes for all operating systems
and GUI frameworks that are supported by the ae portions namespace, in order to reduce the amount of code of
your application project (and of other ae namespace modules/portions).

.. note::
    on import of this portion, and before the app environment got initialized, it calls the function
    :func:`~ae.updater.check_all` of the :mod:`ae.updater` portion in order to prepare the app
    on the first start after their installation, and to check for updates of the app on every app start.


core constants
--------------

there are three debug level constants: :data:`DEBUG_LEVEL_DISABLED`, :data:`DEBUG_LEVEL_ENABLED` and
:data:`DEBUG_LEVEL_VERBOSE`. short names for all debug level constants are provided by the dict :data:`DEBUG_LEVELS`.
the debug level of your application can be either set in your code or optionally data-driven externally (using the
:ref:`config-files` or :ref:`config-options` of the module :mod:`ae.console`).

to use the :mod:`python logging module <logging>` in conjunction with this module, the constant :data:`LOGGING_LEVELS`
is providing a mapping between the debug levels and the python logging levels.

the encoding of strings into byte-strings (to output them to the console/stdout or to file contents) can be tricky
sometimes. to not lose any logging output because of invalid characters, this module will automatically handle any
:exc:`UnicodeEncodeError` exception for you. invalid characters will then automatically be converted to the default
encoding (specified by :data:`~ae.base.DEF_ENCODING`) with the default error handling method specified by
:data:`~ae.base.DEF_ENCODE_ERRORS` (both defined in the :mod:`ae.base` namespace portion/module).

the constants :data:`PACKAGE_NAME`, :data:`PACKAGE_DOMAIN` and :data:`PERMISSIONS` are mainly used for
apps running on mobile devices (Android or iOS). to avoid redundancies, these values get loaded and registered
from the :data:`build config file <ae.base.BUILD_CONFIG_FILE>` - if it exists in the current working directory.


core helper functions
---------------------

the :func:`print_out` function, which is fully compatible to pythons :func:`print`, is using the encoding helper
functions :func:`~ae.base.force_encoding` and :func:`~.ae.base.to_ascii` to autocorrect invalid characters.

the function :func:`hide_dup_line_prefix` is very practical if you want to remove or hide redundant line prefixes in
your log files, to make them better readable.

the two functions :func:`request_app_permissions` and :func:`start_app_service` get only implemented if your app is
running in Android OS; in other systems they are declared no-op dummy functions. the first one gets called automatically
on app start to request permissions from the app user (if not already granted), and the second one allows you
to start a background service for your app.


base class for main- and sub-app threads
----------------------------------------

to apply logging and debugging features to your application, at least one instance of the
class :class:`~ae.core.AppBase`, provided by this portion, has to be created. only the first instance
of this class created at run-time represents the main application thread, having the value `True`
in its app instance property :attr:`~ae.core.AppBase.is_main`.

additional sub-app instances of :class:`~ae.core.AppBase` can be created if your app needs separate
logging/debugging configuration for one of their sub-threads (e.g., for
web or database server threads integrated in your app).

the :meth:`~AppBase.shutdown` method will make sure that first all the created sub-thread instances will get
terminated and joined to the main app thread. additionally, all print-out buffers will be flushed into any
activated log files.


basic usage of an application base class
........................................

at the top of your python application main file/module create an instance of the class :class:`AppBase`::

    \"\"\" docstring at the top of the main module of your application \"\"\"
    from ae.core import AppBase

    __version__ = '1.2.3'

    ca = AppBase()

in the above example the :class:`AppBase` instance will automatically use the docstring title of the module as
application title and the string in the module variable __version___ as the app version. to overwrite these defaults,
pass your application title and version string via the arguments :paramref:`~AppBase.app_title` and
:paramref:`~AppBase.app_version` to the instantiation of :class:`AppBase`::

    ca = AppBase(app_title="title of this app instance", app_version='3.2.1')

other automatically initialized instance attributes of :class:`AppBase` are documented underneath in the
:class:`class docstring <AppBase>`. they include e.g., the
:attr:`date and time when the instance got created <AppBase.startup_beg>`, the
:attr:`name/id of this application instance <AppBase.app_name>` or the :attr:`application path <AppBase.app_path>`.


application class hierarchy
...........................

for most use cases you will not instantiate from :class:`AppBase` directly - instead you will instantiate one of the
extended application classes that are inherited from this base class.

the class :class:`~ae.console.ConsoleApp` e.g., inherits from :class:`AppBase` and is adding configuration options and
variables to it. so in your console application it is recommended to directly use instances of
:class:`~ae.console.ConsoleApp` instead of :class:`AppBase`.

for applications with a GUI use instead one of the classes :class:`~ae.kivy.apps.KivyMainApp`,
:class:`~ae.enaml_app.EnamlMainApp` or :class:`~ae.toga_app.TogaMainApp`.


application logging
-------------------

print-outs are an essential tool for the debugging and logging of your application at run-time. in python the print-outs
are done with the :func:`print` function or with the python :mod:`logging` module. these print-outs get sent per default
to the standard output and error streams of your OS and so displayed on your system console/shell. the :func:`print_out`
function and the :meth:`~AppBase.print_out` method of this :mod:`.core` module are adding two more sophisticated ways
for print-outs to the console/log-files.

using :class:`AppBase` is making the logging much easier and also ensures that print-outs of any imported library or
package will be included within your log files. this is done by redirecting the standard output and error streams to
your log files with the help of the :class:`_PrintingReplicator` class.

headless server applications like web servers are mostly not allowed to use the standard output streams. for some
of these applications you could redirect the standard output and error streams to a log file by using the OS redirection
character (``>``):

    python your_application.py >log_std_out.log 2>log_std_err.log

but because most web servers don't allow you to use this redirection, you can alternatively specify the
:paramref:`~AppBase.suppress_stdout` parameter as ``True`` in the instantiation of an :class:`AppBase` instance.
additionally, you can call the :meth:`~AppBase.init_logging` method to activate a log file. after that, all
the print-outs of your application and libraries will only appear in your log file.

also, in complex applications, where huge print-outs to the console can get lost easily, you want to use a log file
instead. but even a single log file can get messy to read, especially for multithreading server applications. for that,
additional sub-app/sub-thread instances of :class:`~ae.console.ConsoleApp` can be created for each thread/sub-app
in order to specify their separate/own log file configuration.

using this module ensures that any crashes or freezes happening in your application will be fully logged. apart from the
graceful handling of :exc:`UnicodeEncodeError` exceptions, the :mod:`Python faulthandler <faulthandler>` will be
enabled automatically to catch system errors and to dump a traceback of them to the console and any activated log file.


activate ae log file
....................

.. _ae-log-file:

ae log files are text files using by default the encoding of your OS console/shell. to activate the redirection of your
application print-outs into an ae log file for a :class:`AppBase` instance, you simply specify the file name of the log
file in the :meth:`~AppBase.init_logging` method call::

    app = AppBase()
    app.init_logging(log_file_name='my_log_file.log')


activate ae logging features
............................

for multithreaded applications include the thread-id of the printing thread automatically in your log files by
passing a ``True`` value to the :paramref:`~AppBase.multi_threading` argument. to additionally also suppress any
print-outs to the standard output/error streams, pass ``True`` to the :paramref:`~AppBase.suppress_stdout` argument::

    app = AppBase(multi_threading=True, suppress_stdout=True)
    app.init_logging(log_file_name='my_log_file.log')

the log files provided by this module are automatically rotating if the size of a log file succeeds the value in
MBytes defined in the :data:`LOG_FILE_MAX_SIZE`. to adapt this value to your needs, you can specify the maximum log file
size in MBytes with the argument :paramref:`~AppBase.init_logging.log_file_size_max` in your call of
:meth:`~AppBase.init_logging`::

    app.init_logging(log_file_name='my_log_file.log', log_file_size_max=9.)

by using the :class:`~ae.console.ConsoleApp` class instead of :class:`AppBase` you can alternatively store the logging
configuration of your application within a :ref:`configuration variable <config-variables>` or a
:ref:`configuration option <config-options>`. the order of precedence to find the appropriate logging configuration of
each app instance is documented :meth:`here <ae.console.ConsoleApp._init_logging>`.


using python logging module
...........................

if you prefer to use instead the python logging module for the print-outs of your application, then pass a
:mod:`python logging configuration dictionary <logging.config>` with the individual configuration of your logging
handlers, files and loggers to the :paramref:`~AppBase.init_logging.py_logging_params` argument of the
:meth:`~AppBase.init_logging` method::

    app.init_logging(py_logging_params=my_py_logging_config_dict)

passing the python logging configuration dictionary to one of the :class:`AppBase` instances created by your application
will automatically disable the ae log file of this instance.


application debugging
---------------------

the debug features of the :mod:`~ae.core` portion provide additional run-time infos as console and/or log file output.
the default debug level is set to  :data:`verbose debug output <DEBUG_LEVEL_VERBOSE>`. to change it at runtime first
import the respective :ref:`debug level constant <debug-level-constants>`.

to set the initial debug level to less verbose output, you could specify at instantiation of your :class:`AppBase` class
the :data:`DEBUG_LEVEL_ENABLED` constant onto the :paramref:`~AppBase.debug_level` argument::

    app = AppBase(..., debug_level= :data:`DEBUG_LEVEL_ENABLED`)

by passing :data:`DEBUG_LEVEL_DISABLED` constant all debug print-outs will be disabled.

alternatively, you can set or change the :attr:`~AppBase.debug_level` property at run-time after the instantiation
of the app instance. to disable debug output, use :data:`DEBUG_LEVEL_DISABLED` constant::

    app.debug_level = DEBUG_LEVEL_DISABLED

to change the debug levels dynamically and keep its last value persistent until the next app start, use the app class
:class:`~ae.console.ConsoleApp` instead of :class:`AppBase`, because :class:`~ae.console.ConsoleApp` provides the
debug level property as a :ref:`configuration file variable <config-variables>` and
as a :ref:`commend line option <config-options>`. this way you can specify
:ref:`the actual debug level <pre-defined-config-options>` without the need to change (and re-build) your
application code.

.. _debug-level-constants:

"""
import datetime
import faulthandler
import logging
import logging.config
import os
import shutil
import sys
import threading
import traceback
import weakref

from io import StringIO
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple, Union, cast

from ae.base import (  # type: ignore
    BUILD_CONFIG_FILE, DATE_TIME_ISO, DEF_ENCODE_ERRORS, PY_EXT, PY_INIT, PY_MAIN,
    build_config_variable_values, defuse, dummy_function, force_encoding, norm_path,
    os_path_basename, os_path_dirname, os_path_isdir, os_path_isfile, os_path_join, os_path_splitext, os_platform,
    read_file, stack_var, to_ascii, write_file)
from ae.paths import (                                                                                  # type: ignore
    PATH_PLACEHOLDERS, add_common_storage_paths, app_data_path, app_docs_path, app_name_guess, normalize)
from ae.updater import check_all                                                                        # type: ignore


__version__ = '0.3.74'


# package and permissions handling defaults for all platforms and frameworks
PACKAGE_NAME = stack_var('__name__') or 'unspecified_package'                       #: package name default
PACKAGE_DOMAIN = 'org.test'                                                         #: package domain default
PERMISSIONS = "INTERNET,VIBRATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE"
if os_path_isfile(BUILD_CONFIG_FILE):                           # pragma: no cover
    PACKAGE_NAME, PACKAGE_DOMAIN, PERMISSIONS = build_config_variable_values(
        ('package.name', PACKAGE_NAME),
        ('package.domain', PACKAGE_DOMAIN),
        ('android.permissions', PERMISSIONS))
elif os_platform == 'android':                                  # pragma: no cover
    _importing_package = norm_path(stack_var('__file__') or 'empty_package' + PY_EXT)
    if os_path_basename(_importing_package) in (PY_INIT, PY_MAIN):
        _importing_package = os_path_dirname(_importing_package)
    _importing_package = os_path_splitext(os_path_basename(_importing_package))[0]
    write_file(f'{_importing_package}_debug.log', f"{BUILD_CONFIG_FILE} not bundled - using defaults\n", extra_mode='a')


if os_platform == 'android':  # pragma: no cover
    # import permissions module from python-for-android (recipes/android/src/android/permissions.py)
    # noinspection PyUnresolvedReferences
    from android.permissions import request_permissions, Permission     # type: ignore # pylint: disable=import-error
    from jnius import autoclass                                         # type: ignore

    def request_app_permissions(callback: Optional[Callable[[List[Permission], List[bool]], None]] = None):
        """ request app/service permissions on Android OS.

        :param callback:        optional callback receiving two list arguments with identical length,
                                the 1st with the requested permissions and
                                the 2nd with booleans stating if the permission got granted (True) or rejected (False).
        """
        permissions = []
        for permission_str in PERMISSIONS.split(','):
            permission = getattr(Permission, permission_str.strip(), None)
            if permission:
                permissions.append(permission)
        request_permissions(permissions, callback=callback)

    def start_app_service(service_arg: str = "") -> Any:
        """ start service.

        :param service_arg:     string to be assigned to environment variable PYTHON_SERVICE_ARGUMENT on service start.
        :return:                service instance.

        links to other android code and service examples and documentation:

            * `https://python-for-android.readthedocs.io/en/latest/`__
            * `https://github.com/kivy/python-for-android/tree/develop/pythonforandroid/recipes/android/src/android`__
            * `https://github.com/tshirtman/kivy_service_osc/blob/master/src/main.py`__
            * `https://python-for-android.readthedocs.io/en/latest/services/#arbitrary-scripts-services`__
            * `https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/`__
            * `https://github.com/Android-for-Python/Android-for-Python-Users`__
            * `https://github.com/Android-for-Python/INDEX-of-Examples`__

        big thanks to `Robert Flatt <https://github.com/RobertFlatt>`__ for his investigations, findings and
        documentations to code and build Kivy apps for the Android OS, and to
        `Gabriel Pettier <https://github.com/tshirtman>`__ for his service osc example.

        """
        service_instance = autoclass(f"{PACKAGE_DOMAIN}.{PACKAGE_NAME}.Service{PACKAGE_NAME.capitalize()}")
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        service_instance.start(activity, service_arg)        # service_arg will be in env var PYTHON_SERVICE_ARGUMENT

        return service_instance

    request_app_permissions()   # if not yet granted, then request permissions from the app user on (first) app start

else:
    request_app_permissions = dummy_function
    start_app_service = dummy_function


# DON'T RE-ORDER: using module doc-string as _debug-level-constants sphinx hyperlink to the following DEBUG_ constants:
DEBUG_LEVEL_DISABLED: int = 0       #: lowest debug level - only display logging levels ERROR/CRITICAL.
DEBUG_LEVEL_ENABLED: int = 1        #: minimum debugging info - display logging levels WARNING or higher.
DEBUG_LEVEL_VERBOSE: int = 2        #: verbose debug info - display logging levels INFO/DEBUG or higher.

DEBUG_LEVELS: Dict[int, str] = {DEBUG_LEVEL_DISABLED: 'disabled', DEBUG_LEVEL_ENABLED: 'enabled',
                                DEBUG_LEVEL_VERBOSE: 'verbose'}
""" numeric ids and names of all supported debug levels. """

LOGGING_LEVELS: Dict[int, int] = {DEBUG_LEVEL_DISABLED: logging.WARNING, DEBUG_LEVEL_ENABLED: logging.INFO,
                                  DEBUG_LEVEL_VERBOSE: logging.DEBUG}
""" association between ae debug levels and python logging levels. """

HIDDEN_CREDENTIALS = ('password', 'token')      #: credential keys that are hidden in print/repr output (not if verbose)


def hide_dup_line_prefix(last_line: str, current_line: str) -> str:
    """ replace duplicate characters at the start of two strings with spaces.

    :param last_line:       last line string (e.g., the last line of the text/log file).
    :param current_line:    current line string.
    :return:                current line string but duplicate characters at the beginning are replaced by space chars.
    """
    idx = 0
    min_len = min(len(last_line), len(current_line))
    while idx < min_len and last_line[idx] == current_line[idx]:
        idx += 1
    return " " * idx + current_line[idx:]


MAX_NUM_LOG_FILES: int = 69                         #: maximum number of :ref:`ae log files <ae-log-file>`
LOG_FILE_MAX_SIZE: int = 15                         #: maximum size in MB of rotating :ref:`ae log files <ae-log-file>`
LOG_FILE_IDX_WIDTH: int = len(str(MAX_NUM_LOG_FILES)) + 3
""" width of rotating log file index within log file name; adding +3 to ensure index range up to factor 10^3. """

ori_std_out: TextIO = sys.stdout                    #: original sys.stdout on app startup
ori_std_err: TextIO = sys.stderr                    #: original sys.stderr on app startup

log_file_lock: threading.RLock = threading.RLock()  #: log file rotation multi-threading lock


_LOGGER = None       #: python logger for this module gets lazy/late initialized and only if requested by caller


def logger_late_init():
    """ check if logging modules got initialized already and if not, then do it now. """
    global _LOGGER                                      # pylint: disable=global-statement
    if not _LOGGER:
        _LOGGER = logging.getLogger(__name__)           # reset (_LOGGER = None) done in _unregister_app_instance()


_MULTI_THREADING_ACTIVATED: bool = False                #: flag if threading is used in your application


def activate_multi_threading():
    """ activate multi-threading for all app instances (normally done at the main app startup). """
    global _MULTI_THREADING_ACTIVATED                   # pylint: disable=global-statement
    _MULTI_THREADING_ACTIVATED = True


def _deactivate_multi_threading():
    """ disable multi threading (needed to reset the app environment in unit testing). """
    global _MULTI_THREADING_ACTIVATED                   # pylint: disable=global-statement
    _MULTI_THREADING_ACTIVATED = False


def print_out(*objects, sep: str = " ", end: str = "\n", file: Optional[TextIO] = None, flush: bool = False,
              encode_errors_def: str = DEF_ENCODE_ERRORS, logger: Optional['logging.Logger'] = None,
              app: Optional['AppBase'] = None, **kwargs):
    """ universal/unbreakable print function - replacement for the :func:`built-in python function print() <print>`.

    :param objects:             tuple of objects to be printed. if the first object is a string that starts with a
                                carriage return character (\\\\r), then the print-out will be only sent to the standard
                                output (and will not be added to any active log files - see also
                                :paramref:`~print_out.end` argument).
    :param sep:                 separator character between each printed object/string (defaults to a space char).
    :param end:                 finalizing character added to the end of this print-out (defaults to a
                                new-line char/\\\\n). pass a carriage-return char (\\\\r) in order to
                                suppress the print-out into :ref:`ae log file <ae-log-file>` or to any activated python
                                logger - useful for console/shell processing animation (see :meth:`.tcp.TcpServer.run`).
    :param file:                output stream object to be printed to (def=None which will use standard output streams).
                                if given, then the redirection to all active log files and python logging loggers
                                will be disabled (even if the :paramref:`~print_out.logger` argument is specified).
    :param flush:               flush stream after printing (def=False).
    :param encode_errors_def:   default error handling to encode (def=:data:`DEF_ENCODE_ERRORS`).
    :param logger:              used logger to output `objects` (def=None). ignored if the :paramref:`~print_out.file`
                                argument gets specified/passed.
    :param app:                 the app instance from where this print-out got initiated.
    :param kwargs:              catch unsupported kwargs for debugging (all items will be printed to all the activated
                                logging/output streams).

    this function is silently handling and autocorrecting string encode errors for output/log streams which are not
    supporting Unicode. any instance of :class:`AppBase` is providing this function as a method with the
    :func:`same name <AppBase.print_out>`. it is recommended to call/use this instance method instead of this function.

    in multithreading applications this function prevents dismembered/fluttered print-outs from different threads.

    .. note:: this function has an alias named :func:`.po`.
    """
    processing = end == "\r" or (objects and str(objects[0]).startswith('\r'))  # True if called by Progress.next()
    enc = getattr(file or ori_std_out if processing else sys.stdout, 'encoding', 'utf-8')
    use_py_logger = False

    main_app = main_app_instance()
    if main_app:
        file = main_app.log_file_check(file)    # check if late init of the logging system is needed
    if app and app != main_app:
        file = app.log_file_check(file)         # check sub-app suppress_stdout/log file status and rotation
    else:
        app = main_app

    if processing:
        file = ori_std_out
    elif logger is not None and file is None and (
            app and app.py_log_params and main_app != app or main_app and main_app.py_log_params):
        use_py_logger = True
        logger_late_init()

    if kwargs:
        objects += (f"\n   *  EXTRA KWARGS={kwargs}", )

    retries = 2
    while retries:
        try:
            print_strings = tuple(map(lambda _: str(_).encode(enc, errors=encode_errors_def).decode(enc), objects))
            if use_py_logger or _MULTI_THREADING_ACTIVATED:
                # concatenating objects also prevents fluttered log file content in multi-threading apps
                # see https://stackoverflow.com/questions/3029816/how-do-i-get-a-thread-safe-print-in-python-2-6
                # and https://stackoverflow.com/questions/50551637/end-key-in-print-not-thread-safe
                print_one_str = sep.join(print_strings)
                sep = ""
                if end and (not use_py_logger or end != '\n'):
                    print_one_str += end
                    end = ""
                print_strings = (print_one_str, )

            if use_py_logger:
                debug_level = app.debug_level if app else DEBUG_LEVEL_VERBOSE
                if logger:      # mypy insists on have this extra check, although `use_py_logger` is including logger
                    logger.log(level=LOGGING_LEVELS[debug_level], msg=print_strings[0])
            else:
                print(*print_strings, sep=sep, end=end, file=file, flush=flush)
            break
        except UnicodeEncodeError:
            fixed_objects = []
            for obj in objects:
                if not isinstance(obj, str) and not isinstance(obj, bytes):
                    obj = str(obj)
                if retries == 2:
                    obj = force_encoding(obj, encoding=enc)
                else:
                    obj = to_ascii(obj)
                fixed_objects.append(obj)
            objects = tuple(fixed_objects)
            retries -= 1
        except (IOError, OSError, ValueError, Exception):   # pragma: no cover # pylint: disable=broad-except
            traceback.print_exc()
            print("...... in ae.core.print_out(", objects, ")")
            break


APP_KEY_SEP: str = '@'      #: separator character used in :attr:`~AppBase.app_key` of :class:`AppBase` instance

# had to use type comment because the following line is throwing an error in the Sphinx docs make:
# _APP_INSTANCES: weakref.WeakValueDictionary[str, "AppBase"] = weakref.WeakValueDictionary()
_APP_INSTANCES = weakref.WeakValueDictionary()   # type: weakref.WeakValueDictionary[str, AppBase]
""" dict that is weakly holding references to all :class:`AppBase` instances created at run time.

gets automatically initialized in :meth:`AppBase.__init__` to allow log file split/rotation
and debug_level access at application thread or module level.

the first created :class:`AppBase` instance is called the main app instance. :data:`_MAIN_APP_INST_KEY`
stores the dict key of the main instance.
"""
_MAIN_APP_INST_KEY: str = ''    #: key in :data:`_APP_INSTANCES` of main :class:`AppBase` instance

app_inst_lock: threading.RLock = threading.RLock()  #: app instantiation multi-threading lock


def main_app_instance() -> Optional['AppBase']:
    """ determine the main instance of the :class:`AppBase` in the current running application.

    :return:                    the main and first-instantiated :class:`AppBase` instance or None (if the app is not
                                fully initialized yet).
    """
    with app_inst_lock:
        return _APP_INSTANCES.get(_MAIN_APP_INST_KEY)


def registered_app_names() -> List[str]:
    """ determine the app names of all registered/running applications. """
    with app_inst_lock:
        return [app.app_name for app in _APP_INSTANCES.values()]


def _register_app_instance(app: 'AppBase'):
    """ register new :class:`AppBase` instance in :data:`_APP_INSTANCES`.

    :param app:                 :class:`AppBase` instance to register
    """
    with app_inst_lock:
        global _MAIN_APP_INST_KEY                       # pylint: disable=global-statement
        msg = f"register_app_instance({app}) expects "
        assert app not in _APP_INSTANCES.values(), msg + "new instance - this app got already registered"

        key = app.app_key
        assert key and key not in _APP_INSTANCES, \
            msg + f"non-empty, unique app key (app_name+sys_env_id=={key} keys={list(_APP_INSTANCES.keys())})"

        cnt = len(_APP_INSTANCES)
        if _MAIN_APP_INST_KEY:
            assert cnt > 0, f"No app instances registered but main app key is set to {_MAIN_APP_INST_KEY}"
        else:
            assert cnt == 0, f"{cnt} sub-apps {list(_APP_INSTANCES.keys())} found after main app remove"
            _MAIN_APP_INST_KEY = key
        _APP_INSTANCES[key] = app


def _unregister_app_instance(app_key: str) -> Optional['AppBase']:
    """ unregister/remove :class:`AppBase` instance from within :data:`_APP_INSTANCES`.

    :param app_key:             app key of the instance to remove.
    :return:                    removed :class:`AppBase` instance.
    """
    with app_inst_lock:
        global _LOGGER                                  # pylint: disable=global-statement
        _LOGGER = None

        global _MAIN_APP_INST_KEY                       # pylint: disable=global-statement
        app = _APP_INSTANCES.pop(app_key, None)
        cnt = len(_APP_INSTANCES)
        if app_key == _MAIN_APP_INST_KEY:
            _MAIN_APP_INST_KEY = ''
            assert cnt == 0, f"{cnt} sub-apps {list(_APP_INSTANCES.keys())} found after main app {app_key}{app} remove"
        elif _MAIN_APP_INST_KEY:
            assert cnt > 0, f"Unregistered last app {app_key}/{app} but was not the main app {_MAIN_APP_INST_KEY}"

        return app


def _shut_down_sub_app_instances(timeout: Optional[float] = None):
    """ shut down all sub-thread/sub-app instances.

    :param timeout:             timeout float value in seconds used for the sub-app shutdowns and for the
                                acquisition of the threading locks of :data:`the ae log file <log_file_lock>` and the
                                :data:`app instances <app_inst_lock>`.
    """
    aqc_kwargs: Dict[str, Any] = ({'blocking': False} if timeout is None else {'timeout': timeout})
    blocked = app_inst_lock.acquire(**aqc_kwargs)           # pylint: disable=consider-using-with
    for app in reversed(list(_APP_INSTANCES.values())):     # list() because the weak ref dict gets changed in the loop
        if not app.is_main:
            app.shutdown(timeout=timeout)
    if blocked:
        app_inst_lock.release()


class _PrintingReplicator:
    """ replacement of standard/error stream replicating print-outs to all active logging streams (log files/buffers).
    """
    def __init__(self, sys_out_obj: TextIO = ori_std_out) -> None:
        """ initialise a new T-stream-object

        :param sys_out_obj:     standard output/error stream to be replicated (def=sys.stdout)
        """
        self.sys_out_obj = sys_out_obj

    def write(self, any_str: Union[str, bytes]) -> None:
        """ write string to ae logging and standard output streams.

        automatically suppressing UnicodeEncodeErrors if the console/shell or log file has different encoding by forcing
        re-encoding with DEF_ENCODE_ERRORS.

        :param any_str:         string or bytes to output.
        """
        message = any_str.decode() if isinstance(any_str, bytes) else any_str
        app_streams: List[Tuple[Optional[AppBase], TextIO]] = []
        with log_file_lock, app_inst_lock:
            for app in list(_APP_INSTANCES.values()):
                stream = app.log_file_check(app.active_log_stream)  # check if log rotation or buf-to-file-switch needed
                if stream:
                    app_streams.append((app, stream))
            if not self.sys_out_obj.closed:
                app_streams.append((main_app_instance(), self.sys_out_obj))

            if message and message[0] != '\n' and message[-1] == '\n':
                message = '\n' + message[:-1]
            log_lines = message.split('\n')
            for app_or_none, stream in app_streams:
                line_prefix = '\n' + (app_or_none.log_line_prefix() if app_or_none else '')
                app_msg = line_prefix.join(log_lines)
                try:
                    stream.write(app_msg)
                except UnicodeEncodeError:
                    stream.write(force_encoding(app_msg, encoding=stream.encoding))

    def __getattr__(self, attr: str) -> Any:
        """ get attribute value from the standard output stream.

        :param attr:            name of the attribute to retrieve/return.
        :return:                value of the attribute.
        """
        return getattr(self.sys_out_obj, attr)


_APP_THREADS = weakref.WeakValueDictionary()   # type: weakref.WeakValueDictionary[int, threading.Thread]
""" weak dict to keep the references of all application threads. added to prevent
the joining of unit testing threads in the test teardown (resetting app environment). """


def _register_app_thread():
    """ add a new app thread to _APP_THREADS if not already added. """
    tid = threading.get_ident()
    if tid not in _APP_THREADS:
        _APP_THREADS[tid] = threading.current_thread()


def _join_app_threads(timeout: Optional[float] = None):
    """ join/finish all app threads and finally deactivate multi-threading.

    :param timeout:             timeout float value in seconds for thread joining (def=None - block/no-timeout).

    .. note:: this function has to be called by the main app instance only.
    """
    main_thread = threading.current_thread()
    for app_thread in reversed(list(_APP_THREADS.values())):    # threading.enumerate() includes PyCharm/pytest threads
        if app_thread is not main_thread:
            print_out(f"  **  joining thread id <{app_thread.ident: >6}> name={app_thread.getName()}", logger=_LOGGER)
            app_thread.join(timeout)
            if app_thread.ident is not None:     # mypy needs it because ident is Optional
                _APP_THREADS.pop(app_thread.ident)
    _deactivate_multi_threading()


class AppBase:
    """ provides easy logging and debugging for your application.

    most applications only need a single instance of this class; apps with threads could create separate instances
    for each thread.

    instance Attributes (ordered alphabetically - ignoring underscore characters):

    * :attr:`app_key` id/key of this application instance.
    * :attr:`app_name` basename (without the file name extension) of the executable.
    * :attr:`app_path` file path of app executable.
    * :attr:`app_title` application title/description.
    * :attr:`app_version` application version (set via the :paramref:`AppBase.app_version` argument).
    * :attr:`debug_level` debug level of this instance.
    * :attr:`_last_log_line_prefix` last ae log file line prefix that got print-out to the log of this app instance.
    * :attr:`_log_buf_stream` ae log file buffer stream.
    * :attr:`_log_file_index` index of the current rotation ae log file backup.
    * :attr:`_log_file_name` path and file name of the ae log file.
    * :attr:`_log_file_size_max` maximum size in MBytes of an ae log file.
    * :attr:`_log_file_stream` ae log file TextIO output stream.
    * :attr:`_log_with_timestamp` log timestamp line prefix if True or a non-empty strftime compatible format string.
    * :attr:`py_log_params` python logging config dictionary.
    * :attr:`_nul_std_out` null stream used to prevent print-outs to :attr:`standard output <sys.stdout>`.
    * :attr:`_shut_down` flag set to True if this application instance got already shutdown.
    * :attr:`startup_beg` datetime of the start of instantiation/startup of this app instance.
    * :attr:`startup_end` datetime of the end of the instantiation/startup of this application instance.
    * :attr:`suppress_stdout` flag set to True if this application does not print to stdout/console.
    * :attr:`sys_env_id` system environment id of this application instance.
    """
    app_title: str = ""                             #: title/description of this app instance
    app_name: str = ''                              #: name of this app instance
    app_version: str = ''                           #: version of this app instance
    _debug_level: int = DEBUG_LEVEL_VERBOSE         #: debug level of this app instance
    sys_env_id: str = ''                            #: system environment id of this app instance
    suppress_stdout: bool = True                    #: flag to suppress prints to stdout
    startup_end: Optional[datetime.datetime] = None  #: end datetime of the application startup
    _last_log_line_prefix: str = ""                 #: prefix of the last printed log line
    _log_buf_stream: Optional[StringIO] = None      #: log file buffer stream instance
    _log_file_stream: Optional[TextIO] = None       #: log file stream instance
    _log_file_index: int = 0                        #: log file index (for rotating logs)
    _log_file_size_max: float = LOG_FILE_MAX_SIZE   #: maximum log file size in MBytes (rotating log files)
    _log_file_name: str = ""                        #: log file name
    _log_with_timestamp: Union[bool, str] = False   #: True of strftime format string to enable timestamp
    _nul_std_out: Optional[TextIO] = None           #: logging null stream
    py_log_params: Dict[str, Any] = {}              #: dict of config parameters for py logging
    _shut_down: bool = False                        #: True if this app instance got shut down already

    def __init__(self, app_title: str = '', app_name: str = '', app_version: str = '', sys_env_id: str = '',
                 debug_level: int = DEBUG_LEVEL_VERBOSE, multi_threading: bool = False, suppress_stdout: bool = False):
        """ initialize a new :class:`AppBase` instance.

        :param app_title:       application title/description setting the attribute :attr:`~ae.core.AppBase.app_title`.
                                if not specified, then the docstring of your app's main module will be used (see
                                :ref:`example <app-title>`).
        :param app_name:        application instance name to set the attribute :attr:`~ae.core.AppBase.app_name`. if not
                                 specified, then the base name of the main module file name will be used.
        :param app_version:     application version string to set the attribute :attr:`~ae.core.AppBase.app_version`. if
                                not specified, then the value of a global variable with the name `__version__` will be
                                used (if declared in the actual call stack).
        :param sys_env_id:      system environment id to set the instance attribute :attr:`~ae.core.AppBase.sys_env_id`.
                                the default value of this argument is an empty string.
        :param debug_level:     default debug level to set the instance attribute :attr:`~ae.core.AppBase.debug_level`.
                                the default value of this argument is :data:`~ae.core.DEBUG_LEVEL_DISABLED`.
        :param multi_threading: pass True if this instance will be used in a multi-threading app.
        :param suppress_stdout: pass True (for wsgi apps) to prevent any python print outputs to stdout.
        """
        self.startup_beg: datetime.datetime = datetime.datetime.now()   #: begin of app startup datetime
        app_path = sys.argv[0]
        if not os_path_isdir(app_path):                 # if it is a console app module (not a package)
            app_path = os_path_dirname(app_path)        # .. then remove the module file name
        self.app_path: str = norm_path(app_path)        #: path to the folder of your main app code file

        if not app_title:
            doc_str = stack_var('__doc__')
            app_title = doc_str.strip().split('\n')[0] if doc_str else ""
        self.app_title: str = app_title                                         #: title of this app instance
        self.app_name: str = app_name or app_name_guess()                       #: name of this app instance
        self.app_version: str = app_version or stack_var('__version__') or ""   #: version of this app instance
        self._debug_level: int = debug_level                                    #: debug level of this app instance
        self.sys_env_id: str = sys_env_id                                       #: system environment id of this app

        if multi_threading:
            activate_multi_threading()

        self.suppress_stdout: bool = suppress_stdout                            #: flag to suppress prints to stdout
        self.startup_end: Optional[datetime.datetime] = None                    #: end datetime of the app startup

        _register_app_thread()
        _register_app_instance(self)

        if self.is_main:                                # if this instance is the main/first app instance
            self._init_path_placeholders()              # .. then init PATH_PLACEHOLDERS

            app_path, cwd_path = norm_path(app_path), norm_path(os.getcwd())
            if app_path == cwd_path:                    # if this app is not a dev-tool/grm # pragma: no cover
                destination_files = check_all()         # then prepare the app on first-run after install/ubgrade
                self.vpo(f"AppBase.__init__() updated {len(destination_files)} {destination_files=}")
            else:                                                                           # pragma: no cover
                self.vpo(f"AppBase.__init__() upgrade check skipped because {app_path=} != {cwd_path=}")

    def _init_path_placeholders(self):
        """ correct app_name/main_app_name, the related path placeholders and ensure write access for some of them. """
        # correct app name guess, init by :mod:`ae.paths` (main app from ("", 'pyTstConsAppKey', '_jb_pytest_runner'))
        PATH_PLACEHOLDERS['main_app_name'] = PATH_PLACEHOLDERS['app_name'] = app_name = self.app_name
        PATH_PLACEHOLDERS['app'] = app_data_path()
        PATH_PLACEHOLDERS['ado'] = app_docs_path()

        add_common_storage_paths()  # determine platform-specific path placeholders, like e.g. {pictures}, {documents}..

        # to unmask in :meth:`ae.core.AppBase.__init__`/:meth:`ae.updater.check_all` the masked .apk extension of the
        # APK, embedded via grm-build_gui_app action, because buildozer/p4a does not embed it having an .apk extension
        if os_platform == 'android':    # only needed for APKs on Android OS; not needed for AAR app packages
            PATH_PLACEHOLDERS['apk_ext'] = 'apk'                                            # pragma: no cover

        # check folder/file write access for placeholders {ado}, {doc}, {documents}, and {downloads}; to be
        # corrected/redirected to subfolder of {videos}, {pictures}, {usr}, especially if os_platform=='android'
        # version > 12 / API-level > 33 (adding the android app permission MANAGE_EXTERNAL_STORAGE did not help)
        file_content = "check right file content"
        for placeholder in [_ for _ in ('ado', 'doc', 'documents', 'downloads') if _ in PATH_PLACEHOLDERS]:
            name = f'check_write_access_on_{placeholder}'
            cph_path = normalize('{' + placeholder + '}')
            cph_exists = os_path_isdir(cph_path)
            chk_path = os_path_join(cph_path, f"{name}_dir")
            chk_file = os_path_join(chk_path, f"{name}_file_{defuse('svc://chk_usr:chk_pw@chk_host/chk_path')}")
            err_msg = f"{chk_path=}"
            access = False
            try:
                write_file(chk_file, file_content, make_dirs=True)
                assert os_path_isfile(chk_file)
                access = read_file(chk_file) == file_content
                assert access
            except (AssertionError, PermissionError, Exception) as chk_ex:  # pylint: disable=broad-except
                err_msg += f": {chk_ex=!r}"
                for alternative in [_ for _ in ('documents', 'videos', 'pictures', 'usr')
                                    if _ != placeholder and _ in PATH_PLACEHOLDERS]:
                    aph_path = normalize('{' + alternative + '}')
                    aph_exists = os_path_isdir(aph_path)
                    alt_path = os_path_join(aph_path, app_name + "_" + placeholder)
                    alt_file = os_path_join(alt_path, f"{name}_file_{defuse('svc://chk_usr:chk_pw@chk_host/chk_path')}")
                    try:
                        write_file(alt_file, file_content, make_dirs=True)
                        assert os_path_isfile(alt_file)
                        access = read_file(alt_file) == file_content
                        assert access
                    except (AssertionError, PermissionError, Exception) as alt_ex:  # pylint: disable=broad-except
                        err_msg += f"; {alternative=} access error {alt_ex=} for {alt_file=}"
                    finally:
                        if access and os_path_isfile(alt_file):
                            os.remove(alt_file)         # leave just created alt_path folder in place
                        else:
                            shutil.rmtree(alt_path if aph_exists else aph_path, ignore_errors=True)
                    if access:
                        PATH_PLACEHOLDERS[placeholder] = alt_path
                        self.vpo(f"redirected path {placeholder=} from write protected {chk_path=} to {alt_path=}")
                        break
            finally:
                shutil.rmtree(chk_path if cph_exists else cph_path, ignore_errors=True)
            if not access:
                self.po(f"AppBase._init_path_placeholder ignored {placeholder=} errors: {err_msg}")

    def __del__(self):
        """ deallocate this app instance by calling :func:`AppBase.shutdown`.
        """
        self.shutdown(exit_code=None)

    @property
    def active_log_stream(self) -> Optional[Union[StringIO, TextIO]]:
        """ check if ae logging is active and if yes, then return the currently used log stream (read-only property).

        :return:                log file or buf stream if logging is activated, else None.
        """
        with log_file_lock:
            return self._log_file_stream or self._log_buf_stream

    @property
    def app_key(self) -> str:
        """ determine the key of this application class instance (read-only property).

        :return:                application key string.
        """
        return self.app_name + APP_KEY_SEP + self.sys_env_id

    @property
    def debug_level(self) -> int:
        """ debug level property:

        :getter:                return the current debug level of this app instance.
        :setter:                change the debug level of this app instance.
        """
        return self._debug_level

    @debug_level.setter
    def debug_level(self, debug_level: int):
        """ debug level setter (added for easier overwrite in inheriting classes). """
        self._debug_level = debug_level

    @property
    def debug(self) -> bool:
        """ True if the app is in debug mode. """
        return self._debug_level >= DEBUG_LEVEL_ENABLED

    @property
    def is_main(self) -> bool:
        """ True if this app instance is the main/first one or if there is already no main app instance. """
        return main_app_instance() in (None, self)

    @property
    def verbose(self) -> bool:
        """ True if the app is in verbose debug mode. """
        return self._debug_level >= DEBUG_LEVEL_VERBOSE

    def call_method(self, callback: Union[Callable, str], *args, **kwargs) -> Any:
        """ call passed callable/method with the passed args, catching and logging exceptions preventing app exit.

        :param callback:            either a callable or the name of the main app method of this instance to call.
        :param args:                args passed to the main app method to be called.
        :param kwargs:              kwargs passed to the main app method to be called.
        :return:                    the return value of the called method
                                    or None if the callback method throws exception/does not exist.
        """
        if isinstance(callback, str):
            callback = getattr(self, callback, None)    # type: ignore
            if callback is None:
                return None

        try:
            return callback(*args, **kwargs)            # type: ignore
        except (AttributeError, LookupError, TypeError, ValueError, Exception) as ex:  # pylint: disable=broad-except
            self.po(f" ***  AppBase.call_method({callback}, {args}, {kwargs}): {ex}\n{traceback.format_exc()}")

        return None

    def init_logging(self, py_logging_params: Optional[Dict[str, Any]] = None, log_file_name: str = "",
                     log_file_size_max: float = LOG_FILE_MAX_SIZE, log_with_timestamp: Union[bool, str] = False,
                     disable_buffering: bool = False):
        """ initialize the logging system.

        :param py_logging_params:   config dict for python logging configuration. if this dict is not empty, then python
                                    logging is configured with the given options in this dict and all the other kwargs
                                    are ignored.
        :param log_file_name:       default log file name for ae logging (def='' - ae logging disabled).
        :param log_file_size_max:   max. size in MB of ae log file (def=LOG_FILE_MAX_SIZE).
        :param log_with_timestamp:  add a timestamp prefix to each log line if True or a non-empty strftime compatible
                                    format string.
        :param disable_buffering:   pass True to disable ae log buffering at app startup.

        log files and config values will be initialized as late as possible in :meth:`~AppBase.log_file_check`, e.g.,
        indirectly triggered by a request to a config variable via :meth:`~AppBase._parse_args` (like `logFile`).
        """
        with log_file_lock:
            if py_logging_params:                   # init python logging - app is using python logging module
                logger_late_init()
                # logging.basicConfig(level=logging.DEBUG, style='{')
                logging.config.dictConfig(py_logging_params)     # re-configure py logging module
                self.py_log_params = py_logging_params
            else:                                   # (re-)init ae logging
                if self._log_file_stream:
                    self._close_log_file()
                    self._std_out_err_redirection(False)
                self._log_file_name = log_file_name
                self._log_file_size_max = log_file_size_max
                self._log_with_timestamp = log_with_timestamp
                if not disable_buffering:
                    self._log_buf_stream = StringIO(initial_value="####  Log Buffer\n" if self.debug else "")

    def log_line_prefix(self) -> str:
        """ compile prefix of log print-out line for this :class:`AppBase` instance.

        the line prefix consists of (depending on the individual values of either a module variable or of an
        attribute this app instance):

        * :data:`_MULTI_THREADING_ACTIVATED`: if True, then the thread id gets printed surrounded with
          angle brackets (< and >), right aligned and space padded to A minimum of 6 characters.
        * :attr:`sys_env_id`: if not empty, then printed surrounded with curly brackets ({ and }), left aligned
          and space padded to a minimum of 4 characters.
        * :attr:`_log_with_timestamp`: if (a) True or (b) a non-empty string, then the system time
          (determined with :meth:`~datetime.datetime.now`) gets printed in the format specified either by
          (a) the :data:`~ae.base.DATE_TIME_ISO` constant or (b) the string in this attribute.

        this method is using the instance attribute :attr:`_last_log_line_prefix` to keep a copy of
        the last printed log line prefix to prevent the printout of duplicate characters in consecutive
        log lines.

        :return:                log file line prefix string including one space as a separator character at the end.
        """
        parts = []
        if _MULTI_THREADING_ACTIVATED:
            parts.append(f"<{threading.get_ident(): >6}>")
        if self.app_key[-1] != APP_KEY_SEP:
            parts.append(f"{{{self.app_key: <6}}}")
        if self._log_with_timestamp:
            format_string = DATE_TIME_ISO if isinstance(self._log_with_timestamp, bool) else self._log_with_timestamp
            parts.append(datetime.datetime.now().strftime(format_string))
        if self.debug:
            parts.append(f"[{DEBUG_LEVELS[self.debug_level][0]}]")

        prefix = "".join(parts)
        with log_file_lock:
            last_pre = self._last_log_line_prefix
            self._last_log_line_prefix = prefix

        return hide_dup_line_prefix(last_pre, prefix) + " "

    def log_file_check(self, curr_stream: Optional[TextIO] = None) -> Optional[TextIO]:
        """ check and possibly correct log file status and the passed currently used stream.

        :param curr_stream:     currently used stream.
        :return:                stream passed into :paramref:`~log_file_check.curr_stream` or
                                new/redirected stream of :paramref:`~log_file_check.curr_stream` or
                                None if :paramref:`~log_file_check.curr_stream` is None.

        for already opened log files, check if the log file is big enough, and if yes, then do a file rotation. if the
        log file is not opened but the log file name got already set, then check if the log startup buffer is active,
        and if yes, then create a new log file, pass log buffer content to it and close the log buffer.
        """
        old_stream = new_stream = None
        with log_file_lock:
            if self._log_file_stream:
                old_stream = self._log_file_stream
                self._log_file_stream.seek(0, 2)  # seek EOF due to the non-posix-compliant Windows feature
                if self._log_file_stream.tell() >= self._log_file_size_max * 1024 * 1024:
                    self._close_log_file()
                    self._rename_log_file()
                    self._open_log_file()
                    new_stream = self._log_file_stream
            elif self._log_file_name:
                old_stream = self._log_buf_stream
                self._open_log_file()
                self._std_out_err_redirection(True)
                self._flush_and_close_log_buf()
                new_stream = self._log_file_stream
            elif self.suppress_stdout and not self._nul_std_out:    # pragma: no cover/_std_out_err_redirection does it
                old_stream = sys.stdout
                # pylint: disable-next=unspecified-encoding, consider-using-with
                sys.stdout = self._nul_std_out = new_stream = open(os.devnull, 'w')

        if curr_stream == old_stream and new_stream:
            return new_stream
        return curr_stream

    def print_out(self, *objects, file: Optional[TextIO] = None, **kwargs):
        """ app-instance-specific print-outs.

        :param objects:         objects to be printed out.
        :param file:            output stream object to be printed to (def=None). passing None on a main app instance
                                will print the objects to the standard output and any active log files. on the contrary,
                                on a sub-app/sub-thread instance with an active log file, the print-out
                                will get redirected exclusively/only to the log file of this sub-app instance.
        :param kwargs:          all the other supported kwargs of this method are documented
                                :func:`at the print_out() function of this module <print_out>`.

        this method has an alias named :meth:`.po`
        """
        if file is None and main_app_instance() is not self:    # self.is_main==True when main_app_instance() is None
            with log_file_lock:
                file = self._log_buf_stream or self._log_file_stream
        if file:
            kwargs['file'] = file
        if 'app' not in kwargs:
            kwargs['app'] = self
        print_out(*objects, **kwargs)

    po = print_out          #: alias of method :meth:`.print_out`

    def debug_out(self, *objects, minimum_debug_level: int = DEBUG_LEVEL_ENABLED, **kwargs):
        """ special debug version of :func:`builtin print() function <print>`.

        this method will print out the passed objects only if the :attr:`current debug level
        <.core.AppBase.debug_level>` of this app instance is higher than the value passed into the
        :paramref:`~debug_out.minimum_debug_level` argument. in this case the print-out will be
        delegated onto the :meth:`~.print_out`.

        :param objects:             objects to be printed out.
        :param minimum_debug_level: minimum debug level to print the passed objects.
        :param kwargs:              all the supported kwargs of this method are documented at the
                                    :func:`print_out() function <core.print_out>` of the :mod:`~ae.core` module
                                    (including the :paramref:`~.print_out.file` argument).

        this method has an alias named :meth:`.dpo`.
        """
        if self.debug_level >= minimum_debug_level:
            self.po(*objects, **kwargs)

    dpo = debug_out         #: alias of method :meth:`.debug_out`

    def verbose_out(self, *objects, **kwargs):
        """ special verbose debug version of :func:`builtin print() function <print>`.

        :param objects:         objects to be printed out.
        :param kwargs:          the :paramref:`~.core.AppBase.print_out.file` argument is documented at the
                                :meth:`~.core.AppBase.print_out` method of the :class:`~.core.AppBase` class. all other
                                supported kwargs of this method are documented at the
                                :func:`print_out() function <~ae.core.print_out>` of the :mod:`~.core` module.

        this method has an alias named :meth:`.vpo`.
        """
        if self.debug_level >= DEBUG_LEVEL_VERBOSE:
            self.po(*objects, **kwargs)

    vpo = verbose_out         #: alias of method :meth:`.verbose_out`

    def shutdown(self, exit_code: Optional[int] = 0, timeout: Optional[float] = None):
        """ shutdown this app instance, and if it is the main app instance, then also any created sub-app-instances.

        :param exit_code:       set application OS exit code - ignored if this is NOT the main app instance (def=0).
                                pass None to prevent call of sys.exit(exit_code).
        :param timeout:         timeout float value in seconds used for the thread termination/joining, for the
                                shutdowns of the app/sub-app instances and for the acquisition of the threading locks of
                                :data:`the ae log file <log_file_lock>` and the :data:`app instances <app_inst_lock>`.
        """
        if self._shut_down:
            return
        aqc_kwargs: Dict[str, Any] = {'blocking': False} if timeout is None else {'timeout': timeout}
        is_main_app_instance = main_app_instance() is self      # self.is_main==True when main_app_instance() is None
        force = is_main_app_instance and exit_code              # prevent deadlock on app error exit/shutdown

        if exit_code is not None:
            self.po(f"##### {'forced ' if force else ''}shutdown of {self.app_name} with {exit_code=}", logger=_LOGGER)

        # pylint: disable-next=consider-using-with
        a_blocked = (False if force else app_inst_lock.acquire(**aqc_kwargs))
        if is_main_app_instance:
            _shut_down_sub_app_instances(timeout=timeout)
            if _MULTI_THREADING_ACTIVATED:
                _join_app_threads(timeout=timeout)

        # pylint: disable-next=consider-using-with
        l_blocked = (False if force else log_file_lock.acquire(**aqc_kwargs))

        self._flush_and_close_log_buf()
        self._close_log_file()
        if self._log_file_index:
            self._rename_log_file()

        if self._nul_std_out:
            if not self._nul_std_out.closed:
                self._append_eof_and_flush_file(self._nul_std_out, "NUL stdout")
                self._nul_std_out.close()
            self._nul_std_out = None

        if self.py_log_params:
            logging.shutdown()

        self._std_out_err_redirection(False)

        if l_blocked:
            log_file_lock.release()

        _unregister_app_instance(self.app_key)
        if a_blocked:
            app_inst_lock.release()
        self._shut_down = True
        if is_main_app_instance and exit_code is not None:
            sys.exit(exit_code)             # pragma: no cover (would break/cancel test run)

    def _std_out_err_redirection(self, redirect: bool):
        """ enable/disable the redirection of the standard output/error TextIO streams if needed.

        :param redirect:        pass ``True`` to enable or ``False`` to disable the redirection.
        """
        is_main_app_instance = main_app_instance() is self          # is_main is True when main_app_instance() is None
        if redirect:
            if not isinstance(sys.stdout, _PrintingReplicator):     # sys.stdout==ori_std_out fails on pytest/capsys
                if not self.suppress_stdout:
                    std_out = ori_std_out
                elif self._nul_std_out and not self._nul_std_out.closed:
                    std_out = self._nul_std_out
                else:
                    # pylint: disable-next=unspecified-encoding, consider-using-with
                    std_out = self._nul_std_out = open(os.devnull, 'w')
                sys.stdout = cast(TextIO, _PrintingReplicator(sys_out_obj=std_out))
                sys.stderr = cast(TextIO, _PrintingReplicator(sys_out_obj=ori_std_err))
        else:
            if is_main_app_instance:
                sys.stderr = ori_std_err
                sys.stdout = ori_std_out

        if is_main_app_instance:
            if redirect:
                faulthandler.enable(file=sys.stdout)
            elif faulthandler.is_enabled():
                faulthandler.disable()  # pragma: no cover (badly testable - would cancel/break test runs)

    def _append_eof_and_flush_file(self, stream_file: TextIO, stream_name: str):
        """ add a special end-of-file marker in debug mode and flush the internal buffers to the file stream.

        :param stream_file:     file stream.
        :param stream_name:     name of the file stream (only used for debugging/error messages).
        """
        try:
            try:
                # cannot use print_out() here because of recursions on log file rotation, so use built-in print()
                # noinspection PyTypeChecker
                print(file=stream_file)
                if self.debug:
                    # noinspection PyTypeChecker
                    print('EoF', file=stream_file)
            except Exception as ex:     # pragma: no cover - pylint: disable=broad-except
                self.po(f"Ignorable {stream_name} end-of-file marker exception={ex}", logger=_LOGGER)

            stream_file.flush()

        except Exception as ex:         # pylint: disable=broad-except
            self.po(f"Ignorable {stream_name} flush exception={ex}", logger=_LOGGER)

    def _flush_and_close_log_buf(self):
        """ flush and close ae log buffer and pass content to the log stream if opened. """
        stream = self._log_buf_stream
        if stream:
            if self._log_file_stream:
                self._append_eof_and_flush_file(stream, "ae log buf")
                buf = stream.getvalue() + ("\n####  End Of Log Buffer" if self.debug else "")
                self._log_file_stream.write(buf)
            self._log_buf_stream = None
            stream.close()

    def _open_log_file(self):
        """ open the ae log file with a path and file name specified by :attr:`_log_file_name`.

        tries to create a log subfolder - if specified in :attr:`_log_file_name` and
        the folder does not exist (folder creation is limited to one folder level).

        .. note:: an already existing file with the same file name will be overwritten (file contents get lost!).
        """
        log_dir = os_path_dirname(self._log_file_name)
        if log_dir and not os_path_isdir(log_dir):
            os.mkdir(log_dir)
        # pylint: disable-next=unspecified-encoding, consider-using-with
        self._log_file_stream = open(self._log_file_name, "w", errors=DEF_ENCODE_ERRORS)

    def _close_log_file(self):
        """ close the ae log file. """
        if self._log_file_stream:
            stream = self._log_file_stream
            self._append_eof_and_flush_file(stream, "ae log file")
            self._log_file_stream = None
            stream.close()

    def _rename_log_file(self):
        """ rename rotating log file while keeping first/startup log and log file count below :data:`MAX_NUM_LOG_FILE`.
        """
        file_base, file_ext = os_path_splitext(self._log_file_name)
        dfn = f"{file_base}-{self._log_file_index:0>{LOG_FILE_IDX_WIDTH}}{file_ext}"
        if os_path_isfile(dfn):
            os.remove(dfn)                              # remove the old log file from the previous app run
        if os_path_isfile(self._log_file_name):         # prevent errors after log file error or unit test cleanup
            os.rename(self._log_file_name, dfn)

        self._log_file_index += 1
        if self._log_file_index > MAX_NUM_LOG_FILES:    # use > instead of >= to always keep the first/startup log file
            first_idx = self._log_file_index - MAX_NUM_LOG_FILES
            dfn = f"{file_base}-{first_idx:0>{LOG_FILE_IDX_WIDTH}}{file_ext}"
            if os_path_isfile(dfn):
                os.remove(dfn)
