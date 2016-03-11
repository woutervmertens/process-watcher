# Developer Notes

# Watching Processes

Currently, **process-watcher** just manually polls /proc
There are other, potentially better ways to watch processes.

## ptrace

**python-ptrace**

Something like:

```python
debugger = PtraceDebugger()
process = debugger.addProcess(pid, is_attached=False)
process.waitEvent()
```

However, in Ubuntu and probably other distros, permissions are locked down by default.

```
sudo su -
echo 0 > /proc/sys/kernel/yama/ptrace_scope
```

Also, I worry that attaching the debugger may actually slow down the process you're watching or have other negative affects. And because wait blocks this technique requires some thought (threading?).

## inotify

**inotify** does not support python3. Docs say it uses epoll.
[Some people say](http://www.serpentine.com/blog/2008/01/04/why-you-should-not-use-pyinotify/) pyinotify is poorly written.
The main critic wrote [python-inotify](https://bitbucket.org/JanKanis/python-inotify) as a replacement.

Advantage to inotify is **process-watcher** won't miss a process that spawns and ends in between checks.

Leaning toward inotify, but need to research file-system watching more.
