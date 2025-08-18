from datetime import datetime
from typing import Optional, Union

from pydantic import Field, HttpUrl, ConfigDict, field_serializer

from appodus_utils import Object
from appodus_utils.integrations.messaging.models import WebPushPayload, MessageChannel, MessageRequestRecipient, \
    EmailPayload, SmsPayload, WhatsappPayload, PushPayload, MessageStatus, MessageProviderName, MessagePriority, \
    MessageExtras


class MessageBaseDto(Object):
    pass

class UpsertMessageDto(MessageBaseDto):
    id: Optional[str] = Field(None, description="Unique message identifier")
    channel: MessageChannel = Field(..., description="Communication channel type")
    to: MessageRequestRecipient = Field(..., description="Recipient details")
    payload: Union[
        EmailPayload,
        SmsPayload,
        WhatsappPayload,
        PushPayload,
        WebPushPayload,
    ] = Field(..., description="Content to be sent")
    status: MessageStatus = Field(default=MessageStatus.PENDING, description="Current status of the message")
    provider: Optional[MessageProviderName] = Field(None, description="Message provider (e.g., Twilio, Mailjet)")
    provider_id: Optional[str] = Field(None, description="External ID returned by the provider")
    error: Optional[str] = Field(None, description="Last error message encountered, if any")
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts made so far")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Delivery priority level")
    scheduled_at: Optional[datetime] = Field(None, description="Time at which message is scheduled to be sent")
    sent_at: Optional[datetime] = Field(None, description="Timestamp when the message was actually sent")
    delivered_at: Optional[datetime] = Field(None, description="Timestamp when the message was successfully delivered")
    extras: Optional[MessageExtras] = Field(None, description="Additional custom data or tracking metadata")
    callback_url: Optional[HttpUrl] = Field(None, description="Webhook URL for delivery status")
    # url_tags: Optional[str] = Field(default=None, description="The query tags passed for the CTA")
    # sandbox_mode: Optional[bool] = False

    # @model_validator(mode="after")
    # def validate_recipients(self) -> 'UpsertMessageDto':
    #     def normalize(val):
    #         if val is None:
    #             return []
    #         return val if isinstance(val, list) else [val]
    #
    #     all_recipients = normalize(self.to.recipient)
    #     cc_list = normalize(self.to.cc_recipient)
    #     bcc_list = normalize(self.to.bcc_recipient)
    #
    #     total = len(all_recipients) + len(cc_list) + len(bcc_list)
    #
    #     if self.channel in {MessageChannel.SMS, MessageChannel.WHATSAPP} and total > 1:
    #         raise ValueError(f"{self.channel.value.upper()} supports only one recipient")
    #
    #     if total > 1000:
    #         raise ValueError("Total recipients must not exceed 1000")
    #
    #     email_regex = r'^[^@]+@[^@]+\.[^@]+$'
    #     e164_regex = r'^\+[1-9]\d{1,14}$'
    #     wa_regex = r'^\d{1,15}$'
    #
    #     for recipient in all_recipients + cc_list + bcc_list:
    #         if self.channel == MessageChannel.EMAIL:
    #             if not re.fullmatch(email_regex, recipient):
    #                 raise ValueError(f"Invalid email address: {recipient}")
    #         elif self.channel == MessageChannel.SMS:
    #             if not re.fullmatch(e164_regex, recipient):
    #                 raise ValueError(f"Invalid SMS number (E.164): {recipient}")
    #         elif self.channel == MessageChannel.WHATSAPP:
    #             if not re.fullmatch(wa_regex, recipient):
    #                 raise ValueError(f"Invalid WhatsApp number: {recipient}")
    #         elif self.channel in {MessageChannel.PUSH, MessageChannel.WEB_PUSH}:
    #             if not isinstance(recipient, str) or len(recipient) > 256:
    #                 raise ValueError(f"Invalid device token: {recipient}")
    #
    #     if self.channel != MessageChannel.EMAIL and (cc_list or bcc_list):
    #         raise ValueError("CC and BCC are only supported for email channel")
    #
    #     return self


    @field_serializer("scheduled_at", "sent_at", "delivered_at")
    def serialize_datetimes(self, value: Optional[datetime], _info):
        return value.isoformat() if value else None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "msg_123",
                "channel": "email",
                "to": {
                    "user_id": "user_123",
                    "fullname": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "+2348100000000",
                    "ios_push_token": [{"token": "abc123token", "device_id": "ios_device_1"}],
                    "cc_recipient": [
                        {"name": "Team Member", "email": "team@example.com"}
                    ]
                },
                "payload": {
                    "subject": "Welcome!",
                    "body": "<h1>Welcome</h1><p>Thank you for joining</p>"
                },
                "status": "pending",
                "priority": "normal",
                "extras": {
                    "campaign": "welcome_flow"
                }
            }
        }
    )
