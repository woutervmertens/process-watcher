# process-watcher
Watch Linux processes and notify when they complete. Should also work with MacOS*.

Only needs the */proc* pseudo-filesystem to check and gather information about processes. Does not need to create/own the process, if you want a daemon manager, see the *Alternatives* section below.

Currently written for **Python3**, but shouldn't be difficult to make python2 compatible.

\**If you run process-watcher on MacOS and it works, let me know so I can update the documentation.* 

**Supported notification methods:**

* Console (STDOUT)
* Email
* Desktop Notification

**Example output message**

*Sent in body of messages. Other information from /proc/PID/status can easily be added by modifying the code.*
```
PID 18851: /usr/lib/libreoffice/program/soffice.bin --writer --splash-pipe=5
 Started: Thu, Mar 10 18:33:37  Ended: Thu, Mar 10 18:34:26  (duration 0:00:49)
 Memory (current/peak) - Resident: 155,280 / 155,304 kB   Virtual: 1,166,968 / 1,188,216 kB
```
## Alternatives

If you are looking for a more substantial daemon monitoring system, people recommend [Monit](https://mmonit.com/monit)

> Monit is a small Open Source utility for managing and monitoring Unix systems. Monit conducts automatic maintenance and repair and can execute meaningful causal actions in error situations.

There is also [upstart](http://upstart.ubuntu.com), which Ubuntu and some other Linux distros have installed. See [Keeping Daemons alive with Upstart](http://www.alexreisner.com/code/upstart).

# Installation

Just create a symbolic link to **process_watcher.py**

For example: `ln -s path/to/process-watcher/process_watcher.py /usr/local/bin/process_watcher`

*I realize there are better ways to package this; if you have suggestions let me know.*

# Running

The program just runs until all processes end or forever if *--watch-new* is specified.

In Unix environments you can run a program in the background and disconnect from the terminal like this:
`nohup process_watcher ARGs &` 

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
 process-watcher -p 1234 -p 4258 -c myapp* -crx "exec\d+" --to person1@domain.com --to person2@someplace.com

optional arguments:
  -h, --help            show this help message and exit
  -p PID, --pid PID     process ID(s) to watch [+]
  -c COMMAND_PATTERN, --command COMMAND_PATTERN
                        watch all processes matching the command name pattern. (shell-style wildcards) [+]
  -crx COMMAND_REGEX, --command-regex COMMAND_REGEX
                        watch all processes matching the command name regular expression. [+]
  -w, --watch-new       watch for new processes that match --command. (run forever)
  --to EMAIL_ADDRESS    email address to send to [+]
  -n, --notify          send DBUS Desktop notification
  -i SECONDS, --interval SECONDS
                        how often to check on processes. (default: 15.0 seconds)
  -q, --quiet           don't print anything to stdout except warnings and errors
  --log                 log style output (timestamps and log level)
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

- Config file that specifies defaults so you don't need to specify email addresses or a different interval every time.
- Configure logging
- Define body message and /proc/PID/status fields in config
- Record other proc stats
- Rare race condition where a PID is found but ends before /proc/PID is read.
- Package so installable easily with pip
- MacOS support? Need someone to test.
- Other communication protocols. XMPP? Unix command
- Alert on high-memory and high-CPU usage
- Add --command-args option
- RegEx flags
- Make installable from pip
- [Pushover](https://pushover.net/) comm protocol
- IRC
- Separate communication code into another project after adding a few more protocols to make it more useful to people. Config file for setup and message templates. Investigate other python libs first. 
