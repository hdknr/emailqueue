from django.views.decorators.csrf import csrf_exempt
import models
from django_ses.views import handle_bounce


def verify_message(msg):
    return True


def process_subscription(msg):
    return True


def process_notification(msg):
    return True


@csrf_exempt
def bounce(request):
    # Log
    models.Notification.objects.create(request.META, request.body)

    return handle_bounce(request)


@csrf_exempt
def complaint(request):
    return bounce(request)


@csrf_exempt
def delivery(request):
    return bounce(request)
