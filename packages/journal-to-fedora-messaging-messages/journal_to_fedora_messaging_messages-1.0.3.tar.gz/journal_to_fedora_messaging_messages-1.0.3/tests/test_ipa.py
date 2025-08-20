# SPDX-FileCopyrightText: 2025 Contributors to the Fedora Project
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Unit tests for the message schema."""

from itertools import chain

import pytest
from fedora_messaging.message import DEBUG

from journal_to_fedora_messaging_messages.ipa import (
    IpaGroupAddMemberV1,
    IpaGroupRemoveMemberV1,
    IpaUserAddV1,
)


@pytest.fixture
def ipa_message_user_add():
    return {
        "_BOOT_ID": "7cf5624e8b3e487986fbd6c1763b8b72",
        "CODE_LINE": "495",
        "CODE_FUNC": "__audit_to_journal",
        "IPA_API_RESULT": "SUCCESS",
        "_SELINUX_CONTEXT": "system_u:system_r:httpd_t:s0",
        "_CAP_EFFECTIVE": "0",
        "_HOSTNAME": "ipa.example.com",
        "_TRANSPORT": "journal",
        "_EXE": "/usr/sbin/httpd",
        "_SYSTEMD_UNIT": "httpd.service",
        "MESSAGE": (
            "[IPA.API] noggin@FEDORAPROJECT.ORG: user_add: SUCCESS [ldap2_140525848914048] "
            '{"uid": "dummy", "givenname": "Dummy", "sn": "User", "cn": "Dummy User", '
            '"displayname": "Dummy User", "initials": "DU", "gecos": "Dummy User", "loginshell": '
            '"/bin/bash", "krbprincipalname": ["dummy@FEDORAPROJECT.ORG"], "mail": '
            '["dummy@example.com"], "random": false, "fastimezone": "UTC", "faslocale": "en-US", '
            '"fasstatusnote": "active", "fascreationtime": {"__datetime__": "20250320000000Z"}, '
            '"all": true, "raw": false, "version": "2.253", "no_members": false}'
        ),
        "_PID": "160139",
        "SYSLOG_IDENTIFIER": "/mod_wsgi",
        "_SYSTEMD_SLICE": "system.slice",
        "PRIORITY": "5",
        "IPA_API_PARAMS": (
            '{"uid": "dummy", "givenname": "Dummy", "sn": "User", "cn": "Dummy User", '
            '"displayname": "Dummy User", "initials": "DU", "gecos": "Dummy User", "loginshell": '
            '"/bin/bash", "krbprincipalname": ["dummy@FEDORAPROJECT.ORG"], "mail": '
            '["dummy@example.com"], "random": false, "fastimezone": "UTC", "faslocale": "en-US", '
            '"fasstatusnote": "active", "fascreationtime": {"__datetime__": "20250320000000Z"}, '
            '"all": true, "raw": false, "version": "2.253", "no_members": false}'
        ),
        "_GID": "387",
        "_MACHINE_ID": "b494e31dbf2749d7934819780b396d66",
        "__REALTIME_TIMESTAMP": "1742430579781629",
        "IPA_API_ACTOR": "noggin@FEDORAPROJECT.ORG",
        "CODE_FILE": "/usr/lib/python3.9/site-packages/ipalib/frontend.py",
        "_SOURCE_REALTIME_TIMESTAMP": "1742430579781599",
        "_CMDLINE": '"(wsgi:ipa)     " -DFOREGROUND',
        "_RUNTIME_SCOPE": "system",
        "IPA_API_COMMAND": "user_add",
        "_SYSTEMD_INVOCATION_ID": "d67f3e6ec1f1463cba99b2baf5a5cb63",
        "MESSAGE_ID": "6d70f1b493df36478bc3499257cd3b17",
        "_COMM": "httpd",
        "_UID": "387",
        "_SYSTEMD_CGROUP": "/system.slice/httpd.service",
    }


@pytest.fixture
def ipa_message_group_add_user():
    return {
        "IPA_API_PARAMS": (
            '{"cn": "developers", "all": false, "raw": false, "version": "2.254", '
            '"no_members": false, "user": ["testing"]}'
        ),
        "__REALTIME_TIMESTAMP": "1742838354523018",
        "_GID": "991",
        "_UID": "992",
        "_SYSTEMD_INVOCATION_ID": "342f3dc5aa0a425e93f88c82edaaa162",
        "_PID": "9201",
        "_TRANSPORT": "journal",
        "PRIORITY": "5",
        "MESSAGE_ID": "6d70f1b493df36478bc3499257cd3b17",
        "_SOURCE_REALTIME_TIMESTAMP": "1742838354522995",
        "_BOOT_ID": "24e0753793004f54b0a4cd1d1c4fbad5",
        "_CAP_EFFECTIVE": "0",
        "IPA_API_ACTOR": "admin@TINYSTAGE.TEST",
        "IPA_API_COMMAND": "group_add_member",
        "_SYSTEMD_UNIT": "httpd.service",
        "_MACHINE_ID": "0e73a05e18f041b9a528a99f7ab13e35",
        "_RUNTIME_SCOPE": "system",
        "_SELINUX_CONTEXT": "system_u:system_r:httpd_t:s0",
        "_SYSTEMD_SLICE": "system.slice",
        "CODE_FILE": "/usr/lib/python3.12/site-packages/ipalib/frontend.py",
        "SYSLOG_IDENTIFIER": "/mod_wsgi",
        "_HOSTNAME": "ipa.tinystage.test",
        "_EXE": "/usr/sbin/httpd",
        "IPA_API_RESULT": "SUCCESS",
        "_SYSTEMD_CGROUP": "/system.slice/httpd.service",
        "CODE_FUNC": "__audit_to_journal",
        "MESSAGE": (
            "[IPA.API] admin@TINYSTAGE.TEST: group_add_member: SUCCESS [ldap2_139734790206096] "
            '{"cn": "developers", "all": false, "raw": false, "version": "2.254", '
            '"no_members": false, "user": ["testing"]}'
        ),
        "_CMDLINE": '"(wsgi:ipa)     " -DFOREGROUND',
        "CODE_LINE": "495",
        "_COMM": "httpd",
    }


@pytest.fixture
def ipa_message_group_remove_user():
    return {
        "_SOURCE_REALTIME_TIMESTAMP": "1742839089995853",
        "_CMDLINE": '"(wsgi:ipa)     " -DFOREGROUND',
        "PRIORITY": "5",
        "SYSLOG_IDENTIFIER": "/mod_wsgi",
        "_PID": "9202",
        "CODE_LINE": "495",
        "_HOSTNAME": "ipa.tinystage.test",
        "_MACHINE_ID": "0e73a05e18f041b9a528a99f7ab13e35",
        "IPA_API_PARAMS": (
            '{"cn": "developers", "all": false, "raw": false, "version": "2.254", '
            '"no_members": false, "user": ["testing"]}'
        ),
        "_TRANSPORT": "journal",
        "CODE_FUNC": "__audit_to_journal",
        "_SELINUX_CONTEXT": "system_u:system_r:httpd_t:s0",
        "_COMM": "httpd",
        "MESSAGE": (
            "[IPA.API] admin@TINYSTAGE.TEST: group_remove_member: SUCCESS [ldap2_139734790190384] "
            '{"cn": "developers", "all": false, "raw": false, "version": "2.254", '
            '"no_members": false, "user": ["testing"]}'
        ),
        "_CAP_EFFECTIVE": "0",
        "MESSAGE_ID": "6d70f1b493df36478bc3499257cd3b17",
        "IPA_API_COMMAND": "group_remove_member",
        "_UID": "992",
        "__REALTIME_TIMESTAMP": "1742839089995893",
        "_SYSTEMD_INVOCATION_ID": "342f3dc5aa0a425e93f88c82edaaa162",
        "IPA_API_RESULT": "SUCCESS",
        "CODE_FILE": "/usr/lib/python3.12/site-packages/ipalib/frontend.py",
        "_SYSTEMD_UNIT": "httpd.service",
        "_EXE": "/usr/sbin/httpd",
        "_SYSTEMD_SLICE": "system.slice",
        "_BOOT_ID": "24e0753793004f54b0a4cd1d1c4fbad5",
        "IPA_API_ACTOR": "admin@TINYSTAGE.TEST",
        "_RUNTIME_SCOPE": "system",
        "_GID": "991",
        "_SYSTEMD_CGROUP": "/system.slice/httpd.service",
    }


def test_user_add(ipa_message_user_add):
    """
    Assert the message schema validates a message with the required fields.
    """
    message = IpaUserAddV1(body=ipa_message_user_add)
    message.validate()
    assert message.app_name == "IPA"
    assert message.app_icon == "https://apps.fedoraproject.org/img/icons/ipa.png"
    assert message.url is None
    assert message.agent_name == "noggin"
    assert message.user_name == "dummy"
    assert message.result == "SUCCESS"
    assert message.usernames == ["dummy", "noggin"]
    assert message.summary == 'noggin created user "dummy"'
    assert str(message) == "A new user has been created: dummy\nBy: noggin\n"
    assert message.severity == DEBUG

    # Some data must be redacted
    for values in chain(message.body.values(), message._params):
        assert "dummy@example.com" not in values


def test_group_add_member(ipa_message_group_add_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    message = IpaGroupAddMemberV1(body=ipa_message_group_add_user)
    message.validate()
    assert message.agent_name == "admin"
    assert message.user_names == ["testing"]
    assert message.result == "SUCCESS"
    assert message.usernames == ["admin", "testing"]
    assert message.summary == 'User admin has added user testing to group "developers"'
    assert str(message) == "Group developers has a new user:\n- testing\n\nAdded by: admin\n"
    assert message.severity == DEBUG


def test_group_add_member_multiple(ipa_message_group_add_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_add_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"user": ["testing1", "testing2"]}'
    )
    message = IpaGroupAddMemberV1(body=ipa_message_group_add_user)
    message.validate()
    assert message.user_names == ["testing1", "testing2"]
    assert message.usernames == ["admin", "testing1", "testing2"]
    assert message.summary == (
        'User admin has added users testing1, testing2 to group "developers"'
    )
    assert str(message) == (
        "Group developers has new users:\n- testing1\n- testing2\n\nAdded by: admin\n"
    )


def test_group_add_member_group_no_user(ipa_message_group_add_user):
    # Example: https://apps.fedoraproject.org/datagrepper/v2/id?id=d2c5f9c4-0ec4-473d-a2fd-de95bbaa01cb&size=extra-large
    ipa_message_group_add_user["IPA_API_PARAMS"] = (
        '{"cn": "gitlab-centos-sig-nfv", "all": true, "raw": false, "version": "2.254", '
        '"no_members": false, "group": ["sig-nfv"]}'
    )
    message = IpaGroupAddMemberV1(body=ipa_message_group_add_user)
    message.validate()
    assert message.user_names == []
    assert message.group_names == ["sig-nfv"]
    assert message.usernames == ["admin"]
    assert message.groups == ["gitlab-centos-sig-nfv", "sig-nfv"]
    assert message.summary == (
        'User admin has added group sig-nfv to group "gitlab-centos-sig-nfv"'
    )
    assert str(message) == (
        "Group gitlab-centos-sig-nfv has a new group:\n- sig-nfv\n\nAdded by: admin\n"
    )


def test_group_add_member_user_and_group(ipa_message_group_add_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_add_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"user": ["testing-user"], "group": ["testing-group"]}'
    )
    message = IpaGroupAddMemberV1(body=ipa_message_group_add_user)
    message.validate()
    assert message.user_names == ["testing-user"]
    assert message.group_names == ["testing-group"]
    assert message.usernames == ["admin", "testing-user"]
    assert message.groups == ["developers", "testing-group"]
    assert message.summary == (
        'User admin has added user testing-user and group testing-group to group "developers"'
    )
    assert str(message) == (
        "Group developers has a new user:\n"
        "- testing-user\n"
        "Group developers has a new group:\n"
        "- testing-group\n"
        "\nAdded by: admin\n"
    )


def test_group_remove_user(ipa_message_group_remove_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    message = IpaGroupRemoveMemberV1(body=ipa_message_group_remove_user)
    message.validate()
    assert message.agent_name == "admin"
    assert message.user_names == ["testing"]
    assert message.result == "SUCCESS"
    assert message.summary == 'User admin has removed user testing from group "developers"'
    assert str(message) == (
        "The following user was removed from group developers:\n- testing\n\nRemoved by: admin\n"
    )
    assert message.severity == DEBUG


def test_group_remove_user_multiple(ipa_message_group_remove_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_remove_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"user": ["testing1", "testing2"]}'
    )
    message = IpaGroupRemoveMemberV1(body=ipa_message_group_remove_user)
    message.validate()
    assert message.user_names == ["testing1", "testing2"]
    assert message.usernames == ["admin", "testing1", "testing2"]
    assert message.summary == (
        'User admin has removed users testing1, testing2 from group "developers"'
    )
    assert str(message) == (
        "The following users were removed from group developers:\n- testing1\n- testing2\n\n"
        "Removed by: admin\n"
    )


def test_group_remove_group(ipa_message_group_remove_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_remove_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"group": ["testing"]}'
    )
    message = IpaGroupRemoveMemberV1(body=ipa_message_group_remove_user)
    message.validate()
    assert message.agent_name == "admin"
    assert message.group_names == ["testing"]
    assert message.user_names == []
    assert message.groups == ["developers", "testing"]
    assert message.result == "SUCCESS"
    assert message.summary == 'User admin has removed group testing from group "developers"'
    assert str(message) == (
        "The following group was removed from group developers:\n- testing\n\nRemoved by: admin\n"
    )
    assert message.severity == DEBUG


def test_group_remove_group_multiple(ipa_message_group_remove_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_remove_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"group": ["testing1", "testing2"]}'
    )
    message = IpaGroupRemoveMemberV1(body=ipa_message_group_remove_user)
    message.validate()
    assert message.group_names == ["testing1", "testing2"]
    assert message.user_names == []
    assert message.usernames == ["admin"]
    assert message.groups == ["developers", "testing1", "testing2"]
    assert message.summary == (
        'User admin has removed groups testing1, testing2 from group "developers"'
    )
    assert str(message) == (
        "The following groups were removed from group developers:\n- testing1\n- testing2\n\n"
        "Removed by: admin\n"
    )


def test_group_remove_member_user_and_group(ipa_message_group_remove_user):
    """
    Assert the message schema validates a message with the required fields.
    """
    ipa_message_group_remove_user["IPA_API_PARAMS"] = (
        '{"cn": "developers", "all": false, "raw": false, "version": "2.254", "no_members": false, '
        '"user": ["testing-user"], "group": ["testing-group"]}'
    )
    message = IpaGroupRemoveMemberV1(body=ipa_message_group_remove_user)
    message.validate()
    assert message.user_names == ["testing-user"]
    assert message.group_names == ["testing-group"]
    assert message.usernames == ["admin", "testing-user"]
    assert message.groups == ["developers", "testing-group"]
    assert message.summary == (
        'User admin has removed user testing-user and group testing-group from group "developers"'
    )
    assert str(message) == (
        "The following user was removed from group developers:\n"
        "- testing-user\n"
        "The following group was removed from group developers:\n"
        "- testing-group\n"
        "\nRemoved by: admin\n"
    )
