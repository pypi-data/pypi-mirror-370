from finalsa.common.models import (SqsReponse)
from typing import Dict, List, Union, Optional
from uuid import uuid4
from abc import ABC, abstractmethod
from orjson import dumps, loads
from finalsa.traceability import (
    get_w3c_traceparent, get_w3c_tracestate
)
from finalsa.traceability.functions import (
    HTTP_HEADER_TRACEPARENT, HTTP_HEADER_TRACESTATE,
)


class SqsService(ABC):

    @staticmethod
    def default_correlation_id():
        return str(uuid4())

    @abstractmethod
    def receive_messages(
            self,
            queue_url: str,
            max_number_of_messages: int = 1,
            wait_time_seconds: int = 1
    ) -> List[SqsReponse]:
        pass

    def send_message(
            self,
            queue_url: str,
            payload: Dict,
            message_attributes: Optional[Dict] = None,
    ) -> None:
        self.send_raw_message(queue_url, payload, message_attributes)

    def get_default_message_attrs(
        self,
    ) -> Dict:
        result = {
            HTTP_HEADER_TRACEPARENT: {'DataType': 'String', 'StringValue': get_w3c_traceparent()},
            HTTP_HEADER_TRACESTATE: {'DataType': 'String', 'StringValue': get_w3c_tracestate()},
        }
        return result

    @abstractmethod
    def send_raw_message(
            self,
            queue_url: str,
            data: Union[Dict, str],
            message_attributes: Optional[Dict] = None,
    ) -> None:
        pass

    @staticmethod
    def __dump_payload__(payload: Union[Dict, str]) -> str:
        if isinstance(payload, dict):
            body = dumps(payload)
            return body.decode()
        if isinstance(payload, str):
            return payload
        raise TypeError("Unsupported payload type; expected dict or str")

    @staticmethod
    def __parse_to_message__(
        payload: Union[Dict, str],
    ) -> Dict:
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str):
            try:
                parsed = loads(payload)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        # Fallback to empty dict if not parseable
        return {}

    @abstractmethod
    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        pass

    @abstractmethod
    def get_queue_arn(self, queue_url: str) -> str:
        pass

    @abstractmethod
    def get_queue_attributes(self, queue_url: str, ) -> Dict:
        pass

    @abstractmethod
    def get_queue_url(self, queue_name: str) -> str:
        pass
