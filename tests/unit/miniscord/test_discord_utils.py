from unittest import TestCase
from unittest.mock import Mock, AsyncMock
from tests.utils import AsyncTestCase

import discord
from miniscord._discord_utils import delete_message, message_id


class TestDeleteMessage(AsyncTestCase):
    def test_success(self):
        message = AsyncMock()
        self.assertTrue(self._await(delete_message(message)))
        message.delete.assert_awaited_once()

    def test_forbidden(self):
        message = AsyncMock()
        message.delete.side_effect = discord.Forbidden(Mock(), "")
        self.assertFalse(self._await(delete_message(message)))
        message.delete.assert_awaited_once()

    def test_not_found(self):
        message = AsyncMock()
        message.delete.side_effect = discord.NotFound(Mock(), "")
        self.assertFalse(self._await(delete_message(message)))
        message.delete.assert_awaited_once()


class TestMessageId(TestCase):
    def test_direct(self):
        message = Mock()
        message.channel.type = discord.ChannelType.private
        message.author.id = "TEST"
        self.assertEqual("TEST", message_id(message))

    def test_not_direct(self):
        message = Mock()
        message.channel.type = discord.ChannelType.text
        message.guild.id = "TEST1"
        message.channel.id = "TEST2"
        message.author.id = "TEST3"
        self.assertEqual("TEST1/TEST2/TEST3", message_id(message))
