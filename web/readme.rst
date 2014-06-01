For gunicorn runs under apache mod_proxy
================================================

httpd.conf
-----------

- enable apache mods

::

    $ sudo a2enmod proxy
    $ sudo a2enmod proxy_http
    $ sudo a2enmod headers

- if you want to run app under "/mail" path

::

    ProxyPass /mail/static !
    Alias /mail/static /home/hide/sample/mail/web/static
    ProxyPreserveHost On

    <Location /mail/ >
    ProxyPass http://127.0.0.1:8000/mail/
    ProxyPassReverse http://127.0.0.1:8000/mail/
    RequestHeader set SCRIPT_NAME /mail
    #   --- only for <VirtualHost *:443>
    #   RequestHeader set X-FORWARDED-PROTOCOL ssl
    #   RequestHeader set X-FORWARDED-SSL on 
    </Location>


run application
-----------------

::

    $ python manage.py run_gunicorn

