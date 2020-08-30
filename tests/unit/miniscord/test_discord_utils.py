from unittest import TestCase
import asyncio
from unittest.mock import Mock, AsyncMock
import discord
from miniscord._discord_utils import delete_message, message_id


class TestDeleteMessage(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_success(self):
        mock = AsyncMock()
        self.assertTrue(self.loop.run_until_complete(delete_message(mock)))
        mock.delete.assert_awaited_once()

    def test_forbidden(self):
        mock = AsyncMock()
        mock.delete.side_effect = discord.Forbidden(Mock(), "")
        self.assertFalse(self.loop.run_until_complete(delete_message(mock)))
        mock.delete.assert_awaited_once()

    def test_not_found(self):
        mock = AsyncMock()
        mock.delete.side_effect = discord.NotFound(Mock(), "")
        self.assertFalse(self.loop.run_until_complete(delete_message(mock)))
        mock.delete.assert_awaited_once()


class TestMessageId(TestCase):
    def test_direct(self):
        mock = Mock()
        mock.channel.type = discord.ChannelType.private
        mock.author.id = "TEST"
        self.assertEqual("TEST", message_id(mock))

    def test_not_direct(self):
        mock = Mock()
        mock.channel.type = discord.ChannelType.text
        mock.guild.id = "TEST1"
        mock.channel.id = "TEST2"
        mock.author.id = "TEST3"
        self.assertEqual("TEST1/TEST2/TEST3", message_id(mock))
