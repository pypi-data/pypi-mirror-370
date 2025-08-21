"""
SQS utilities for trace ID propagation
"""
from typing import Any, Dict, Optional

from .logger import get_logger
from .trace_context import TRACE_ID_HEADER, get_trace_id, set_trace_id

logger = get_logger(__name__)


def add_trace_to_message_attributes(
    message_attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add trace ID to SQS message attributes.

    Args:
        message_attributes: Existing message attributes (optional)

    Returns:
        Message attributes with trace ID added
    """
    if message_attributes is None:
        message_attributes = {}
    else:
        message_attributes = message_attributes.copy()

    trace_id = get_trace_id()
    if trace_id:
        message_attributes[TRACE_ID_HEADER] = {
            "StringValue": trace_id,
            "DataType": "String",
        }

    return message_attributes


def extract_trace_from_message_attributes(
    message_attributes: Optional[Dict[str, Any]]
) -> Optional[str]:
    """
    Extract trace ID from SQS message attributes.

    Args:
        message_attributes: Message attributes from SQS message

    Returns:
        Trace ID if found, None otherwise
    """
    if not message_attributes:
        return None

    trace_attr = message_attributes.get(TRACE_ID_HEADER)
    if trace_attr and isinstance(trace_attr, dict):
        return trace_attr.get("StringValue")

    return None


def send_message_with_trace(sqs_client, **kwargs) -> Dict[str, Any]:
    """
    Send an SQS message with trace ID automatically added.

    This wraps the boto3 SQS client's send_message method.

    Args:
        sqs_client: boto3 SQS client
        **kwargs: Arguments for send_message

    Returns:
        Response from send_message
    """
    # Add trace ID to message attributes
    kwargs["MessageAttributes"] = add_trace_to_message_attributes(
        kwargs.get("MessageAttributes")
    )

    trace_id = get_trace_id()
    logger.debug(
        "Sending SQS message",
        extra={
            "queue_url": kwargs.get("QueueUrl"),
            "trace_id": trace_id,
            "message_attributes": list(kwargs.get("MessageAttributes", {}).keys()),
        },
    )

    return sqs_client.send_message(**kwargs)


def send_message_batch_with_trace(sqs_client, **kwargs) -> Dict[str, Any]:
    """
    Send a batch of SQS messages with trace ID automatically added to each.

    This wraps the boto3 SQS client's send_message_batch method.

    Args:
        sqs_client: boto3 SQS client
        **kwargs: Arguments for send_message_batch

    Returns:
        Response from send_message_batch
    """
    # Add trace ID to each message in the batch
    entries = kwargs.get("Entries", [])
    for entry in entries:
        entry["MessageAttributes"] = add_trace_to_message_attributes(
            entry.get("MessageAttributes")
        )

    trace_id = get_trace_id()
    logger.debug(
        "Sending SQS message batch",
        extra={
            "queue_url": kwargs.get("QueueUrl"),
            "trace_id": trace_id,
            "batch_size": len(entries),
        },
    )

    return sqs_client.send_message_batch(**kwargs)


def process_sqs_message(message: Dict[str, Any], handler_func, *args, **kwargs):
    """
    Process an SQS message with trace context.

    This extracts the trace ID from the message and sets it in the context
    before calling the handler function.

    Args:
        message: SQS message dict
        handler_func: Function to process the message
        *args, **kwargs: Arguments passed to handler_func

    Returns:
        Result from handler_func
    """
    # Extract trace ID from message attributes
    trace_id = extract_trace_from_message_attributes(message.get("MessageAttributes"))

    if trace_id:
        logger.debug(
            "Processing SQS message with trace",
            extra={"trace_id": trace_id, "message_id": message.get("MessageId")},
        )
        set_trace_id(trace_id)
    else:
        logger.debug(
            "Processing SQS message without trace",
            extra={"message_id": message.get("MessageId")},
        )

    # Call the handler function
    return handler_func(message, *args, **kwargs)


def receive_message_with_trace(sqs_client, **kwargs) -> Dict[str, Any]:
    """Receive message and set trace context from message attributes"""
    response = sqs_client.receive_message(**kwargs)

    if "Messages" in response:
        for message in response["Messages"]:
            trace_id = extract_trace_from_message_attributes(
                message.get("MessageAttributes")
            )
            if trace_id:
                # Set the trace context for the first message with a trace
                set_trace_id(trace_id)
                break  # Use the first message's trace ID for context

    return response


class TracedSQSClient:
    """
    A wrapper around boto3 SQS client that automatically adds trace IDs to messages.
    """

    def __init__(self, sqs_client):
        self.sqs_client = sqs_client

    def send_message(self, **kwargs) -> Dict[str, Any]:
        """Send message with trace ID"""
        return send_message_with_trace(self.sqs_client, **kwargs)

    def send_message_batch(self, **kwargs) -> Dict[str, Any]:
        """Send message batch with trace IDs"""
        return send_message_batch_with_trace(self.sqs_client, **kwargs)

    def receive_message(self, **kwargs) -> Dict[str, Any]:
        """Receive message and extract trace ID from message attributes."""
        return receive_message_with_trace(self.sqs_client, **kwargs)

    def __getattr__(self, name):
        """Delegate other methods to the wrapped client"""
        return getattr(self.sqs_client, name)
