# Developer Notes

# Watching Processes

Currently, **process-watcher** just manually polls /proc
There are other, potentially better ways to watch processes.

**Goals:**

- Get exit code when process ends.
- Guarantee short-lived processes are found. (appear during sleep)

## ptrace

**python-ptrace**

Something like:

```python
debugger = PtraceDebugger()
process = debugger.addProcess(pid, is_attached=False)
process.waitEvent()
```

However, in Ubuntu and probably other distros, [permissions are locked down by default](https://wiki.ubuntu.com/SecurityTeam/Roadmap/KernelHardening#ptrace).

```
sudo su -
echo 0 > /proc/sys/kernel/yama/ptrace_scope
```

A better way to grant permissions is with **libcap-bin** as [described here](http://askubuntu.com/questions/146160/what-is-the-ptrace-scope-workaround-for-wine-programs-and-are-there-any-risks)

```
sudo apt-get install libcap2-bin 
sudo setcap cap_sys_ptrace=eip /usr/bin/wineserver
```

Also, I worry that attaching the debugger may actually slow down the process you're watching or have other negative affects. And because wait blocks this technique requires some thought (threading?).

## inotify

**inotify** does not support python3. Docs say it uses epoll.
[Some people say](http://www.serpentine.com/blog/2008/01/04/why-you-should-not-use-pyinotify/) pyinotify is poorly written.
The main critic wrote [python-inotify](https://bitbucket.org/JanKanis/python-inotify) as a replacement.

Advantage to inotify is **process-watcher** won't miss a process that spawns and ends in between checks.

Leaning toward inotify, but need to research file-system watching more.

# Checking if process is running

On unix systems, os.kill(pid, 0) can be used to check if a PID is still running. However, it's only slightly faster than os.path.exists('/proc/PID') and suffers from PermissionError when the process is under a different PID. Code could be written to swap between implementations, but this is overoptimizing.
