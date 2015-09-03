''' Tasks for postfix
'''

from celery import shared_task


import traceback
import models

import logging
logger = logging.getLogger('postfix')


@shared_task
def save_inbound(sender, recipient, raw_message):
    '''
    Save `raw_message` (serialized email) to  :ref:`postfix.models.Message`
    This is called by bounce hander defined in SMTP server
    (ex. transport defined in Postfix :ref:`master.cf`).

    :param email sender: sender address
    :param email recipient: recipient address
    :param basestring raw_message: seriazlied email
    '''

    try:
        models.Message.objects.create(
            sender=sender, recipient=recipient, raw_message=raw_message)
    except:
        logger.error(traceback.format_exc())
