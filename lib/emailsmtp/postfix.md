# Postfix

## main.cf

Transport:

- `relay_domains`: list of accepting domains
- `transport_maps`: defines master.cf services for each domain

Alias:

- `virual_alias_maps`: accepting email

~~~
relay_domains = proxy:mysql:/etc/postfix/db/relay_domains.cf
transport_maps = proxy:mysql:/etc/postfix/db/transport_maps.cf
virtual_alias_maps = proxy:mysql:/etc/postfix/db/virtual_alias_maps.cf

default_transport=jail
~~~

## postfix.mysql

### relay_domains.cf

~~~
hosts = localhost
dbname = emailqueue
user = emailqueue
password = emailqueue
table = emailsmtp_domain
select_field = domain
where_field = domain
~~~

~~~
CREATE TABLE `emailsmtp_domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(50) NOT NULL,
  `transport` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
~~~

### transport_maps.cf

~~~
host = localhost
user = emailqueue
password = emailqueue
dbname = emailqueue
table = emailsmtp_domain
select_field = transport
where_field = domain
~~~

### virtual_alias_maps.cf 

~~~
host = localhost
user = emailqueue
password = emailqueue
dbname = emailqueue
table = emailsmtp_alias
select_field = forward
where_field = recipient
~~~

~~~
CREATE TABLE `emailsmtp_alias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipient` varchar(100) NOT NULL,
  `forward` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `recipient` (`recipient`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
~~~


## master.cf

~~~
jail unix  -       n       n       -       -       pipe
  flags=FDRq user=vagrant argv=/home/vagrant/inbound.sh jail $sender $recipient $original_recipient
inbound unix  -       n       n       -       -       pipe
  flags=FDRq user=vagrant argv=/home/vagrant/inbound.sh inbound $sender $recipient $original_recipient
mailbox unix  -       n       n       -       -       pipe
  flags=FDRq user=vagrant argv=/home/vagrant/inbound.sh mailbox $sender $recipient $original_recipient
~~~

## inbound..sh

~~~
#!/bin/sh
PYTHON=/home/vagrant/.anyenv/envs/pyenv/versions/production/bin/python
MANAGE=/home/vagrant/projects/mysite/web/manage.py

$PYTHON $MANAGE empostfix bounce $@
~~~


## Senario 

- Someone can send mails to `@admin.deb`. 
- `webmaster@admin.deb` can accept mails and hold those in `webmaster@mailbox.local`.  
- `nodbody@admin.deb` is not in the alias table. DSN is returned back to original sender.

### Transport

- `mailbox` is service which delegate bash script to save message.
- `error` is service defined by Postfix.

~~~
mysql> select * from emailsmtp_domain;
+----+---------------+----------------------+
| id | domain        | transport            |
+----+---------------+----------------------+
|  3 | mailbox.local | mailbox              |
|  5 | admin.deb     | error                |
+----+---------------+----------------------+
~~~

### Alias

~~~
mysql> select * from emailsmtp_alias;
+----+---------------------+-------------------------+
| id | recipient           | forward                 |
+----+---------------------+-------------------------+
|  1 | webmaster@admin.deb | webmaster@mailbox.local |
+----+---------------------+-------------------------+
~~~

### bounced DSN

~~~
From MAILER-DAEMON  Thu Sep  3 05:53:04 2015
Return-Path: <MAILER-DAEMON>
Delivered-To: vagrant@jessie.local
Received: by jessie.local (Postfix)
    id 510C68E5B5; Thu,  3 Sep 2015 05:53:04 +0000 (UTC)
Date: Thu,  3 Sep 2015 05:53:04 +0000 (UTC)
From: MAILER-DAEMON@jessie.local (Mail Delivery System)
Subject: Undelivered Mail Returned to Sender
To: vagrant@jessie.local
Auto-Submitted: auto-replied
MIME-Version: 1.0
Content-Type: multipart/report; report-type=delivery-status;
    boundary="4CD378E5B3.1441259584/jessie.local"
Message-Id: <20150903055304.510C68E5B5@jessie.local>

This is a MIME-encapsulated message.

--4CD378E5B3.1441259584/jessie.local
Content-Description: Notification
Content-Type: text/plain; charset=us-ascii

This is the mail system at host jessie.local.

I'm sorry to have to inform you that your message could not
be delivered to one or more recipients. It's attached below.

For further assistance, please send mail to postmaster.

If you do so, please include this problem report. You can
delete your own text from the attached returned message.

                   The mail system

<nobody@admin.deb>: Address is undeliverable

--4CD378E5B3.1441259584/jessie.local
Content-Description: Delivery report
Content-Type: message/delivery-status

Reporting-MTA: dns; jessie.local
X-Postfix-Queue-ID: 4CD378E5B3
X-Postfix-Sender: rfc822; vagrant@jessie.local
Arrival-Date: Thu,  3 Sep 2015 05:53:04 +0000 (UTC)

Final-Recipient: rfc822; nobody@admin.deb
Action: failed
Status: 5.0.0
Diagnostic-Code: X-Postfix; Address is undeliverable

--4CD378E5B3.1441259584/jessie.local
Content-Description: Undelivered Message
Content-Type: message/rfc822

Return-Path: <vagrant@jessie.local>
Received: by jessie.local (Postfix, from userid 1000)
    id 4CD378E5B3; Thu,  3 Sep 2015 05:53:04 +0000 (UTC)
Subject: to nobady
To: <nobody@admin.deb>
X-Mailer: mail (GNU Mailutils 2.99.98)
Message-Id: <20150903055304.4CD378E5B3@jessie.local>
Date: Thu,  3 Sep 2015 05:53:04 +0000 (UTC)
From: vagrant@jessie.local (Vagrant User)

2015年  9月  3日 木曜日 05:53:04 UTC

--4CD378E5B3.1441259584/jessie.local--
~~~
