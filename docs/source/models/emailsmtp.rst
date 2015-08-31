==========
Model
==========

.. contents::
    :local:

.. _emailsmtp.models.Server:

Server:SMTPサーバー
==============================

.. autoclass:: emailsmtp.models.Server
    :members:


.. list-table::

    *    - id
         - ID
         - integer AUTO_INCREMENT
         - 

    *    - created_at
         - 作成日時
         - datetime
         - 

    *    - updated_at
         - 更新日時
         - datetime
         - 

    *    - name
         - メールサービス名
         - varchar(50)
         - 

    *    - domain
         - ドメイン名
         - varchar(50)
         - 

    *    - backend
         - バックエンド
         - varchar(100)
         - 

    *    - forwarder
         - Mail Forwarder
         - varchar(100)
         - 

    *    - server_ptr
         - server ptr
         - integer
         - 

    *    - wait_every
         - 送信ごとの待ち時間
         - integer
         - 送信ごとの待ち時間(ミリ秒)

    *    - wait_ms
         - 待ち時間(ミリ秒)
         - integer
         - 待ち時間(ミリ秒)

.. include:: emailsmtp.models.Server.rst


.. _emailsmtp.models.er:

ER Diagram
============================

.. image:: emailsmtp_models_er.png
