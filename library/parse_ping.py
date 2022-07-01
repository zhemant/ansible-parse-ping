#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = r"""
---
module: parse_ping

short_description: This module uses host ping and parses output and provides the result back

version_added: "1.0.0"

description: This is a custom module to ping a destination IP and print the results in readable format and for use in later stages of ansible plays

options:
    dest:
        description: The destination IP to ping
        required: true
        type: str
    count:
        description: Number of ping packets to send
        required: false
        type: int
        default: 2
    v4:
        description:
        - Only send IPv4 ping
        required: false
        type: boolean
    v6:
        description: Only send IPv4 ping
        required: false
        type: boolean
    interface_name:
        description: Interface to use to send ping
        required: false
        type: str
    interface_ip:
        description: IP address to use to send ping
        required: false
        type: str
    interval:
        description: seconds between sending each packet
        required: false
        type: int
    packet_size:
        description: number of data bytes to be sent
        required: false
        type: int

author:
    - Hemant Zope (@zhemant)
"""

EXAMPLES = r"""
- name: Test Ping
  parse_ping:
    dest: 127.0.0.1
    count: 4
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
stdout:
    description: The command standard output
    returned: always
    type: string
    sample: 'PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.061 ms\n64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.061 ms\n\n--- 127.0.0.1 ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss, time 1013ms\nrtt min/avg/max/mdev = 0.061/0.061/0.061/0.000 ms\n'
stderr:
    description: The command standard error
    returned: always
    type: string
    sample: 'bash: ping: command not found'
rc:
    description: The command return code (0 means success)
    returned: always
    type: int
    sample: 0
stdout_lines:
    description: The command standard output split in lines
    returned: always
    type: list of strings
    sample: '[
                "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.",
                "64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.061 ms",
                "64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.061 ms",
                "",
                "--- 127.0.0.1 ping statistics ---",
                "2 packets transmitted, 2 received, 0% packet loss, time 1013ms",
                "rtt min/avg/max/mdev = 0.061/0.061/0.061/0.000 ms"
            ]'
cmd:
    description: The complete command executed
    type: str
    returned: always
    sample: 'ping -c 2 127.0.0.1'
parsed:
    description: Dictionary of parsed output of ping
    type: dict
    returned: always
    sample: '
        {
            "packet_loss": "0",
            "packet_rx": "2",
            "packet_tx": "2",
            "time_avg": "0.061",
            "time_max": "0.061",
            "time_min": "0.061",
            "time_total": "1013ms"
        }
    '
"""

from ansible.module_utils.basic import AnsibleModule
import re


def main():

    regex = r"^PING\b[^(]*\(([^)]*)\)\s([^.]*)\..*?^(\d+\sbytes).*?icmp_seq=(\d+).*?ttl=(\d+).*?time=(.*?ms).*?(\d+)\spackets\stransmitted.*?(\d+)\sreceived.*?(\d+%)\spacket\sloss.*?time\s(\d+ms).*?=\s([^\/]*)\/([^\/]*)\/([^\/]*)\/(.*?)\sms"

    fields = {
        "dest": {"required": True, "type": "str"},
        "count": {"required": False, "type": "int", "default": 2},
        "v4": {"required": False, "type": "boolean"},
        "v6": {"required": False, "type": "boolean"},
        "interface_name": {"required": False, "type": "str"},
        "interface_ip": {"required": False, "type": "str"},
        "interval": {"required": False, "type": "int"},
        "packet_size": {"required": False, "type": "int"},
    }

    module = AnsibleModule(argument_spec=fields)

    # params
    dest = module.params["dest"]
    count = module.params["count"]

    #build command
    cmd = ["ping"]

    if count:
        cmd.append(f"-c { count }")

    cmd.append(dest)

    run_cmd = " ".join(cmd)
    rc, out, err = module.run_command(run_cmd)

    if rc == 1:
        module.fail_json(changed=False, stdout=out, rc=rc, stderr=err, cmd=run_cmd)

    if rc == 0:
        matches = re.search(regex, out, re.MULTILINE | re.DOTALL)
        if matches:
            res = dict()
            res["packet_tx"] = matches.group(7)
            res["packet_rx"] = matches.group(8)
            res["packet_loss"] = matches.group(9)
            res["time_total"] = matches.group(10)
            res["time_min"] = matches.group(11)
            res["time_avg"] = matches.group(12)
            res["time_max"] = matches.group(13)

            module.exit_json(
                changed=False, stdout=out, rc=rc, stderr=err, cmd=run_cmd, parsed=res
            )

    module.exit_json(changed=False, stdout=out, rc=rc, stderr=err, cmd=run_cmd)


if __name__ == "__main__":
    main()
