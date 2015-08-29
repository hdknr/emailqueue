__all__ = ['LOGGING', ]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', },
    },
}
