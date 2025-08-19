import logging
import logging.handlers
import os
import platform
import threading
from datetime import datetime as dt

# Import necessary logging functions and variables
from logging import *  # noqa


class HostnameFilter(logging.Filter):
    """
    A logging filter that adds the hostname as an additional attribute to each log record.
    This class inherits from `logging.Filter` and is designed to be used with Python's logging module to filter
    log records based on the hostname where the program is running.
    hostname: The name of the host where the program is running.
    use case:
        # Create a logger and add the HostnameFilter to it
        import logging

        logger = logging.getLogger('my_logger')
        hostname_filter = HostnameFilter()
        logger.addFilter(hostname_filter)

        # Log a message
        logger.info('This is a log message.')
       # The log record will now have an additional 'hostname' attribute containing the name of the host.
    note: The `hostname` attribute is added to each log record when the filter is applied, and it is set to the
    hostname of the machine where the program is running at that time.
    """

    hostname = platform.node()

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add the `hostname` attribute to the provided log record.
        :param record: The log record to be filtered.
        :return: Always returns True to include the log record in the final output.
        """
        record.hostname = HostnameFilter.hostname
        return True


class ShardNameFilter(logging.Filter):
    """
    A logging filter that adds the 'shard_name' attribute to the log records.
    The value of the 'shard_name' is obtained from the environment variable 'DEVV_SHARD_NAME', or it defaults
    to "shard" if the environment variable is not set.
    use case:
        # Create a logger and add the ShardNameFilter to it
        import logging

        shard_filter = ShardNameFilter()
        logger = logging.getLogger('my_logger')
        logger.addFilter(shard_filter)

        # Log a message
        logger.info('This is a log message')
        # The log record will now have an additional 'shard_name' attribute containing the name of the host.
    """

    shard_name = os.environ.get("DEVV_SHARD_NAME") or "shard"

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add the 'shard_name' attribute to the log record.
        :param record: the log record to which the 'shard_name' attribute will be added.
        :return: always returns True to indicate that the log record should be processed.
        """
        record.shard_name = ShardNameFilter.shard_name
        return True


class DevvJobFilter(logging.Filter):
    """
    A custom logging filter that creates a record tag to specify the unique hash of the DevvJob.

    This filter is used to add a 'job_hash' attribute to the log records. The 'job_hash' is a unique
    hash representing the DevvJob being processed. If the 'job_hash' is not set explicitly using the
    'set_hash' method, it will default to 'devvinit'.

    _local: A threading.local object used to store the thread-local 'job_hash' value.
    """

    def __init__(self):
        logging.Filter.__init__(self)
        self._local = threading.local()

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records and add the 'job_hash' attribute if not already set.
        :param record: The log record to be processed.
        :return: True to allow further processing of the log record.
        """
        if "job_hash" not in self._local.__dict__:
            self._local.job_hash = "devvinit"
        record.job_hash = self._local.job_hash
        return True

    def set_hash(self, job_hash: str):
        """
        Set a custom 'job_hash' value for the current thread.
        :param job_hash: The custom hash value representing the DevvJob.
        """
        self._local.job_hash = job_hash


class TimestampFilter(logging.Filter):
    """
    A custom logging filter that creates a microsecond timestamp.

    This filter is used to add a 'timestamp' attribute to the log records. The 'timestamp' represents
    the current time with microsecond precision when the log record is processed.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records and add a microsecond timestamp.
        :param record: The log record to be processed.
        :return: True to allow further processing of the log record.
        """
        record.timestamp = dt.now()
        return True


global_job_filter = DevvJobFilter()


class DevvLogger(logging.Logger):
    """
    The Devv logger.

    This logger extends the functionality of the standard logging.Logger class. It provides additional
    log levels and customizations specific to the Devv application.

    TRACE: An integer representing the TRACE log level.
    NOTICE: An integer representing the NOTICE log level.
    _severity_map: A dictionary mapping severity strings to log levels.
    """

    def __init__(self, name, level=logging.NOTSET):
        """Initialize the logger with a name and an optional level."""
        logging.Logger.__init__(self, name=name, level=level)
        self.TRACE = 9
        self.NOTICE = 25
        self._set_levels()

        self._severity_map = {
            "trace": self.TRACE,
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "notice": self.NOTICE,
            "warn": logging.WARNING,
            "error": logging.ERROR,
            "crit": logging.CRITICAL,
            "fatal": logging.CRITICAL,
            "notset": logging.NOTSET,
        }

        output_loglevel = self._parse_severity(
            os.getenv("DEVV_OUTPUT_LOGLEVEL", "info")
        )

        # Set logger level to trace (accept everything. Handlers will set their own loglevels)
        self.setLevel(self.TRACE)

        # add console handler to the logger
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(output_loglevel)

        base_format = (
            "%(timestamp)s %(levelname)-5s %(job_hash)s %(thread)x %(name)s [%(filename)s:%(lineno)d]"
            " %(funcName)s -> %(message)s"
        )

        stream_formatter = logging.Formatter(fmt=base_format)
        stream_handler.setFormatter(stream_formatter)

        # self.addHandler(stream_handler)
        self.handlers = [stream_handler]

        self.addFilter(TimestampFilter())
        self.addFilter(ShardNameFilter())
        self.addFilter(HostnameFilter())
        self.addFilter(global_job_filter)

    def trace(self, message, *args, **kws):
        """
        Log a message with the TRACE level if it is enabled.
        :param message: The log message.
        """
        if self.isEnabledFor(self.TRACE):
            # Yes, logger takes its '*args' as 'args'.
            self._log(self.TRACE, message, args, **kws)

    def notice(self, message, *args, **kws):
        """
        Log a message with the NOTICE level if it is enabled.
        :param message: The log message.
        """
        if self.isEnabledFor(self.NOTICE):
            # Yes, logger takes its '*args' as 'args'.
            self._log(self.NOTICE, message, args, **kws)

    def _set_levels(self):
        """
        Set the custom log level names.
        """
        logging.addLevelName(self.TRACE, "trace")
        logging.addLevelName(logging.DEBUG, "debug")
        logging.addLevelName(logging.INFO, "info")
        logging.addLevelName(self.NOTICE, "notice")
        logging.addLevelName(logging.WARNING, "warn")
        logging.addLevelName(logging.ERROR, "error")
        logging.addLevelName(logging.CRITICAL, "crit")

    def _parse_severity(self, severity_string: str):
        """
        Parse the severity string and return the corresponding log level.
        :param severity_string: The severity string to parse.
        :return: The corresponding log level.
        """
        return self._severity_map[severity_string]


def trace(msg, *args, **kwargs):
    """
    Log a message with severity 'TRACE' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    if len(logging.root.handlers) == 0:
        logging.basicConfig()

    logging.root.trace(msg, *args, **kwargs)


logging.trace = trace
logging.setLoggerClass(DevvLogger)
logging.root = DevvLogger("global")


if __name__ == "__main__":

    class A_Class:
        def __init__(self, logger):
            self.logger = logger
            logging.debug("a global message")
            logger.trace("a module logger")

    def logger2_test():
        logger2 = logging.getLogger()
        logger2.notice("from logger2")

    # Tests
    logger = DevvLogger("logtest")
    logger.trace("Trace message")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.notice("Notice message")
    logger.warning("Warning message")
    logger.error("Error message")

    logging.debug("another debug message using the default global logger")
    logging.trace("another trace message using the default global logger")

    a = A_Class(logger)

    logger2_test()
