from json import JSONEncoder

class DefaultJsonEncoder(JSONEncoder):
    def default(self, o):
        if '__dict__' in dir(o):
            return o.__dict__
        else:
            return o.__str__()
