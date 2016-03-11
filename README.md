# process-watcher
Watch Linux processes and notify when they complete.
Should also work with MacOS, please let me know if it does or needs a few fixes to be compatible.

Only needs the */proc* pseudo-filesystem to check and gather information about processes.

Currently written for **Python3**, but shouldn't be difficult to make python2 compatible.

**Supported Notification Methods:**

* Console (STDOUT)
* Email
* Desktop Notification

**Output message**
> PID 18851: /usr/lib/libreoffice/program/soffice.bin --writer --splash-pipe=5
>  Started: Thu, Mar 10 18:33:37  Ended: Thu, Mar 10 18:34:26  (duration 0:00:49)
>  Memory (current/peak) - Resident: 155,280 / 155,304 kB   Virtual: 1,166,968 / 1,188,216 kB

# Installation

Just create a symbolic link to **process_watcher.py**

For example: `ln -s path/to/process-watcher/process_watcher.py /usr/local/bin/process_watcher`

*I realize there may be a better way to package this. If you have suggestions to make this installable in the pip world create an issue or PR.*

# Running

The program just runs until all processes end or forever if *--watch-new* is specified.

In Unix environments you can run a program in the background and disconnect from the terminal like this:
`nohup process_watcher.py ARGs &` 

## Examples
Send an email when process 1234 exits.
`process_watcher --pid 1234 --to me@gmail.com`

Watch all **myapp** processes and continue to watch for new ones. Send desktop notifications.
`process_watcher --command myapp --notify --watch-new`

Watch 2 PIDs, continue to watch for multiple command name patterns, email two people.
`process_watcher -p 4242 -p 5655 -c myapp -c anotherapp -c "kworker/[24]" -w --to bob@gmail.com --to alice@gmail.com`

## Help

Arguments from **process_watcher --help**

```
[+] indicates the argument may be specified multiple times, for example:
 process-watcher -p 1234 -p 4258 -c myapp -c "exec\d+" --to person1@domain.com --to person2@someplace.com

optional arguments:
  -h, --help            show this help message and exit
  -p PID, --pid PID     process ID(s) to watch [+]
  -c COMMAND_PATTERN, --command COMMAND_PATTERN
                        watch all processes matching the command name. (RegEx pattern) [+]
  -w, --watch-new       watch for new processes that match --command. (run forever)
  --to EMAIL_ADDRESS    email address to send to [+]
  -n, --notify          send DBUS Desktop notification
  -i SECONDS, --interval SECONDS
                        how often to check on processes. (default: 15.0 seconds)
  -q, --quiet           don't print anything to stdout
```

# Optional Dependencies

## Desktop Notifications

Requires [notify2](https://notify2.readthedocs.org/en/latest)
`pip install notify2`

Requires **python-dbus**, which is easiest to install with your package manager:
`sudo apt-get install python3-dbus`

## Email

Uses Python's built-in email module. However, you will need to setup a local smtp server. 
[This tutorial](https://easyengine.io/tutorials/linux/ubuntu-postfix-gmail-smtp) shows how to setup Postfix with a GMail relay on Ubuntu. 

# Contributions

I created this after searching for a program to notify via email when a process ends. After a brief search, most suggestions I found were basic unix commands, such as on [StackExchange thread](http://unix.stackexchange.com/questions/55395/is-there-a-program-that-can-send-me-a-notification-e-mail-when-a-process-finishe).

So I decided to create this to refresh my Python skills and hopefully create something others find useful. I'm sure there are other programs that do the same thing, but if you think this code has promise and want to extend it, don't hesitate to send me a PR.

# Ideas & Bugs

These are some ideas and known issues I have; if any of these is particularly important to you, please create a GitHub issue (or PR) and describe your requirements and suggestions. Otherwise, I have no way of knowing what changes users want.

- Recycled PIDs won't be detected in --watch-new mode
- Config file that specifies defaults so you don't need to specify email addresses or a different interval every time.
- Configure logging
- Record other proc stats
- Code may not be as exception tolerant as it should be. Need to place try blocks in appropriate locations.
- Rare race condition where a PID is found but ends before /proc/PID is read.
- Package so installable easily with pip
- MacOS support? Need someone to test.
- Other communication protocols. XMPP? Unix command
- Alert on high-memory and high-CPU usage
- Add --command-args option
- RegEx flags
