# SPDX-FileCopyrightText: 2025 Contributors to the Fedora Project
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import json
import re
import typing

from fedora_messaging import message

from .base import JOURNAL_SCHEMA, SCHEMA_URL


IPA_JOURNAL_FIELDS = (
    "IPA_API_ACTOR",
    "IPA_API_COMMAND",
    "IPA_API_PARAMS",
    "IPA_API_RESULT",
)
IPA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        **JOURNAL_SCHEMA["properties"],
        **{field: {"type": "string"} for field in IPA_JOURNAL_FIELDS},
    },
    "required": [*JOURNAL_SCHEMA["required"], *IPA_JOURNAL_FIELDS],
}

REDACT_FIELDS = ("MESSAGE", "IPA_API_PARAMS")
REDACT_EXPRS = (re.compile(r", \"mail\": \[[^\]]*\]"),)


class IpaMessage(message.Message):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by IPA.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in REDACT_FIELDS:
            for expr in REDACT_EXPRS:
                self.body[field] = expr.sub("", self.body[field])

    @property
    def _params(self):
        return json.loads(self.body["IPA_API_PARAMS"])

    @property
    def app_name(self):
        return "IPA"

    @property
    def app_icon(self):
        return "https://apps.fedoraproject.org/img/icons/ipa.png"

    @property
    def agent_name(self):
        """str: The username of the user who initiated the action that generated this message."""
        return self.body["IPA_API_ACTOR"].partition("@")[0]

    @property
    def result(self):
        """str: The status code of the action."""
        return self.body["IPA_API_RESULT"]


class IpaUserAddV1(IpaMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by IPA when a new user is created.
    """

    # Don't notify in FMN: Noggin already sends a message on this action
    severity = message.DEBUG

    topic = "ipa.user_add.v1"
    body_schema: typing.ClassVar = {
        "id": SCHEMA_URL + topic,
        "description": "Schema for messages sent when a new user is created",
        **IPA_SCHEMA,
    }

    @property
    def user_name(self):
        """str: The user that was created."""
        return self._params["uid"]

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return f"A new user has been created: {self.user_name}\nBy: {self.agent_name}\n"

    @property
    def summary(self):
        """str: Return a summary of the message."""
        return f'{self.agent_name} created user "{self.user_name}"'

    @property
    def usernames(self):
        return [self.user_name, self.agent_name]


class IpaGroupMemberMessage(IpaMessage):
    """
    A base class that defines a message schema for messages published by IPA when new users
    and/or new groups are added or removed from a group.
    """

    # Don't notify in FMN: Noggin already sends a message on these actions
    severity = message.DEBUG

    @property
    def user_names(self):
        """list[str]: The users that were added or removed."""
        return self._params.get("user", [])

    @property
    def group_names(self):
        """list[str]: The groups that were added or removed."""
        return self._params.get("group", [])

    @property
    def group(self):
        """str: The group that the users were added to or removed from."""
        return self._params["cn"]

    @property
    def usernames(self):
        return [self.agent_name, *self.user_names]

    @property
    def groups(self):
        return [self.group, *self.group_names]


class IpaGroupAddMemberV1(IpaGroupMemberMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by IPA when new users are added to a group.
    """

    topic = "ipa.group_add_member.v1"
    body_schema: typing.ClassVar = {
        "id": SCHEMA_URL + topic,
        "description": "Schema for messages sent when new users are added to a group",
        **IPA_SCHEMA,
    }

    def __str__(self):
        """A complete human-readable representation of the message."""
        lines = []
        if self.user_names:
            lines.append(self._collection_text(self.user_names, "user"))
        if self.group_names:
            lines.append(self._collection_text(self.group_names, "group"))
        lines.append(f"\nAdded by: {self.agent_name}\n")
        return "\n".join(lines)

    @property
    def summary(self):
        """str: A summary of the message."""
        words = ["User", self.agent_name, "has added"]
        if self.user_names:
            words.append(self._collection_summary(self.user_names, "user"))
            if self.group_names:
                words.append("and")
        if self.group_names:
            words.append(self._collection_summary(self.group_names, "group"))
        words.extend(["to group", f'"{self.group}"'])
        return " ".join(words)

    def _collection_summary(self, collection, name):
        words = []
        if len(collection) == 1:
            words.append(name)
        else:
            words.append(f"{name}s")
        words.append(", ".join(collection))
        return " ".join(words)

    def _collection_text(self, collection, name):
        lines = []
        lines.append(f"Group {self.group} has ")
        if len(collection) == 1:
            lines[-1] += f"a new {name}:"
        else:
            lines[-1] += f"new {name}s:"
        for entry in collection:
            lines.append(f"- {entry}")
        return "\n".join(lines)


class IpaGroupRemoveMemberV1(IpaGroupMemberMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by IPA when users and/or groups are removed from a group.
    """

    topic = "ipa.group_remove_member.v1"
    body_schema: typing.ClassVar = {
        "id": SCHEMA_URL + topic,
        "description": "Schema for messages sent when new users are removed from a group",
        **IPA_SCHEMA,
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        lines = []
        if self.user_names:
            lines.append(self._collection_text(self.user_names, "user"))
        if self.group_names:
            lines.append(self._collection_text(self.group_names, "group"))
        lines.append(f"\nRemoved by: {self.agent_name}\n")
        return "\n".join(lines)

    @property
    def summary(self):
        """str: A summary of the message."""
        words = ["User", self.agent_name, "has removed"]
        if self.user_names:
            words.append(self._collection_summary(self.user_names, "user"))
            if self.group_names:
                words.append("and")
        if self.group_names:
            words.append(self._collection_summary(self.group_names, "group"))
        words.extend(["from group", f'"{self.group}"'])
        return " ".join(words)

    def _collection_summary(self, collection, name):
        words = []
        if len(collection) == 1:
            words.append(name)
        else:
            words.append(f"{name}s")
        words.append(", ".join(collection))
        return " ".join(words)

    def _collection_text(self, collection, name):
        lines = []
        if len(collection) == 1:
            lines.append(f"The following {name} was removed from group {self.group}:")
        else:
            lines.append(f"The following {name}s were removed from group {self.group}:")
        for entry in collection:
            lines.append(f"- {entry}")
        return "\n".join(lines)
