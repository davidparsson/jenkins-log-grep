#!/usr/bin/env python3
"""
Usage: ./grep.py [options] <pattern> <view> ...

Options:
-l      Write only the urls of logs containing selected lines.
"""
import json
import docopt
import re
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
            self._queried_data = self.request_json()

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

    def url(self, relative_url=None):
        if relative_url:
            return self._url + relative_url
        return self._url

    def request_json(self, relative_url='api/json'):
        return json.loads(self.request(relative_url))

    def request(self, relative_url):
        return request.urlopen(self._url + relative_url).read().decode()



def main():
    arguments = docopt.docopt(__doc__)
    files_only = arguments.get('-l')
    pattern = re.compile(arguments['<pattern>'])
    view_urls = arguments['<view>']
    for view_url in view_urls:
        for job in recursive_jobs(Jenkins(view_url)):
            for build in job.builds or []:
                console_text = build.request('consoleText')
                line_number = 0
                for line in console_text.splitlines():
                    line_number += 1
                    if pattern.search(line):
                        if files_only:
                            print(build.url('consoleText'))
                            break
                        else:
                            print('{}:{}: {}'.format(build.url('consoleText'), line_number, line))


def recursive_jobs(jenkins):
    for job in jenkins.jobs or []:
        yield job
        for child_job in recursive_jobs(job):
            yield child_job

if __name__ == '__main__':
    main()
