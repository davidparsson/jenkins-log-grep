#!/usr/bin/env python3
"""
Usage: ./grep.py [options] <pattern> <view> ...

Options:
--urls-only      Write only the urls of logs containing selected lines.
--jobs-only      Write only the urls of jobs having logs containing selected lines.
--no-urls        Suppress the prefixing of urls on output.
"""
import docopt
import re
import jenkins


def main():
    arguments = docopt.docopt(__doc__)
    pattern = re.compile(arguments['<pattern>'])
    view_urls = arguments['<view>']
    for view_url in view_urls:
        for job in recursive_jobs(jenkins.Jenkins(view_url)):
            for build in job.builds or []:
                console_text = build.get_raw('consoleText')
                line_number = 0
                one_per_job = False
                for line in console_text.splitlines():
                    line_number += 1
                    if pattern.search(line):
                        one_per_build = False
                        if arguments.get('--urls-only'):
                            line_format = '{console_url}'
                            one_per_build = True
                        elif arguments.get('--no-urls'):
                            line_format = '{line}'
                        elif arguments.get('--jobs-only'):
                            line_format = '{job_url}'
                            one_per_job = True
                        else:
                            line_format = '{console_url}:{line_number}: {line}'
                        print(line_format.format(job_url=job.get_url(),
                                                 console_url=build.get_url('consoleText'),
                                                 line_number=line_number,
                                                 line=line))
                        if one_per_build or one_per_job:
                            break
                if one_per_job:
                    break


def recursive_jobs(jenkins):
    for job in jenkins.jobs or []:
        yield job
        for child_job in recursive_jobs(job):
            yield child_job

if __name__ == '__main__':
    main()
