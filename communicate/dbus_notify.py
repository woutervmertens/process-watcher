
import sys
import notify2
from notify2 import Notification


notify2.init(sys.argv[0])


def send(process=None, subject_format='{executable} process {pid} ended',
         timeout=notify2.EXPIRES_NEVER):
    """Display a Desktop Notification via DBUS (notify2)

    :param process: information about process. (.info() inserted into body)
    :param subject_format: subject format string. (uses process.__dict__)
    :param timeout: how long to display notification (milliseconds) default 0 (never expires)
    """
    notif = Notification(subject_format.format(**process.__dict__),
                         process.info())
    notif.timeout = timeout
    notif.show()
