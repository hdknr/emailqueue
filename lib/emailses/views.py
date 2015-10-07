from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, HttpResponse
import models


def verify_message(msg):
    return True


def process_subscription(msg):
    return True


def process_notification(msg):
    return True


@csrf_exempt
def bounce(request):
    notification = models.Notification.objects.create(
        request.META, request.body)

    if not notification.is_valid():
        return HttpResponseBadRequest('bad request')

    return HttpResponse('OK')


@csrf_exempt
def complaint(request):
    return bounce(request)


@csrf_exempt
def delivery(request):
    return bounce(request)
