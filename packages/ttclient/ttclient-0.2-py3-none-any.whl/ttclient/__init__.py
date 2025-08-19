from logging.config import dictConfig

from .client import BaseClient, TTClient

__version__ = '0.2'
__all__ = ['BaseClient', 'TTClient']

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'debug': {
            'fmt': '%(levelname)s-8s %(asctime)s %(name)s %(filename)s:%(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'default': {
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'ttclient': {'handlers': ['default'], 'level': 'DEBUG', 'propagate': False},
    },
})
