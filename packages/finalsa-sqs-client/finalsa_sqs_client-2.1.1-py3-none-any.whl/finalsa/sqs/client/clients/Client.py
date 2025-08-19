from finalsa.sqs.client.exceptions import SqsException
from finalsa.sqs.client.interfaces import SqsService
from finalsa.common.models import SqsReponse, to_sqs_message_attributes
from typing import Dict, List, Union, Optional
import botocore.exceptions
import botocore
import boto3

class SqsServiceImpl(SqsService):

    def __init__(
        self,
    ) -> None:
        self.sqs = boto3.client('sqs')

    def receive_messages(
        self,
        queue_url: str,
        max_number_of_messages: int = 1,
        wait_time_seconds: int = 1
    ) -> List[SqsReponse]:
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['SentTimestamp'],
                MaxNumberOfMessages=max_number_of_messages,
                MessageAttributeNames=['All'],
                WaitTimeSeconds=wait_time_seconds
            )
            if 'Messages' not in response:
                return []
            messages = response['Messages']
            message_responses = []
            for message in messages:
                message_responses.append(
                    SqsReponse.from_boto_response(message))
            return message_responses
        except botocore.exceptions.ClientError as err:
            raise SqsException(err, err.response['Error']['Message'])
        except Exception as ex:
            raise SqsException(ex, "No se pudo recibir el mensaje de la cola")

    def send_raw_message(
        self,
        queue_url: str,
        data: Union[Dict, str],
        message_attributes: Optional[Dict] = None,
    ) -> None:
        message_attributes = message_attributes or {}
        message_attributes = to_sqs_message_attributes(message_attributes)
        message_attributes.update(self.get_default_message_attrs())
        try:
            self.sqs.send_message(
                QueueUrl=queue_url,
                MessageAttributes=message_attributes,
                MessageBody=self.__dump_payload__(data)
            )
        except botocore.exceptions.ClientError as err:
            raise SqsException(err, err.response['Error']['Message'])
        except Exception as ex:
            raise SqsException(ex, "No se pudo enviar el mensaje a la cola")

    def delete_message(self, queue_url: str, receipt_handle: str):
        try:
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
        except botocore.exceptions.ClientError as err:
            raise SqsException(err, err.response['Error']['Message'])
        except Exception as ex:
            raise SqsException(
                ex, f"The message could not be deleted from the queue {receipt_handle}")

    def get_queue_arn(self, queue_url: str):
        response = self.get_queue_attributes(queue_url)
        return response['Attributes']['QueueArn']

    def get_queue_attributes(self, queue_url: str):
        response = self.sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=[
                'All',
            ]
        )
        return response

    def get_queue_url(self, queue_name: str):
        response = self.sqs.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']
