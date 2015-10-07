from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, HttpResponse
import json


def verify_message(msg):
    return True


def process_subscription(msg):
    return True


def process_notification(msg):
    return True


@csrf_exempt
def bounce(request):
    msg = {}

    try:
        msg = json.loads(request.body)
        # TODO: verify msg
        verify_message(msg)
    except:
        return HttpResponseBadRequest('bad request')

    if msg.get('Type', '') == 'SubscriptionConfirmation':
        if process_subscription(msg):
            return HttpResponse('SubscriptionConfirmation OK')
        else:
            return HttpResponse('SubscriptionConfirmation Failed')

    elif msg.get('Type', '') == 'Notification':
        process_notification(msg)
        return HttpResponse(json.dumps({'error': 0, 'msg': msg}))

    return HttpResponseBadRequest('No Type')


@csrf_exempt
def complaint(request):
    return bounce(request)


@csrf_exempt
def delivery(request):
    return bounce(request)
