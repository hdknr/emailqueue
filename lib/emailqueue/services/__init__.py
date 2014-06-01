
class Api(object):
    name = "Servcie Api" 

    def __init__(self, service):
        self.service = service

    def send(self, email):
        raise NotImplemented
