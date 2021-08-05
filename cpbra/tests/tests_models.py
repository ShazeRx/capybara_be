from django.test import TestCase
from model_bakery import baker

from cpbra.models import Message


class MessageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.channel = baker.make('Channel')
        cls.messages = baker.make('Message', _quantity=20, channel=cls.channel)

    def test_should_return_10_messages(self):
        self.assertEqual(Message.objects.get_last_10_messages_from_now(self.channel).count(), 10)

    def test_should_return_10_mesages_from_timestamp(self):
        messages = self.messages[-5:]
        from_timestamp = messages[0].timestamp
        response = Message.objects.get_last_10_messages_from_timestamp(from_timestamp, self.channel)
        self.assertEqual(response.count(), 10)
        assert response.first().timestamp < from_timestamp
        assert response[response.count() - 1].timestamp < from_timestamp
