#!/usr/bin/env python3

import sys
import time
from datetime import datetime
import argparse
import os.path as P

# Information text format for ProcessByPID class
INFO_RUNNING_FORMAT="""PID {pid}: {command}
 Started: {created_datetime:%a, %b %d %H:%M:%S}"""

INFO_ENDED_FORMAT=INFO_RUNNING_FORMAT + "  Ended: {ended_datetime:%a, " \
                                        "%b %d %H:%M:%S}  (duration {" \
                                        "duration_text})"

MEM_TEXT = "\n Memory (current/peak) - " \
           "Resident: {status[VmRSS]:,} / {status[VmHWM]:,} kB   " \
           "Virtual: {status[VmSize]:,} / {status[VmPeak]:,} kB"

INFO_RUNNING_FORMAT += MEM_TEXT
INFO_ENDED_FORMAT += MEM_TEXT

parser = argparse.ArgumentParser(description='Watch a process and notify when it completes.')
parser.add_argument('-p', '--pid', help='process ID(s) to watch (may specify '
                                        '-p multiple times)',
                    type=int,
                    action='append')
parser.add_argument('-i', '--interval', help='how often to check on processes (seconds) default: 15',
                    type=float, default=15.0)
parser.add_argument('-q', '--quiet', help="don't print anything to stdout",
                    action='store_true')

# Just print help and exit if no arguments specified.
if len(sys.argv) == 1:
    print('No arguments given, printing help:\n')
    parser.print_help()
    sys.exit()

args = parser.parse_args()

# Shadow built-in print that does nothing if --quiet specified
if args.quiet:
    def print(*args, **kwargs):
        pass


def notify():
    # mailx
    pass

# class Notifier

#FIXME how to do by name? ps -C name
#
# TODO option to check for new processes with name every time, or only at beginning?

class NoProcessFound(Exception):
    """Indicate a process could not be found."""
    def __init__(self, pid):
        super(NoProcessFound, self).__init__('No process with PID {}'
                                             .format(pid))
        self.pid = pid


class ProcessByPID:
    """Information about a process using the /proc filesystem"""

    # /proc/<PID>/status fields to record
    # WARNING: Must list fields in order found in file for update_status()
    # algorithm to work. (done for efficiency)
    # Also, fields are assumed to be int
    status_fields = ('VmPeak', 'VmSize', 'VmHWM', 'VmRSS')

    # Values will be stored in object as _status_X

    def __init__(self, pid):

        self.pid = pid

        # Mapping of each status_fields to value from the status file.
        # Initialize fields to zero in case info() is called.
        self.status = {field: 0 for field in self.status_fields}

        self.path = path = P.join('/proc', str(pid))
        if not P.exists(path):
            raise NoProcessFound(pid)

        self.status_path = P.join(path, 'status')
        self.running = True

        # Get the command that started the process
        with open(P.join(path, 'cmdline')) as f:
            cmd = f.read()
            # args are separated by \x00 (Null byte)
            self.command = cmd.replace('\x00', ' ').strip()

        # Get the start time (/proc/PID file creation time)
        self.created_datetime = datetime.fromtimestamp(P.getctime(path))

        self.update_status()

    def info(self):
        """Get information about process.
        command, start_time"""

        if self.running:
            return INFO_RUNNING_FORMAT.format(**self.__dict__)
        else:
            return INFO_ENDED_FORMAT.format(**self.__dict__)

    def update_status(self):
        """Update memory statistics"""
        # Memory information can be found in status and statm /proc/PID files
        # status file VmRSS equivalent to top's RES column
        # statm disagrees with status VmRSS, I think it may not include
        # sub-processes
        # From: man proc
        #       * VmPeak: Peak virtual memory size.
        #       * VmSize: Virtual memory size.
        #       * VmHWM: Peak resident set size ("high water mark").
        #       * VmRSS: Resident set size.

        fields = iter(self.status_fields)
        field = next(fields)
        with open(self.status_path) as f:
            for line in f:
                if line.startswith(field):
                    # separated by white-space, 2nd element is value
                    # 3rd is units e.g. kB
                    # At the moment all fields are ints
                    self.status[field] = int(line.split()[1])

                    try:
                        field = next(fields)
                    except StopIteration:
                        break

    def check(self):
        """Check whether process is running and update stats
        :return True if running, otherwise False
        """

        if not self.running:
            return False

        running = P.exists(self.path)
        if running:
            self.update_status()
        else:
            # Process ended since last check, recond end time
            self.running = False
            self.ended_datetime = datetime.now()
            self.duration = self.ended_datetime - self.created_datetime
            # Looks like 3:06:29.873626   cutoff microseconds
            text = str(self.duration)
            self.duration_text = text[:text.rfind('.')]

        return running

# List of all the watching objects
watchers = []

# Initial check on processes, get metadata
try:
    watchers += (ProcessByPID(pid) for pid in args.pid)

except NoProcessFound as ex:
    print('No process with PID {}'.format(ex.pid))
    sys.exit(1)

print('Watching {} processes:'.format(len(watchers)))
for w in watchers:
    print(w.info())

try:
    while True:
        time.sleep(args.interval)
        # Need to iterate copy since removing within loop.
        for w in watchers[:]:
            running = w.check()

            if not running:
                print('Process stopped:')
                print(w.info())
                watchers.remove(w)

        if not watchers:
            sys.exit()

except KeyboardInterrupt:
    print('\n')
