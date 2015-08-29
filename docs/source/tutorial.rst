==============
emailqueue
==============


.. contents::
    :local:

Install
==========

.. code-block:: bash

    $ pip instal -e+https://github.com/hdknr/emailqueue.git#egg=emailqueue


RabbitMQ
===========

- Configure RabbitMQ(or other backend) to make Celery to work

Postfix
===========

- configure  main.cf / master.cf to access incoming mails to save :ref:`emailqueue.models.Message` .
- see :doc:`emailsmtp.management`

