import logging,inspect,sys

class CustomFormatter(logging.Formatter):
    def format(self, record):
        frame = inspect.currentframe()
        
        parent_function = inspect.getouterframes(frame)[9].function
        
        record.parent_function = parent_function
              
        try:
            class_name = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_locals["self"].__class__.__name__
        except:
            class_name = "unknown"
        class_name = class_name.lower().replace("jtable","")
        record.class_name = class_name
        return super().format(record)

class CustomFilter(logging.Filter):
    def filter(self, record):
        record.class_name = getattr(record, 'class_name', 'UnknownClass')
        record.parent_function = getattr(record, 'parent_function', 'UnknownFunction')
        
        context = f"{record.class_name}.{record.parent_function}"
        record.fixed_context = f"{context:<50}"
        
        # total_message_size = len(record.fixed_context) + len(record.msg)
        # logging.info(f"total_message_size: {str(total_message_size)}")
        # print(f"total_message_size: {str(total_message_size)}")
        # if total_message_size > terminal_size.columns:
        #     record.msg = str(record.msg)[:terminal_size.columns - len(record.fixed_context) ] + '...'

        return True

class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        """Only lets through log messages with log level below ERROR ."""
        return record.levelno < logging.ERROR

"""
https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
"""
logging_config = {
    'version': 1,
    'formatters': {
        'my_formatter': {
            '()': CustomFormatter,
            # 'format': '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S'

        }
    },
    'filters': {
        'custom': {
            '()': CustomFilter,
        },
    },
    'handlers': {
        'console_stderr': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'my_formatter',
            'stream': sys.stderr,
            'filters': ['custom'],
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['console_stderr']
    },
}
