from logging import Logger
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from kink import inject, di

from main.app.config.settings import settings
from main.app.domain.message.message_payload_builder import MessageRecipientBuilder
from main.app.domain.user.auth.active_auditor.service import ActiveAuditorService
from main.app.integrations.messaging.channel_sender import MessageDispatcher
from main.app.integrations.messaging.models import (
    MessageChannel, MultiChannelMessageRequest,
    MessageRequestRecipient, MessageCategory, MessageRecipientUserId, MessageContextModule
)
from main.app.integrations.messaging.templating.models import AvailableTemplate

logger: Logger = di["logger"]


@inject
class ListingManagementMessages(BaseMessageSender):
    """Handles all property listing related notifications"""

    async def send_property_listed_success_message(self, recipient_user_id: MessageRecipientUserId,
                                                   context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PROPERTY_LISTED_SUCCESS,
            context_modules=context_modules,
            category=MessageCategory.LISTING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_property_rejected_message(self, recipient_user_id: MessageRecipientUserId,
                                             context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PROPERTY_REJECTED_REASONS,
            context_modules=context_modules,
            category=MessageCategory.LISTING,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_listing_pending_moderation_message(self, recipient_user_id: MessageRecipientUserId,
                                                      context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.LISTING_PENDING_MODERATION,
            context_modules=context_modules,
            category=MessageCategory.LISTING,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_listing_performance_summary(self, recipient_user_id: MessageRecipientUserId,
                                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.LISTING_PERFORMANCE_SUMMARY,
            context_modules=context_modules,
            category=MessageCategory.ANALYTICS,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_price_suggestion_trends(self, recipient_user_id: MessageRecipientUserId,
                                           context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PRICE_SUGGESTION_TRENDS,
            context_modules=context_modules,
            category=MessageCategory.ANALYTICS,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )


@inject
class BuyerNotificationMessages(BaseMessageSender):
    """Handles all buyer-related notifications"""

    async def send_new_property_match(self, recipient_user_id: MessageRecipientUserId,
                                      context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_PROPERTY_MATCH_SAVED_SEARCH,
            context_modules=context_modules,
            category=MessageCategory.ALERT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_price_drop_alert(self, recipient_user_id: MessageRecipientUserId,
                                    context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PRICE_DROP_SAVED_PROPERTY,
            context_modules=context_modules,
            category=MessageCategory.ALERT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_seller_reply_notification(self, recipient_user_id: MessageRecipientUserId,
                                             context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.SELLER_REPLIED_TO_INQUIRY,
            context_modules=context_modules,
            category=MessageCategory.MESSAGE,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_new_message_from_agent(self, recipient_user_id: MessageRecipientUserId,
                                          context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_MESSAGE_FROM_SELLER_AGENT,
            context_modules=context_modules,
            category=MessageCategory.MESSAGE,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_inquiry_confirmation(self, recipient_user_id: MessageRecipientUserId,
                                        context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.INQUIRY_CONFIRMATION,
            context_modules=context_modules,
            category=MessageCategory.CONFIRMATION,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_tour_confirmation(self, recipient_user_id: MessageRecipientUserId,
                                     context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.SCHEDULE_TOUR_CONFIRMATION,
            context_modules=context_modules,
            category=MessageCategory.CONFIRMATION,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_tour_rescheduled_cancelled(self, recipient_user_id: MessageRecipientUserId,
                                              context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.TOUR_RESCHEDULED_CANCELLED,
            context_modules=context_modules,
            category=MessageCategory.UPDATE,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )


@inject
class ReminderAlertMessages(BaseMessageSender):
    """Handles all reminder and alert notifications"""

    async def send_tour_reminder(self, recipient_user_id: MessageRecipientUserId,
                                 context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.BUYER_TOUR_REMINDER,
            context_modules=context_modules,
            category=MessageCategory.REMINDER,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_inactive_user_reengagement(self, recipient_user_id: MessageRecipientUserId,
                                              context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.INACTIVE_USER_REENGAGEMENT,
            context_modules=context_modules,
            category=MessageCategory.REENGAGEMENT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )


@inject
class AgentEngagementMessages(BaseMessageSender):
    """Handles all agent engagement notifications"""

    async def send_new_buyer_lead_alert(self, recipient_user_id: MessageRecipientUserId,
                                        context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_BUYER_LEAD_ALERT,
            context_modules=context_modules,
            category=MessageCategory.LEAD,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_buyer_scheduled_visit(self, recipient_user_id: MessageRecipientUserId,
                                         context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.BUYER_SCHEDULED_VISIT,
            context_modules=context_modules,
            category=MessageCategory.APPOINTMENT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_buyer_canceled_visit(self, recipient_user_id: MessageRecipientUserId,
                                        context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.BUYER_CANCELED_VISIT,
            context_modules=context_modules,
            category=MessageCategory.APPOINTMENT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_agent_performance_summary(self, recipient_user_id: MessageRecipientUserId,
                                             context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.AGENT_PERFORMANCE_SUMMARY,
            context_modules=context_modules,
            category=MessageCategory.ANALYTICS,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_new_agent_review_notification(self, recipient_user_id: MessageRecipientUserId,
                                                 context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_REVIEW_FOR_AGENT,
            context_modules=context_modules,
            category=MessageCategory.REVIEW,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH
            ]
        )


@inject
class TransactionMessages(BaseMessageSender):
    """Handles all transaction-related notifications"""

    async def send_offer_submitted_confirmation(self, recipient_user_id: MessageRecipientUserId,
                                                context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.OFFER_SUBMITTED_CONFIRMATION,
            context_modules=context_modules,
            category=MessageCategory.CONFIRMATION,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_offer_received_notification(self, recipient_user_id: MessageRecipientUserId,
                                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.OFFER_RECEIVED_TO_SELLER,
            context_modules=context_modules,
            category=MessageCategory.OFFER,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_offer_accepted_notification(self, recipient_user_id: MessageRecipientUserId,
                                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.OFFER_ACCEPTED,
            context_modules=context_modules,
            category=MessageCategory.OFFER,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_offer_rejected_notification(self, recipient_user_id: MessageRecipientUserId,
                                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.OFFER_REJECTED,
            context_modules=context_modules,
            category=MessageCategory.OFFER,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_counter_offer_received(self, recipient_user_id: MessageRecipientUserId,
                                          context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.COUNTER_OFFER_RECEIVED,
            context_modules=context_modules,
            category=MessageCategory.OFFER,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_escrow_initiated_notification(self, recipient_user_id: MessageRecipientUserId,
                                                 context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ESCROW_INITIATED,
            context_modules=context_modules,
            category=MessageCategory.TRANSACTION,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_escrow_status_update(self, recipient_user_id: MessageRecipientUserId,
                                        context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ESCROW_STATUS_UPDATE,
            context_modules=context_modules,
            category=MessageCategory.TRANSACTION,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_transaction_completed_notification(self, recipient_user_id: MessageRecipientUserId,
                                                      context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.TRANSACTION_COMPLETED,
            context_modules=context_modules,
            category=MessageCategory.TRANSACTION,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_transaction_failed_notification(self, recipient_user_id: MessageRecipientUserId,
                                                   context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.TRANSACTION_FAILED_DECLINED,
            context_modules=context_modules,
            category=MessageCategory.TRANSACTION,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )


@inject
class PostSaleMessages(BaseMessageSender):
    """Handles all post-sale follow-up messages"""

    async def send_buyer_feedback_request(self, recipient_user_id: MessageRecipientUserId,
                                          context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.POST_SALE_BUYER_FEEDBACK_REQUEST,
            context_modules=context_modules,
            category=MessageCategory.FEEDBACK,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_seller_feedback_request(self, recipient_user_id: MessageRecipientUserId,
                                           context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.POST_SALE_SELLER_FEEDBACK_REQUEST,
            context_modules=context_modules,
            category=MessageCategory.FEEDBACK,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_buyer_referral_incentive(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.BUYER_REFERRAL_INCENTIVE,
            context_modules=context_modules,
            category=MessageCategory.REFERRAL,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_seller_referral_incentive(self, recipient_user_id: MessageRecipientUserId,
                                             context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.SELLER_REFERRAL_INCENTIVE,
            context_modules=context_modules,
            category=MessageCategory.REFERRAL,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )


@inject
class TrustSafetyMessages(BaseMessageSender):
    """Handles all trust and safety related notifications"""

    async def send_id_verification_pending(self, recipient_user_id: MessageRecipientUserId,
                                           context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ID_DOCUMENT_VERIFICATION_PENDING,
            context_modules=context_modules,
            category=MessageCategory.VERIFICATION,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH
            ]
        )

    async def send_id_verification_result(self, recipient_user_id: MessageRecipientUserId,
                                          context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ID_DOCUMENT_REJECTED_ACCEPTED,
            context_modules=context_modules,
            category=MessageCategory.VERIFICATION,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_fraud_warning_alert(self, recipient_user_id: MessageRecipientUserId,
                                       context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.FRAUD_WARNING_ALERT,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_terms_policy_update(self, recipient_user_id: MessageRecipientUserId,
                                       context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.TERMS_POLICY_UPDATES,
            context_modules=context_modules,
            category=MessageCategory.ADMIN,
            default_channels=[MessageChannel.EMAIL]
        )


@inject
class ProductUpdateMessages(BaseMessageSender):
    """Handles all product update and feature announcements"""

    async def send_new_feature_announcement(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_FEATURE_ANNOUNCEMENT,
            context_modules=context_modules,
            category=MessageCategory.PRODUCT_IMPROVEMENT,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_feature_test_invitation(self, recipient_user_id: MessageRecipientUserId,
                                           context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.INVITE_TEST_NEW_FEATURE,
            context_modules=context_modules,
            category=MessageCategory.PRODUCT_IMPROVEMENT,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_post_transaction_feedback_request(self, recipient_user_id: MessageRecipientUserId,
                                                     context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.FEEDBACK_REQUEST_POST_TRANSACTION,
            context_modules=context_modules,
            category=MessageCategory.FEEDBACK,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_product_improvement_survey(self, recipient_user_id: MessageRecipientUserId,
                                              context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.SURVEY_PRODUCT_IMPROVEMENT,
            context_modules=context_modules,
            category=MessageCategory.FEEDBACK,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )


@inject
class MarketingMessages(BaseMessageSender):
    """Handles all marketing and promotional messages"""

    async def send_seller_tips(self, recipient_user_id: MessageRecipientUserId,
                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.SELLER_TIPS_CONTENT,
            context_modules=context_modules,
            category=MessageCategory.MARKETING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_buyer_tips(self, recipient_user_id: MessageRecipientUserId,
                              context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.BUYER_TIPS_CONTENT,
            context_modules=context_modules,
            category=MessageCategory.MARKETING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )

    async def send_referral_program_invitation(self, recipient_user_id: MessageRecipientUserId,
                                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.REFERRAL_PROGRAM_INVITATION,
            context_modules=context_modules,
            category=MessageCategory.MARKETING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )

    async def send_holiday_greeting(self, recipient_user_id: MessageRecipientUserId,
                                    context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.HOLIDAY_FESTIVE_GREETING,
            context_modules=context_modules,
            category=MessageCategory.MARKETING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_limited_time_promo(self, recipient_user_id: MessageRecipientUserId,
                                      context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.LIMITED_TIME_PROMO_DISCOUNT,
            context_modules=context_modules,
            category=MessageCategory.MARKETING,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH,
                MessageChannel.WEB_PUSH
            ]
        )
