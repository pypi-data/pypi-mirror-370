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
        return self.message_query()

    def message_query(self, filter_query=None, select_fields=None, order_by=None, top=None):
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
        return self.message_query(filter_query=filter_query)

    def get_messages_to_recipient(self, recipient_email):
        """Get messages sent to a specific recipient"""
        filter_query = f"recipients/any(r: r/emailAddress/address eq '{recipient_email}')"
        return self.message_query(filter_query=filter_query)

    def get_conversation_with(self, target_email):
        """Get all messages in conversation with a specific email address"""
        filter_query = f"(from/emailAddress/address eq '{target_email}') or (recipients/any(r: r/emailAddress/address eq '{target_email}'))"
        return self.message_query(filter_query=filter_query, order_by="sentDateTime desc")

    def get_unread_messages(self):
        """Get all unread messages"""
        filter_query = "isRead eq false"
        return self.message_query(filter_query=filter_query)

    def get_messages_with_attachments(self):
        """Get messages that have attachments"""
        filter_query = "hasAttachments eq true"
        return self.message_query(filter_query=filter_query)

    def get_messages_by_subject(self, subject_keyword):
        """Get messages containing keyword in subject"""
        filter_query = f"contains(subject, '{subject_keyword}')"
        return self.message_query(filter_query=filter_query)

    def get_messages_by_importance(self, importance_level="high"):
        """Get messages by importance level (low, normal, high)"""
        filter_query = f"importance eq '{importance_level}'"
        return self.message_query(filter_query=filter_query)

    def get_recent_messages(self, days=7):
        """Get messages from the last N days"""
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
        filter_query = f"receivedDateTime ge {cutoff_date}"
        return self.message_query(filter_query=filter_query, order_by="receivedDateTime desc")

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
                email = Email.from_graph_response(message_data, current_user_email)
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
