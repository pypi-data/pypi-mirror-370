import logging
from json_log_formatter import JSONFormatter

logger = logging.getLogger()


class StandardJSONLogFormatter(JSONFormatter):
    def json_record(self, message, extra, record):
        additional_info = {
            "name": record.name,
            "level": record.levelname,
            "file": record.filename,
            "exc_info": record.exc_info,
            "thread": record.thread,
        }
        extra = {**extra, **additional_info}
        return super(StandardJSONLogFormatter, self).json_record(message, extra, record)
