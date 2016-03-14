import unittest
import time
import re
import subprocess

from process import *


class ProcessTests(unittest.TestCase):
    """Test process module code"""

    def test_all_processes(self):
        """Verify that all_processes yields each PID once and finds new processes."""

        start_time = time.time()
        cleanup_seen_interval = 0.05
        processes = all_processes(yield_None=True, cleanup_seen_interval=cleanup_seen_interval)
        proc_list = []
        for p in processes:
            if p is None:
                break
            proc_list.append(p)

        self.assertGreater(len(proc_list), 10)
        proc_list.sort()
        print('Initial PIDs: {}'.format(proc_list))

        # There's a slight chance a new process could appear, but unlikely
        self.assertIsNone(next(processes))

        # Start a new process to see if processes generator finds it
        sleep_process = subprocess.Popen(['sleep', '5'])

        new_process = next(processes)
        while new_process is None:
            time.sleep(0.005)
            new_process = next(processes)

        self.assertEqual(new_process, sleep_process.pid)
        print('Found created sleep process: {}'.format(new_process))

        # There's a slight chance a new process could appear, but unlikely
        self.assertIsNone(next(processes))

        sleep_process.kill()  # avoid confusing other tests
        sleep_process.communicate()

        print('first part of test took {} sec'.format(time.time() - start_time))

        # Trigger cleanup
        sleep_process = subprocess.Popen(['sleep', '5'])
        time.sleep(cleanup_seen_interval)
        for pid in processes:
            if pid is None:
                break

        sleep_process.kill()  # avoid confusing other tests
        sleep_process.communicate()

    def test_pids_with_command_name(self):
        """Verify pids can be found by command regex"""

        re_obj = re.compile('kworker.*')
        processes = all_processes()
        pids = pids_with_command_name(processes, re_obj)
        print('kworker PIDs: {}'.format(pids))
        self.assertGreater(len(pids), 0)

    def test_new_command_by_name(self):
        """Verify pids_with_command_name identifies a new process"""

        re_obj = re.compile('sleep')
        processes = all_processes(yield_None=True)
        pids = pids_with_command_name(processes, re_obj)
        self.assertFalse(pids)

        sleep_process = subprocess.Popen(['sleep', '5'])
        pids = pids_with_command_name(processes, re_obj)
        self.assertListEqual([sleep_process.pid], pids)

        sleep_process.kill()
        sleep_process.communicate()

    def test_process_obj_identity(self):
        """Verify ProcessByPID identity behavior"""

        processes = [p for p in all_processes()]
        pid = processes[-1]

        p1 = ProcessByPID(pid)
        p2 = ProcessByPID(pid)
        self.assertEqual(p1, p2)
        self.assertIsNot(p1, p2)


if __name__ == '__main__':
    unittest.main()
