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
        processes = ProcessIDs(cleanup_seen_interval=cleanup_seen_interval)
        proc_list = [pid for pid in processes]

        self.assertGreater(len(proc_list), 10)
        proc_list.sort()
        print('Initial PIDs: {}'.format(proc_list))

        # There's a slight chance a new process could appear, but unlikely, so should be empty


        # Start a new process to see if processes generator finds it
        sleep_process = subprocess.Popen(['sleep', '5'])

        self.assertIn(sleep_process.pid, [pid for pid in processes])

        # Again, check that next iter is empty
        self.assertFalse([pid for pid in processes])

        sleep_process.kill()  # avoid confusing other tests
        sleep_process.communicate()

        print('first part of test took {} sec'.format(time.time() - start_time))

        # Trigger cleanup
        time.sleep(cleanup_seen_interval)
        self.assertIn(sleep_process.pid, processes.seen)
        for pid in processes:
            pass

        self.assertNotIn(sleep_process.pid, processes.seen)


    def test_wildcard_match(self):
        """Verify pids can be found by command regex"""

        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_wildcard('kworker*')
        pids = list(matcher.matching(processes))
        print('kworker PIDs: {}'.format(pids))
        self.assertGreater(len(pids), 0)

    def test_wildcard_nomatch(self):

        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_wildcard('aoeutshoaeutnhoeunaotehuoensuhtnaoeunth')
        pids = list(matcher.matching(processes))
        self.assertFalse(pids)

    def test_regex_match(self):
        """Verify pids_with_command_name identifies a new process"""

        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_regex('kworker.+')
        pids = list(matcher.matching(processes))
        print('kworker PIDs: {}'.format(pids))
        self.assertGreater(len(pids), 0)

    def test_regex_nomatch(self):
        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_regex('oenuthoeuaseouoaenuthoeauaoseunth')
        pids = list(matcher.matching(processes))
        self.assertFalse(pids)

    def test_regex_nomatch2(self):
        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_regex('worker.+')
        pids = list(matcher.matching(processes))
        self.assertFalse(pids)

    def test_regex_nomatch3(self):
        processes = ProcessIDs()
        matcher = ProcessMatcher()
        matcher.add_command_regex('kworker')
        pids = list(matcher.matching(processes))
        self.assertFalse(pids)

    def test_process_obj_identity(self):
        """Verify ProcessByPID identity behavior"""

        processes = [p for p in ProcessIDs()]
        pid = processes[-1]

        p1 = ProcessByPID(pid)
        p2 = ProcessByPID(pid)
        self.assertEqual(p1, p2)
        self.assertIsNot(p1, p2)


if __name__ == '__main__':
    unittest.main()
