============
Features
============

.. contents::
    :local:

Relay
======

Forward
------------------------

- Postbox is an email "alias" 
- If an Message comes to Postbox.address, that Mesage is forwarded to Postbox.forward. 

DNS Bounce back
---------------------------------

- If the alias mailbox or server has something wrong and the DSN is returned back to the Server,
  that DNS message is forwarded back to original sender.

Mail Maganzine
==================

Scheduled
-----------

- A circulation can be scheduled at Mail.due_at

Interruption
------------------------

- A circualtion can be intterrupted when time is at Mail.sleep_from.
- And circualtion will come back when time is at Mail.sleep_to.
- Recipients already sent before the interruption will not be targetted again.

Bounce Management
=================

Bounce count
-------------

- Email addresses sent outside form this server are managed by MailAddress.
- If DSN message are returned to Return-Path, MailAddresds.bounced is counted up. 

Banned address
----------------

- If MailAddress.enabled is False, no mails to this adddress is sent out from the Server. 


