
import logging
import json
import subprocess


def send(channel=None, process=None):
    """Notify Slack channel about the ended process.

    :param channel: Slack channel
    :param process: information about process. (.info() inserted into body)
    """
    if channel is None:
        raise ValueError("'channel'keyword arg required")
    else:
        channel = channel[0]

    body = process.info()
    body += '\n\n(automatically sent by process-watcher program)'

    #curl -X POST \
    #-H 'Content-type: application/json' \
    #--data '{"text": "This is posted to <#general> and comes from *monkey-bot*.", "channel": "#general", "username": "monkey-bot", "icon_emoji": ":monkey_face:"}' \
    #https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
  
    cmd_template = "curl -X POST -H 'Content-type: application/json' --data '{}' {}"
    payload = json.dumps({"text": body, "icon_emoji": ":computer:"})
    url = "https://hooks.slack.com/services/{}".format(channel)

    cmd = cmd_template.format(payload,url)
    ret = subprocess.call(cmd,shell=True)
    if ret:
        raise Exception("Failed in POST to {}: error code({})".format(url,ret))
