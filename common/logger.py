import logging
import logging.config
import logging.handlers


class Logger():

    def __init__(self):
        self.config= {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        # 其他的 formatter
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '.\log\logs.txt',
            'level': 'DEBUG',
            'formatter': 'simple',
            'encoding': 'GBK'
        },
        # 其他的 handler
    },
    'loggers':{
        'StreamLogger': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'FileLogger': {
            # 既有 console Handler，还有 file Handler
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        # 其他的 Logger
    }
}
        logging.config.dictConfig(self.config)
        self.logger=logging.getLogger("FileLogger")

    def __call__(self, *args):
        self.logger.info(*args)

    def get_logger(self):
        return self.logger
    
if __name__ == '__main__':
    Logger()("122222")
    complex_logger=Logger().get_logger()
    simple_logger=Logger()
    simple_logger(8888)
    complex_logger.debug('This is a customer debug message')
    complex_logger.info('This is an customer info message')
    complex_logger.warning('This is a customer warning message')
    complex_logger.error('This is an customer error message')
    complex_logger.critical('This is a customer critical message')