from unittest import TestCase
import asyncio


class AsyncTestCase(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def _await(self, fn):
        return self.loop.run_until_complete(fn)
