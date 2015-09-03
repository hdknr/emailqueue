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
table = postfix_transport
select_field = domain
where_field = domain
~~~

~~~
CREATE TABLE `postfix_transport` (
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
table = postfix_transport
select_field = transport
where_field = domain
~~~

### virtual_alias_maps.cf 

~~~
host = localhost
user = emailqueue
password = emailqueue
dbname = emailqueue
table = postfix_alias
select_field = forward
where_field = recipient
~~~

~~~
CREATE TABLE `postfix_alias` (
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
  flags=FDRq user=vagrant argv=/home/vagrant/inbound.sh $sender $recipient
mailbox unix  -       n       n       -       -       pipe
  flags=FDRq user=vagrant argv=/home/vagrant/mailbox.sh $sender $recipient
~~~


## Senario 

- Someone can send mails to `@admin.deb`. 
- `webmaster@admin.deb` can accept mails and hold those in `webmaster@mailbox.local`.  
- `nodbody@admin.deb` is not in the alias table. DSN is returned back to original sender.

### Transport

- `mailbox` is service which delegate bash script to save message.
- `error` is service defined by Postfix.

~~~
mysql> select * from postfix_transport;
+----+---------------+----------------------+
| id | domain        | transport            |
+----+---------------+----------------------+
|  3 | mailbox.local | mailbox              |
|  5 | admin.deb     | error                |
+----+---------------+----------------------+
~~~

### Alias

~~~
mysql> select * from postfix_alias;
+----+---------------------+-------------------------+
| id | recipient           | forward                 |
+----+---------------------+-------------------------+
|  1 | webmaster@admin.deb | webmaster@mailbox.local |
+----+---------------------+-------------------------+
~~~
