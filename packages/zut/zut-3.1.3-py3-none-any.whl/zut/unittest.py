"""
Utilities for unit tests.
"""
from __future__ import annotations

import sys
from unittest import TestProgram

def run_test_module(start_module = 'test', *, exit = False):
    """
    Run unit tests with discovery from the given start module, while still allowing to pass module.
    """
    actual_args = []
    tests = []

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg.startswith('-'):
            actual_args.append(arg)
            if arg == '-s' or arg == '--start-directory':
                raise ValueError(f"Argument not allowed: {arg}")
            elif arg in {'-k', '-p', '--pattern', '-t', '--top-level-directory'} and args: # options with values
                arg_value = args.pop(0)
                actual_args.append(arg_value)
        else:
            tests.append(arg)

    if tests:
        actual_args = ['unittest', *actual_args, *[f'{start_module}.{test}' for test in tests]]
    else:
        actual_args = ['unittest', 'discover', '-s', start_module, *actual_args]

    TestProgram(module=None, exit=exit, argv=actual_args)


if sys.version_info < (3, 10):
    from unittest import TestCase

    if sys.version_info < (3, 9):
        import logging
        import collections

        from unittest.case import _BaseTestCaseContext

        _LoggingWatcher = collections.namedtuple("_LoggingWatcher",
                                                ["records", "output"])

        class _CapturingHandler(logging.Handler):
            """
            A logging handler capturing all (raw and formatted) logging output.
            """

            def __init__(self):
                logging.Handler.__init__(self)
                self.watcher = _LoggingWatcher([], [])

            def flush(self):
                pass

            def emit(self, record):
                self.watcher.records.append(record)
                msg = self.format(record)
                self.watcher.output.append(msg)


        class _AssertLogsContext(_BaseTestCaseContext):
            """A context manager used to implement TestCase.assertLogs()."""

            LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

            def __init__(self, test_case, logger_name, level):
                _BaseTestCaseContext.__init__(self, test_case)
                self.logger_name = logger_name
                if level:
                    self.level = logging._nameToLevel.get(level, level)
                else:
                    self.level = logging.INFO
                self.msg = None

            def __enter__(self):
                if isinstance(self.logger_name, logging.Logger):
                    logger = self.logger = self.logger_name
                else:
                    logger = self.logger = logging.getLogger(self.logger_name)
                formatter = logging.Formatter(self.LOGGING_FORMAT)
                handler = _CapturingHandler()
                handler.setFormatter(formatter)
                self.watcher = handler.watcher
                self.old_handlers = logger.handlers[:]
                self.old_level = logger.level
                self.old_propagate = logger.propagate
                logger.handlers = [handler]
                logger.setLevel(self.level)
                logger.propagate = False
                return handler.watcher

            def __exit__(self, exc_type, exc_value, tb):
                self.logger.handlers = self.old_handlers
                self.logger.propagate = self.old_propagate
                self.logger.setLevel(self.old_level)
                if exc_type is not None:
                    # let unexpected exceptions pass through
                    return False
                if len(self.watcher.records) == 0:
                    self._raiseFailure(
                        "no logs of level {} or higher triggered on {}"
                        .format(logging.getLevelName(self.level), self.logger.name))
        
    else:
        from unittest._log import _AssertLogsContext

    class _AssertNoLogsContext(_AssertLogsContext):
        def __enter__(self):
            super().__enter__()
            return None

        def __exit__(self, exc_type, exc_value, tb):
            self.logger.handlers = self.old_handlers
            self.logger.propagate = self.old_propagate
            self.logger.setLevel(self.old_level)

            if exc_type is not None:
                # let unexpected exceptions pass through
                return False

            # assertNoLogs
            if len(self.watcher.records) > 0:
                self._raiseFailure(
                    "Unexpected logs found: {!r}".format(
                        self.watcher.output
                    )
                )

    def _assertNoLogs(self, logger=None, level=None):
        return _AssertNoLogsContext(self, logger, level)
    
    TestCase.assertNoLogs = _assertNoLogs
