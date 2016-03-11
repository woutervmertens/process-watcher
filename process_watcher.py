#!/usr/bin/env python3

import sys
import time
import argparse
from argparse import RawTextHelpFormatter
import re
import logging

from process import *

logging.basicConfig()

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                 description="""Watch a process and notify when it completes via various \
communication protocols. (See README.md for help installing dependencies)

--pid, --command, --to may be specified multiple times. For example:
{exec} -p 123 -p 456 -c exec1 -c exec2 -c exec3 --to person1@domain.com --to person2@someplace.com
""".format(exec=sys.argv[0]))
parser.add_argument('-p', '--pid', help='process ID(s) to watch',
                    type=int,
                    action='append', default=[])
parser.add_argument('-c', '--command', help='Watch all processes matching the command name. (RegEx pattern)',
                    action='append', default=[])
parser.add_argument('-w', '--watch-new', help='Watch for new processes that match --command.\n'
                                              '(causes program to run forever)', action='store_true')
parser.add_argument('--to', help='email address to send to when a process completes.',
                    action='append')
parser.add_argument('-n', '--notify', help='send DBUS Desktop notification', action='store_true')
parser.add_argument('-i', '--interval', help='how often to check on processes (seconds)\ndefault interval: 15',
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

# Load communication protocols based present arguments
# (library, send function keyword args)
comms = []
if args.to:
    try:
        import communicate.email
        comms.append((communicate.email, {'to': args.to}))
    except:
        logging.exception('Failed to load email module.')

if args.notify:
    try:
        import communicate.dbus_notify
        comms.append((communicate.dbus_notify, {}))
    except:
        logging.exception('Failed to load Desktop Notification module.')


# dict of all the process watching objects pid -> ProcessByPID
# items removed when process ends
processes = {}

# Initialize processes from arguments, get metadata
try:
    for pid in args.pid:
        if pid not in processes:
            processes[pid] = ProcessByPID(pid)

except NoProcessFound as ex:
    print('No process with PID {}'.format(ex.pid))
    sys.exit(1)

command_regexs = [re.compile(pat) for pat in args.command]
if command_regexs:
    new_processes = all_processes(yield_None=True)
    for pid in pids_with_command_name(new_processes, *command_regexs):
        if pid not in processes:
            processes[pid] = ProcessByPID(pid)

# Whether program needs to check for new processes matching conditions
watch_new = args.watch_new and len(command_regexs) > 0

if not processes and not watch_new:
    print('No processes found to watch.')
    sys.exit()

print('Watching {} processes:'.format(len(processes)))
for pid, process in processes.items():
    print(process.info())

try:
    to_delete = []
    while True:
        time.sleep(args.interval)
        # Need to iterate copy since removing within loop.
        for pid, process in processes.items():
            running = process.check()
            if not running:
                to_delete.append(pid)

                print('Process stopped:')
                print(process.info())

                for comm, send_args in comms:
                    comm.send(process=process, **send_args)

        if to_delete:
            for pid in to_delete:
                del processes[pid]

            to_delete.clear()

        if watch_new:
            for pid in pids_with_command_name(new_processes, *command_regexs):
                if pid not in processes:
                    processes[pid] = p = ProcessByPID(pid)
                    print(p.info())

        elif not processes:
            sys.exit()

except KeyboardInterrupt:
    print('\n')
