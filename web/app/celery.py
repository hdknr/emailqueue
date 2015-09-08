# part of app.settings
from kombu import Exchange, Queue
DEFAULT_JOBQ = 'sandbox'

CELERY_RESULT_BACKEND = 'amqp'
CELERY_TASK_SERIALIZER = 'pickle'
BROKER_URL = 'amqp://{JOBQ}:{JOBQ}@localhost:5672/{JOBQ}'.format(
    JOBQ=DEFAULT_JOBQ)
CELERY_DEFAULT_QUEUE = DEFAULT_JOBQ
CELERY_QUEUES = (Queue(DEFAULT_JOBQ, Exchange(DEFAULT_JOBQ),
                 routing_key=DEFAULT_JOBQ),)
# CELERY_ALWAYS_EAGER = True
