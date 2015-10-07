# -*- coding: utf-8 -*-
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives

from emailsmtp.tasks import send_raw_message


def create_greetings(from_email, to_email):
    text_template = get_template('alumni/mails/greetings.txt')
    html_template = get_template('alumni/mails/greetings.html')

    var1 = u'aaaa'
    var2 = u'bbbb'

    ctx = Context({'var1': var1, 'var2': var2})

    subject = 'Hello'

    text_content = text_template.render(Context())
    html_content = html_template.render(Context())

    msg = EmailMultiAlternatives(
        subject, text_content,
        from_email,
        [to_email])

    msg.attach_alternative(html_content, "text/html")
    return msg.message()


def send_greetings():
    from_email = 'admin@groups.rioja.jp'
    to_email = 'hidelafoglia@gmail.com'    # 'hdknr@ic-tact.co.jp'
    send_raw_message(
        from_email, [to_email],
        create_greetings(from_email, to_email).as_string())
