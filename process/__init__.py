"""Process management and information gathering using /proc filesystem.
"""

from datetime import datetime
import os
import os.path as P

PROC_DIR = '/proc'

# Information text format for
#  ProcessByPID class
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

        self.path = path = P.join(PROC_DIR, str(pid))
        if not P.exists(path):
            raise NoProcessFound(pid)

        self.status_path = P.join(path, 'status')
        self.running = True

        # Get the command that started the process
        with open(P.join(path, 'cmdline')) as f:
            cmd = f.read()
            # args are separated by \x00 (Null byte)
            self.command = cmd.replace('\x00', ' ').strip()

            if self.command == '':
                # Some processes (such as kworker) have nothing in cmdline, read comm instead
                with open(P.join(path, 'comm')) as comm_file:
                    self.command = self.executable = comm_file.read().strip()

            else:
                # Just use 1st arg instead of reading comm
                self.executable = self.command.split()[0]

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

    def __eq__(self, other):
        return self.pid == other.pid


def all_processes(yield_None=False):
    """yields every PID seen in /proc once.

    :param yield_None: yield None instead of raising StopIteration if no new processes.
    :return PID or None if no new processes
    """
    seen = set()
    while True:
        current_pids = set()
        for file in os.listdir(PROC_DIR):
            try:
                current_pids.add(int(file))
            except ValueError:
                pass

        new_pids = current_pids - seen
        if not new_pids:
            if yield_None:
                yield None
                continue
            else:
                return

        seen.update(new_pids)

        for pid in new_pids:
            yield pid


def pids_with_command_name(pid_generator, *re_objs):
    """Get a PID list of all processes matching the compiled regular expression object.

    :param pid_generator: object yielding PIDs to check. (stops checking if yields None)
    :param re_objs: compiled regular expressions to match against (from re.compile)
    :return: list of PIDs (int)
    """
    pids = []
    for pid in pid_generator:
        if pid is None:
            break

        path = P.join(PROC_DIR, str(pid), 'comm')
        with open(path) as f:
            comm = f.read().rstrip()
            for re_obj in re_objs:
                if re_obj.match(comm):
                    pids.append(pid)
                    break

    return pids
