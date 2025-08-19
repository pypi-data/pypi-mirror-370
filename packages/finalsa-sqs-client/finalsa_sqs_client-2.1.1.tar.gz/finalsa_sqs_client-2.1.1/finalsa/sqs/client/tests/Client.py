from finalsa.sqs.client.interfaces import SqsService
from finalsa.common.models import SqsReponse, to_sqs_message_attributes
from finalsa.traceability import set_correlation_id
from typing import Dict, List, Union, Optional
from uuid import uuid4

class SqsServiceTest(SqsService):

    def __init__(
        self,
    ) -> None:
        self.messages = {}
        set_correlation_id("test")

    def receive_messages(
            self,
            queue_url: str,
            max_number_of_messages: int = 1,
            _: int = 1
    ) -> List[SqsReponse]:
        if queue_url not in self.messages:
            return []
        messages = self.messages[queue_url]
        if len(messages) == 0:
            return []
        message_responses = []
        while len(messages) > 0 and len(message_responses) < max_number_of_messages:
            message_responses.append(messages.pop(0))
        return message_responses

    def send_raw_message(
            self,
            queue_url: str,
            data: Union[Dict, str],
            message_attributes: Optional[Dict] = None,
    ) -> None:
        if queue_url not in self.messages:
            self.messages[queue_url] = []
        message_attributes = message_attributes or {}
        message_attributes = to_sqs_message_attributes(message_attributes)
        message_attributes.update(self.get_default_message_attrs())
        self.messages[queue_url].append(SqsReponse.from_boto_response({
            'MessageId': str(uuid4()),
            'ReceiptHandle': str(uuid4()),
            'MD5OfBody': str(uuid4()),
            'Body': self.__dump_payload__(data),
            'Attributes': {},
            'MessageAttributes': message_attributes,
        }))

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        if queue_url not in self.messages:
            return
        messages = self.messages[queue_url]
        for i, message in enumerate(messages):
            if message.receipt_handle == receipt_handle:
                messages.pop(i)
                return

    def get_queue_arn(self, _: str) -> str:
        return 'arn:aws:sqs:us-east-1:123456789012:MyQueue'

    def get_queue_attributes(self, _: str, ) -> Dict:
        return {
            "QueueArn": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
            "ApproximateNumberOfMessages": "0",
            "ApproximateNumberOfMessagesNotVisible": "0",
            "ApproximateNumberOfMessagesDelayed": "0",
        }

    def get_queue_url(self, queue_name: str) -> str:
        return f"https://sqs.us-east-1.amazonaws.com/123456789012/{queue_name}"
