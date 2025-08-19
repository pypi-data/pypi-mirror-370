from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger as log

from .mail import Email


@dataclass
class Me:
    businessPhones: Any
    displayName: str
    givenName: str
    jobTitle: str
    mail: str
    mobilePhone: Any
    officeLocation: Any
    preferredLanguage: Any
    surname: str
    userPrincipalName: Any
    id: str


@dataclass
class Organization:
    id: str
    deletedDateTime: Any
    businessPhones: Any
    city: Any
    country: Any
    countryLetterCode: Any
    createdDateTime: Any
    defaultUsageLocation: Any
    displayName: str
    isMultipleDataLocationsForServicesEnabled: Any
    marketingNotificationEmails: Any
    onPremisesLastSyncDateTime: Any
    onPremisesSyncEnabled: Any
    partnerTenantType: Any
    postalCode: Any
    preferredLanguage: Any
    securityComplianceNotificationMails: Any
    securityComplianceNotificationPhones: Any
    state: Any
    street: Any
    technicalNotificationMails: Any
    tenantType: str
    directorySizeQuota: Any
    privacyProfile: Any
    assignedPlans: Any
    onPremisesSyncStatus: Any
    provisionedPlans: Any
    verifiedDomains: Any


class GraphAPI:
    def __init__(self, token: str, version: str = "v1.0"):
        self.token: str = token
        self.version = version.strip("/")
        self.base_url = f"https://graph.microsoft.com/{self.version}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def __repr__(self):
        return f"[GraphAPI.{self.token[:4]}"

    @property
    def me(self):
        info: dict = self.request(
            method="get",
            resource="me"
        )
        del info['@odata.context']
        return Me(**info)

    @property
    def organization(self):
        """Get user's organization/tenant info from Graph API"""
        info = self.request(
            "GET",
            "organization"
        )
        info = info["value"][0]
        inst = Organization(**info)
        log.debug(f"{self}: Got user's organizational info:\n  - org={inst}")
        return inst

    @property
    def messages(self):
        """Get all messages and return as Email objects"""
        return self._get_messages()

    def _get_messages(self, filter_query=None, select_fields=None, order_by=None, top=None):
        """
        Base method to get messages with optional filtering

        Args:
            filter_query (str): OData filter string
            select_fields (str): Comma-separated list of fields to select
            order_by (str): Field to order by
            top (int): Number of messages to return
        """
        params = {}

        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        if top:
            params["$top"] = top

        log.debug(f"Getting messages with params: {params}")

        info = self.request("get", "me/messages", params=params)

        if not info or 'value' not in info:
            log.warning(f"{self}: No messages found or invalid response")
            return []

        # Get current user email for direction detection
        current_user_email = self.me.userPrincipalName

        # Convert each message to Email object
        email_objects = []
        for message_data in info['value']:
            try:
                email = Email(**message_data)
                email_objects.append(email)
            except Exception as e:
                log.error(f"{self}: Error creating Email object: {e}")
                continue

        log.info(f"{self}: Converted {len(email_objects)} messages to Email objects")
        return email_objects

    def get_messages_from_sender(self, sender_email):
        """Get messages from a specific sender"""
        filter_query = f"from/emailAddress/address eq '{sender_email}'"
        return self._get_messages(filter_query=filter_query)

    def get_messages_to_recipient(self, recipient_email):
        """Get messages sent to a specific recipient"""
        filter_query = f"toRecipients/any(r: r/emailAddress/address eq '{recipient_email}')"
        return self._get_messages(filter_query=filter_query)

    def get_conversation_with(self, target_email):
        """Get all messages in conversation with a specific email address"""
        filter_query = f"(from/emailAddress/address eq '{target_email}') or (toRecipients/any(r: r/emailAddress/address eq '{target_email}')) or (ccRecipients/any(r: r/emailAddress/address eq '{target_email}'))"
        return self._get_messages(filter_query=filter_query, order_by="sentDateTime desc")

    def get_all_messages_with(self, email_address):
        """Get all messages either sent to or received from a specific email address"""
        # Try getting messages from sender first
        from_messages = self.get_messages_from_sender(email_address)
        # Then get messages to recipient
        to_messages = self.get_messages_to_recipient(email_address)

        # Combine and deduplicate based on message ID
        all_messages = from_messages + to_messages
        seen_ids = set()
        unique_messages = []

        for msg in all_messages:
            if msg.id not in seen_ids:
                seen_ids.add(msg.id)
                unique_messages.append(msg)

        # Sort by sentDateTime descending
        unique_messages.sort(key=lambda msg: msg.sentDateTime, reverse=True)
        return unique_messages

    def get_conversations_with(self, target_email):
        """Get all conversations with a specific email address, grouped by conversationId"""
        messages = self.get_conversation_with(target_email)

        # Group messages by conversationId
        conversations = {}
        for message in messages:
            conv_id = message.conversationId
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append(message)

        # Sort messages within each conversation by sentDateTime
        for conv_id in conversations:
            conversations[conv_id].sort(key=lambda msg: msg.sentDateTime)

        log.info(f"{self}: Found {len(conversations)} conversations with {target_email}")
        return conversations

    def get_latest_conversation_with(self, target_email):
        """Get the most recent conversation with a specific email address"""
        conversations = self.get_conversations_with(target_email)

        if not conversations:
            return []

        # Find the conversation with the most recent message
        latest_conv_id = None
        latest_timestamp = None

        for conv_id, messages in conversations.items():
            # Get the latest message in this conversation
            latest_msg = max(messages, key=lambda msg: msg.sentDateTime)
            if latest_timestamp is None or latest_msg.sentDateTime > latest_timestamp:
                latest_timestamp = latest_msg.sentDateTime
                latest_conv_id = conv_id

        return conversations[latest_conv_id]

    def get_unread_messages(self):
        """Get all unread messages"""
        filter_query = "isRead eq false"
        return self._get_messages(filter_query=filter_query)

    def get_messages_with_attachments(self):
        """Get messages that have attachments"""
        filter_query = "hasAttachments eq true"
        return self._get_messages(filter_query=filter_query)

    def get_messages_by_subject(self, subject_keyword):
        """Get messages containing keyword in subject"""
        filter_query = f"contains(subject, '{subject_keyword}')"
        return self._get_messages(filter_query=filter_query)

    def get_messages_by_importance(self, importance_level="high"):
        """Get messages by importance level (low, normal, high)"""
        filter_query = f"importance eq '{importance_level}'"
        return self._get_messages(filter_query=filter_query)

    def get_recent_messages(self, days=7):
        """Get messages from the last N days"""
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
        filter_query = f"receivedDateTime ge {cutoff_date}"
        return self._get_messages(
            filter_query=filter_query,
            order_by="receivedDateTime desc"
        )

    def search_messages(self, search_term):
        """Search messages by content (requires search endpoint)"""
        # Note: This uses the search endpoint which has different syntax
        search_params = {
            "$search": f'"{search_term}"'
        }

        log.debug(f"Searching messages with term: {search_term}")

        info = self.request("get", "me/messages", params=search_params)

        if not info or 'value' not in info:
            log.warning(f"{self}: No search results found")
            return []

        current_user_email = self.me.userPrincipalName
        email_objects = []

        for message_data in info['value']:
            try:
                email = Email(**message_data)
                email_objects.append(email)
            except Exception as e:
                log.error(f"{self}: Error creating Email object from search: {e}")
                continue

        log.info(f"{self}: Found {len(email_objects)} messages matching search term")
        return email_objects

    def request(self, method, resource, params: dict = None, headers=None, json_body=None):
        url = f"{self.base_url}/{resource}"

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        log.info(f"{self}: Sending {method.upper()} request to: {url}")

        try:
            with httpx.Client() as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=json_body
                )

                if not response.is_success:
                    log.error(f"{self}: Error {response.status_code}: {response.text}")
                    return None

                return response.json()

        except Exception as e:
            log.exception(f"{self}: Request failed: {e}")
            return None
