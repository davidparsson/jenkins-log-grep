import json
from urllib import request


class Jenkins:

    def __init__(self, url=None, initial_data=None):
        if not initial_data:
            initial_data = {}
        self._url = initial_data.get('url', url)
        self._initial_data = initial_data
        self._queried_data = None

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass

        initial_value = self._initial_data.get(name, None)
        if initial_value:
            return initial_value

        if not self._queried_data:
            if not self._url:
                return None
            self._queried_data = self.get_json()

        return self.__get_child(name)

    def __get_child(self, name):
        value = self._queried_data.get(name)
        if type(value) == list:
            return [Jenkins(initial_data=item) for item in value]
        elif value:
            return Jenkins(initial_data=value)
        else:
            return None

    def __repr__(self):
        return "<Jenkins {}>".format(repr(self._initial_data))

    def get_url(self, relative_url=None):
        if relative_url:
            return self._url + relative_url
        return self._url

    def get_json(self, relative_url='api/json'):
        return json.loads(self.get_raw(relative_url))

    def get_raw(self, relative_url):
        return request.urlopen(self._url + relative_url).read().decode()
