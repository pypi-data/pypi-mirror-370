from typing import Any, Dict, Union

from finalsa.common.models import SqsReponse

try:
    from orjson import loads
except ImportError:
    from json import loads


class SqsEvent(SqsReponse):
    event_source: str
    event_source_arn: str
    aws_region: str
    original_payload: str

    def get_original_payload(self) -> Union[Dict, str]:
        try:
            return loads(self.original_payload)
        except Exception:
            return self.original_payload

    def try_parse(self) -> Union[Dict, str]:
        try:
            payload = self.parse()
            return payload
        except Exception:
            return self.original_payload

    @classmethod
    def from_sqs_lambda_event(cls, event: Dict[str, Any]) -> 'SqsEvent':
        event_source = event.get('eventSource', "")
        event_source_arn = event.get('eventSourceARN', "")
        aws_region = event.get('awsRegion', "")
        message_id = event.get('messageId', '')
        attributes = event.get('attributes', {})
        message_attributes = event.get('messageAttributes', {})
        md5_of_body = event.get('md5OfBody', '')
        receipt_handle = event.get('receiptHandle', '')
        body = event.get('body', '')
        return cls(
            event_source=event_source,
            event_source_arn=event_source_arn,
            aws_region=aws_region,
            message_id=message_id,
            receipt_handle=receipt_handle,
            original_payload=body,
            attributes=attributes,
            message_attributes=message_attributes,
            md5_of_body=md5_of_body,
            body=body
        )
