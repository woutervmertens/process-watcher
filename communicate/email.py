
import smtplib
from email.mime.text import MIMEText


def send(to=None, process=None, subject_format='{executable} process {pid} ended'):
    """Send email about the ended process.

    :param to: email addresses to send to
    :param process: information about process. (.info() inserted into body)
    :param subject_format: subject format string. (uses process.__dict__)
    """
    if to is None:
        raise ValueError('to keyword arg required')

    body = process.info()
    body += '\n\n(automatically sent by process-watcher program)'
    msg = MIMEText(body)
    msg['Subject'] = subject_format.format(**process.__dict__)
    # From is required
    msg['From'] = 'process.watcher@localhost'
    msg['To'] = ', '.join(to)

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    try:
        print('Sending email to: {}'.format(msg['To']))
        s.send_message(msg)
    finally:
        s.quit()
