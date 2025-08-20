# SPDX-FileCopyrightText: 2025 Contributors to the Fedora Project
#
# SPDX-License-Identifier: LGPL-3.0-or-later


SCHEMA_URL = "http://fedoraproject.org/message-schema/"

# Data is usually serialized as strings.
# If it's huge, it can be serialized as null.
# If it's a binary, it's serialized as an array of numbers
# https://systemd.io/JOURNAL_EXPORT_FORMATS/#journal-json-format
JOURNAL_VALUE = {"type": ["string", "null", "array"], "items": {"type": "number"}}

# See https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html
JOURNAL_SCHEMA = {
    "type": "object",
    "properties": {
        "_HOSTNAME": {"type": "string"},
        "_CMDLINE": {"type": "string"},
        "_COMM": {"type": "string"},
        "ERRNO": {"type": "string"},
        "_EXE": {"type": "string"},
        "_PID": {"type": "string"},
        "_UID": {"type": "string"},
        "_GID": {"type": "string"},
        "PRIORITY": {"type": "string"},
        "MESSAGE": JOURNAL_VALUE,
        "CODE_FILE": {"type": "string"},
        "CODE_FUNC": {"type": "string"},
        "CODE_LINE": {"type": "string"},
        "SYSLOG_FACILITY": {"type": "string"},
        "SYSLOG_IDENTIFIER": {"type": "string"},
        "SYSLOG_PID": {"type": "string"},
        "SYSLOG_TIMESTAMP": {"type": "string"},
        "_SYSTEMD_CGROUP": {"type": "string"},
        "_SYSTEMD_SLICE": {"type": "string"},
        "_SYSTEMD_UNIT": {"type": "string"},
        "_SYSTEMD_INVOCATION_ID": {"type": "string"},
        "__REALTIME_TIMESTAMP": {"type": "string"},
        "_SOURCE_REALTIME_TIMESTAMP": {"type": "string"},
    },
    "required": ["_HOSTNAME", "_COMM", "MESSAGE", "PRIORITY", "__REALTIME_TIMESTAMP"],
}
