#!/usr/bin/env python3
"""
Usage: ./jgrep.py [options] <pattern> <url> ...

<pattern>       A regular expression to look for in the logs.
<url>           The URL of a Job or a View in Jenkins.

Options:
--urls-only         Prints only the urls of logs containing selected lines.
--builds-only       Prints only the urls of builds having logs containing selected lines.
--jobs-only         Prints only the urls of jobs having logs containing selected lines.
--no-urls           Suppress the prefixing of urls on output.
--include-disabled  Include disabled jobs.
--timestamps        Prints the build time.
"""
import re
from datetime import datetime

import docopt

import jenkins


def main():
    arguments = docopt.docopt(__doc__)
    pattern = re.compile(arguments['<pattern>'])
    urls = arguments['<url>']
    for url in urls:
        for job in recursive_jobs(jenkins.Jenkins(url)):
            if arguments['--include-disabled'] or job.color != 'disabled':
                grep_builds(arguments, pattern, job)


def grep_builds(arguments, pattern, job):
    for build in job.builds or []:
        console_text = build.request('consoleText')
        line_number = 0
        one_per_job = False
        for line in console_text.splitlines():
            line_number += 1
            if pattern.search(line):
                one_per_build = False
                timestamp = None
                if arguments.get('--urls-only'):
                    line_format = '{console_url}'
                    one_per_build = True
                elif arguments.get('--builds-only'):
                    line_format = '{build_url}'
                    one_per_build = True
                elif arguments.get('--no-urls'):
                    line_format = '{line}'
                elif arguments.get('--jobs-only'):
                    line_format = '{job_url}'
                    one_per_job = True
                else:
                    line_format = '{console_url}#{line_number}: {line}'

                if arguments.get('--timestamps'):
                    line_format = '[{timestamp}] ' + line_format
                    timestamp = datetime.fromtimestamp(build.timestamp // 1000)
                print(line_format.format(job_url=job.get_url(),
                                         console_url=build.get_url('consoleText'),
                                         build_url=build.get_url(),
                                         line_number=line_number,
                                         line=line,
                                         timestamp=timestamp))
                if one_per_job:
                    return
                elif one_per_build:
                    break


def recursive_jobs(job_or_view):
    jobs = set()
    if job_or_view.builds:
        jobs.add(job_or_view)
        yield job_or_view
    for job in job_or_view.jobs or []:
        for child_job in unique(recursive_jobs(job), jobs):
            yield child_job
    for view in job_or_view.views or []:
        if view.get_url() != job_or_view.get_url():
            for child_job in unique(recursive_jobs(view), jobs):
                yield child_job


def unique(items, previous_items):
    for item in items:
        if item not in previous_items:
            previous_items.add(item)
            yield item


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
