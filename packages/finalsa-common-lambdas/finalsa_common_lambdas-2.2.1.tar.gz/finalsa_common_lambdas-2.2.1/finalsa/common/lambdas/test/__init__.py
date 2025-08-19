from datetime import datetime, timezone
from json import dumps
from typing import Dict, List, Optional, Union
from uuid import uuid4

from finalsa.common.lambdas.app.App import App
from finalsa.common.lambdas.common.constants import TIMESTAMP_HEADER
from finalsa.traceability.functions import (
    ASYNC_CONTEXT_CORRELATION_ID,
    HTTP_HEADER_CORRELATION_ID,
    HTTP_HEADER_TRACE_ID,
)


class TestContext:

    def __init__(self):
        self.aws_request_id = f"test-{uuid4()}"


class Consumer:

    def __init__(self, app: App) -> None:
        self.app = app

    def consume(
            self,
            payload: Dict,
            topic: str,
            timestamp: Optional[datetime] = None
    ) -> Union[List[Optional[Dict]], Dict]:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        if isinstance(payload, Dict):
            payload = dumps(payload)

        sns_event = {
            "Type": "Notification",
            "MessageId": str(uuid4()),
            "TopicArn": f"arn:aws:sns:us-east-1:123456789012:{topic}",
            "Message": payload,
            "MessageAttributes": {
                ASYNC_CONTEXT_CORRELATION_ID: {
                    "Type": "String",
                    "Value": "test-correlation-id",
                },
                TIMESTAMP_HEADER: {
                    "Type": "String",
                    "Value": timestamp.isoformat(),
                },
            },
            "Timestamp": timestamp.isoformat(),
            "SignatureVersion": "1",
            "Signature": "EXAMPLE",

        }
        data = {
            "Records": [
                {
                    "messageId": str(uuid4()),
                    "receiptHandle": "MessageReceiptHandle",
                    "body": dumps(sns_event),
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1523232000000",
                        "SenderId": "123456789012",
                        "ApproximateFirstReceiveTimestamp": "1523232000001"
                    },
                }
            ]
        }
        context = TestContext()
        return self.app.execute(data, context)


class HttpClient:

    def __init__(self, app: App) -> None:
        self.app = app

    def fix_headers(self, headers: Dict, timestamp: Optional[datetime] = None) -> Dict:
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        if HTTP_HEADER_CORRELATION_ID not in headers:
            headers[HTTP_HEADER_CORRELATION_ID] = f"test-{uuid4()}"
        if HTTP_HEADER_TRACE_ID not in headers:
            headers[HTTP_HEADER_TRACE_ID] = f"test-{uuid4()}"
        if TIMESTAMP_HEADER not in headers:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            headers[TIMESTAMP_HEADER] = timestamp.isoformat()
        else:
            headers[TIMESTAMP_HEADER] = datetime.fromisoformat(
                headers[TIMESTAMP_HEADER]
            ).isoformat()
        return headers

    def get(
        self,
        path: str,
        headers: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if headers is None:
            headers = {}
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        data = {
            "httpMethod": "GET",
            "path": path,
            "headers": self.fix_headers(headers, timestamp),
            "body": "",
        }
        if query_params:
            data["queryStringParameters"] = query_params
        return self.app.execute(data, TestContext())

    def post(
        self,
        path: str,
        payload: Dict,
        headers: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if isinstance(payload, Dict):
            payload = dumps(payload)
        if headers is None:
            headers = {}
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        data = {
            "httpMethod": "POST",
            "path": path,
            "headers": self.fix_headers(headers, timestamp),
            "body": payload,
        }
        if query_params:
            data["queryStringParameters"] = query_params
        return self.app.execute(data, TestContext())

    def put(
        self,
        path: str,
        payload: Dict,
        headers: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if isinstance(payload, Dict):
            payload = dumps(payload)
        if headers is None:
            headers = {}
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        data = {
            "httpMethod": "PUT",
            "path": path,
            "headers": self.fix_headers(headers, timestamp),
            "body": payload,
        }
        if query_params:
            data["queryStringParameters"] = query_params
        return self.app.execute(data, TestContext())

    def delete(
        self,
        path: str,
        headers: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if headers is None:
            headers = {}
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        data = {
            "httpMethod": "DELETE",
            "path": path,
            "headers": self.fix_headers(headers, timestamp),
            "body": "",
        }
        if query_params:
            data["queryStringParameters"] = query_params
        return self.app.execute(data, TestContext())

    def patch(
        self,
        path: str,
        payload: Dict,
        headers: Optional[Dict] = None,
        timestamp: Optional[datetime] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        if not self.app.__is_test__:
            raise Exception("Test mode not enabled")
        if isinstance(payload, Dict):
            payload = dumps(payload)
        if headers is None:
            headers = {}
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        data = {
            "httpMethod": "PATCH",
            "path": path,
            "headers": self.fix_headers(headers, timestamp),
            "body": payload,
        }
        if query_params:
            data["queryStringParameters"] = query_params
        return self.app.execute(data, TestContext())
