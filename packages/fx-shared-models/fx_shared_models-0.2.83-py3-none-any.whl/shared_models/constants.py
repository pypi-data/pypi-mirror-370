from enum import Enum

class EmailProvider(str, Enum):
    SMTP = 'smtp'
    SENDGRID = 'sendgrid'

class SettingType(str, Enum):
    EMAIL = 'email'
    SECURITY = 'security'
    KYC = 'kyc'
    COMMISSION = 'commission'

class SettingStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'

class ContentType(str, Enum):
    TEXT = 'text'
    HTML = 'html'

class BaseEmailVariables:
    """Base variables available for all system emails"""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ID = "id"
    FULL_NAME = "full_name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    LOCATION = "location"
    CP_URL = "cp_url"
    CRM_URL = "crm_url"
    USER_AGENT = "user_agent"
    IP_ADDRESS = "ip_address"
    TIMESTAMP = "timestamp"
    TYPE = "type"
    PASSWORD = "password"
    ERROR_TYPE = "error_type"
    DATE = "date"
    TIME = "time"
    CHANNEL = "channel"
    PASSWORD_RESET_LINK = "password_reset_link"

    CP_LOGIN_LINK = "cp_login_link"
    CRM_LOGIN_LINK = "crm_login_link"

    # Customer related
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_EMAIL = "customer_email"
    CUSTOMER_PHONE = "customer_phone"
    CUSTOMER_ADDRESS = "customer_address"
    CUSTOMER_CITY = "customer_city"
    CUSTOMER_STATE = "customer_state"
    CUSTOMER_ZIP = "customer_zip"
    CUSTOMER_COUNTRY = "customer_country"
    CUSTOMER_ID = "customer_id"
    CUSTOMER_FIRST_NAME = "customer_first_name"
    CUSTOMER_LAST_NAME = "customer_last_name"
    CUSTOMER_CRM_LINK = "customer_crm_link"
    # User related
    USER_NAME = "user_name"  # Full name of the user
    USER_FULL_NAME = "user_full_name"  # Full name of the user
    USER_EMAIL = "user_email"  # Email address of the user
    USER_FIRST_NAME = "user_first_name"  # First name of the user
    USER_LAST_NAME = "user_last_name"  # Last name of the user
    # Company related
    COMPANY_NAME = "company_name"  # Name of the company
    COMPANY_ADDRESS = "company_address"  # Company address
    COMPANY_PHONE = "company_phone"  # Company phone number
    COMPANY_EMAIL = "company_email"  # Company email address
    COMPANY_WEBSITE = "company_website"  # Company website URL
    APP_NAME = "app_name"  # Name of the application
    APP_URL = "app_url"  # Base URL of the application
    CURRENT_DATE = "current_date"  # Current date
    CURRENT_TIME = "current_time"  # Current time
    SUPPORT_EMAIL = "support_email"  # Support email address
    LOGO_URL = "logo_url"  # URL to company logo

    # Common
    TICKET_ID = "ticket_id"  # Ticket ID
    TICKET_NUMBER = "ticket_number"  # Ticket number
    TICKET_URL = "ticket_url"  # Ticket URL
    TICKET_MESSAGE = "ticket_message"  # Ticket message
    TICKET_SUBJECT = "ticket_subject"  # Ticket subject
    TICKET_DESCRIPTION = "ticket_description"  # Ticket description
    TICKET_STATUS = "ticket_status"  # Ticket status
    TICKET_PRIORITY = "ticket_priority"  # Ticket priority
    TICKER_CATEGORY = "ticket_category"  # Ticket category

    # Referral
    REFERRAL_CODE = "referral_code"  # Referral code
    REFERRAL_LINK = "referral_link"  # Referral link
    REFERRAL_CAMPAIGN = "referral_campaign"  # Referral campaign
    REFERRAL_DASHBOARD_URL = "referral_dashboard_url"  # Referral dashboard URL

    FEEDBACK_LINK = "feedback_link"  # Feedback link
    VERIFICATION_LINK = "verification_link"  # Verification link
    EXPIRY_TIME = "expiry_time"  # Expiry time
    CODE = "code"  # Code
    REASON = "reason"  # Reason
    STATUS = "status"  # Status
    SEVERITY = "severity"  # Severity
    ACTION_REQUIRED = "action_required"  # Action required
    ACTION_URL = "action_url"  # Action URL

    # Specific Contextual URLs (often needed)
    MT5_DOWNLOAD_LINK = "mt5_download_link"
    SECURITY_SETTINGS_URL = "security_settings_url"
    PASSWORD_RESET_URL = "password_reset_url"
    ENTER_CODE_URL = "enter_code_url"
    REFERRAL_DASHBOARD_URL = "referral_dashboard_url"
    REWARD_HISTORY_URL = "reward_history_url"
    SUPPORT_URL = "support_url"
    TICKET_CRM_URL = "ticket_crm_url"
    REQUEST_HISTORY_URL = "request_history_url"
    IB_PORTAL_URL = "ib_portal_url"
    UPLOAD_DOCUMENT_URL = "upload_document_url"
    TRANSACTION_HISTORY_URL = "transaction_history_url"

    @classmethod
    def get_all_variables(cls) -> list:
        """Get all base variables as a list"""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        """Get descriptions for all base variables"""
        return {
            cls.CP_URL: "URL to the CP",
            cls.CRM_URL: "URL to the CRM",
            cls.CRM_LOGIN_LINK: "Login link for the CRM",
            cls.CP_LOGIN_LINK: "Login link for the CP",
            cls.NAME: "Full name of the receiver (customer or user, can be used when both details are not required)",
            cls.EMAIL: "Email address of the receiver (customer or user, can be used when both details are not required)",
            cls.PHONE: "Phone number of the receiver (customer or user, can be used when both details are not required)",
            cls.ID: "ID of the receiver (customer or user, can be used when both details are not required)",
            cls.FIRST_NAME: "First name of the receiver (customer or user, can be used when both details are not required)",
            cls.LAST_NAME: "Last name of the receiver (customer or user, can be used when both details are not required)",
            cls.LOCATION: "Location of the receiver (customer or user, can be used when both details are not required)",
            cls.CUSTOMER_NAME: "Full name of the customer",
            cls.CUSTOMER_ID: "ID of the customer",
            cls.CUSTOMER_EMAIL: "Email address of the customer",
            cls.CUSTOMER_PHONE: "Phone number of the customer",
            cls.CUSTOMER_ADDRESS: "Address of the customer",
            cls.CUSTOMER_CITY: "City of the customer",
            cls.CUSTOMER_STATE: "State of the customer",
            cls.CUSTOMER_ZIP: "Zip code of the customer",
            cls.CUSTOMER_COUNTRY: "Country of the customer",
            cls.CUSTOMER_FIRST_NAME: "First name of the customer",
            cls.CUSTOMER_LAST_NAME: "Last name of the customer",
            cls.USER_NAME: "Full name of the user",
            cls.USER_EMAIL: "Email address of the user",
            cls.USER_FIRST_NAME: "First name of the user",
            cls.USER_LAST_NAME: "Last name of the user",
            cls.COMPANY_NAME: "Name of the company",
            cls.COMPANY_ADDRESS: "Company address",
            cls.COMPANY_PHONE: "Company phone number",
            cls.COMPANY_EMAIL: "Company email address",
            cls.COMPANY_WEBSITE: "Company website URL",
            cls.APP_NAME: "Name of the application",
            cls.APP_URL: "Base URL of the application",
            cls.CURRENT_DATE: "Current date",
            cls.CURRENT_TIME: "Current time",
            cls.SUPPORT_EMAIL: "Support email address",
            cls.LOGO_URL: "URL to company logo",
            cls.TICKET_NUMBER: "Ticket number",
            cls.TICKET_URL: "Ticket URL",
            cls.FEEDBACK_LINK: "Feedback link",
            cls.VERIFICATION_LINK: "Verification link",
            cls.EXPIRY_TIME: "Expiry time",
            cls.CODE: "Code",
            cls.REASON: "Reason",
            cls.STATUS: "Status",
            cls.SEVERITY: "Severity level of the alert",
            cls.ACTION_REQUIRED: "Required action to be taken",
            cls.ACTION_URL: "Generic Action URL",
            cls.MT5_DOWNLOAD_LINK: "Link to download the MT5 platform",
            cls.SECURITY_SETTINGS_URL: "Link to user's security settings page",
            cls.PASSWORD_RESET_URL: "Link to the password reset page",
            cls.ENTER_CODE_URL: "Link to the page where verification code is entered",
            cls.REFERRAL_DASHBOARD_URL: "Link to the referrer's dashboard/tracking page",
            cls.REWARD_HISTORY_URL: "Link to the reward/payment history page",
            cls.SUPPORT_URL: "Link to the main support/contact page",
            cls.TICKET_CRM_URL: "Link for CRM users to view a specific ticket",
            cls.REQUEST_HISTORY_URL: "Link to the user's request history page",
            cls.IB_PORTAL_URL: "Link to the IB portal section",
            cls.UPLOAD_DOCUMENT_URL: "Link to the document upload page",
            cls.TRANSACTION_HISTORY_URL: "Link to the transaction history page",
            cls.TICKET_ID: "ID of the ticket",
            cls.TICKER_CATEGORY: "Category of the ticket",
            cls.TICKET_PRIORITY: "Priority of the ticket",
            cls.TICKET_STATUS: "Status of the ticket",
            cls.TICKET_SUBJECT: "Subject of the ticket",
            cls.TICKET_DESCRIPTION: "Description of the ticket",
            cls.TICKET_MESSAGE: "Message of the ticket",
            cls.REFERRAL_CODE: "Referral code of the referrer",
            cls.REFERRAL_LINK: "Link to the referrer's dashboard/tracking page",
            cls.REFERRAL_CAMPAIGN: "Campaign of the referrer",
            cls.REFERRAL_DASHBOARD_URL: "Link to the referrer's dashboard/tracking page",

        } 

class SystemEmailTrigger:
    """System email trigger events and their descriptions"""
    
    # Authentication related
    LOGIN_NOTIFICATION = "login_notification"
    LOGIN_FAILED_NOTIFICATION = "login_failed_notification"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    EMAIL_VERIFICATION = "email_verification"
    EMAIL_VERIFICATION_FAILED = "email_verification_failed"
    EMAIL_VERIFICATION_SUCCESS = "email_verification_success"
    TWO_FACTOR_CODE = "two_factor_code"
    ACCESS_CHANGED = "access_changed"
    TWO_FACTOR_STATUS_CHANGED = "two_factor_status_changed"
    SECURITY_KEY_STATUS_CHANGED = "security_key_status_changed"
    
    # Customer related
    CUSTOMER_WELCOME_LIVE_EMAIL = "customer_welcome_live_email"
    CUSTOMER_WELCOME_DEMO_EMAIL = "customer_welcome_demo_email"
    CUSTOMER_WELCOME_IB_EMAIL = "customer_welcome_ib_email"
    CUSTOMER_AGENT_ASSIGNED = "customer_agent_assigned"
    CUSTOMER_AGENT_UNASSIGNED = "customer_agent_unassigned"
    CUSTOMER_FEEDBACK = "customer_feedback"
    CUSTOMER_SUPPORT = "customer_support"

    # User related
    USER_WELCOME_EMAIL = "user_welcome_email"
    USER_CUSTOMER_ASSIGNED = "user_customer_assigned"
    USER_CUSTOMER_UNASSIGNED = "user_customer_unassigned"
    USER_CUSTOMER_ADDED = "user_customer_added"

    # System related
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_NOTIFICATION = "maintenance_notification"
    SECURITY_ALERT = "security_alert"

    # Accounts related 
    ACCOUNT_UPDATED = "account_updated"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_LINKED = "account_linked"
    ACCOUNT_STATUS_CHANGED = "account_status_changed"
    ACCOUNT_TRADING_STATUS_CHANGED = "account_trading_status_changed"
    ACCOUNT_PASSWORD_CHANGED = "account_password_changed"
    ACCOUNT_RESET_PASSWORD = "account_reset_password"
    ACCOUNT_LEVERAGE_CHANGED = "account_leverage_changed"
    ACCOUNT_GROUP_CHANGED = "account_group_changed"
    ACCOUNT_ARCHIVED = "account_archived"
    ACCOUNT_RESTORED = "account_restored"

    # Documents Related
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_STATUS_CHANGED = "document_status_changed"
    DOCUMENT_VERIFICATION_REQUIRED = "document_verification_required"

    # KYC Related
    KYC_SUBMITTED = "kyc_submitted"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    KYC_RESUBMITTED = "kyc_resubmitted"
    KYC_ADDITIONAL_VERIFICATION_REQUIRED = "kyc_additional_verification_required"

    # Transactions Related
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_STATUS_CHANGED = "transaction_status_changed"
    TRANSACTION_FAILED = "transaction_failed"
    TRANSACTION_APPROVED = "transaction_approved"
    TRANSACTION_SUCCESS = "transaction_success"
    TRANSACTION_REJECTED = "transaction_rejected"
    TRANSACTION_EVIDENCE_REQUIRED = "transaction_evidence_required"
    TRANSACTION_EVIDENCE_UPLOADED = "transaction_evidence_uploaded"
    TRANSACTION_EVIDENCE_VERIFIED = "transaction_evidence_verified"
    TRANSACTION_EVIDENCE_REJECTED = "transaction_evidence_rejected"

    # Referral Related
    REFERRAL_CREATED = "referral_created"
    REFERRAL_AQUISITION = "referral_acquisition"
    REFERRAL_EVENT = "referral_event"
    REFERRAL_REWARD_EARNED = "referral_reward_earned"
    REFERRAL_REWARD_PAYMENT_FAILED = "referral_reward_payment_failed"
    REFERRAL_REWARD_PAYMENT_SUCCESS = "referral_reward_payment_success"

    # Ticket Related
    TICKET_CREATED = "ticket_created"
    TICKET_STATUS_CHANGED = "ticket_status_changed"
    TICKET_PRIORITY_CHANGED = "ticket_priority_changed"
    TICKET_ASSIGNED = "ticket_assigned"
    TICKET_NEW_MESSAGE = "ticket_new_message"
    TICKET_CLOSED = "ticket_closed"

    # Requests Related
    REQUEST_CREATED = "request_created"
    REQUEST_STATUS_CHANGED = "request_status_changed"
    ACCOUNT_REQUEST_APPROVED = "account_request_approved"
    LEVERAGE_REQUEST_APPROVED = "leverage_request_approved"
    IB_REQUEST_APPROVED = "ib_request_approved"
    REQUEST_REJECTED = "request_rejected"

    REFERRAL_LINK = "referral_link"
    REFERRAL_CURRENCY = "referral_currency"

    @classmethod
    def get_all_triggers(cls) -> list:
        """Get all trigger events as a list"""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_trigger_descriptions(cls) -> dict:
        """Get descriptions for all trigger events"""
        return {
            cls.LOGIN_NOTIFICATION: "Sent when a user/customer logs in",
            cls.LOGIN_FAILED_NOTIFICATION: "Sent when a user's/customer's login attempt fails",
            cls.PASSWORD_CHANGED: "Sent when a user/customer changes their password",
            cls.PASSWORD_RESET: "Sent when a user/customer requests a password reset",
            cls.PASSWORD_RESET_REQUEST: "Sent when a user/customer requests a password reset",
            cls.EMAIL_VERIFICATION: "Sent to verify a user's/customer's email address",
            cls.EMAIL_VERIFICATION_FAILED: "Sent when a user's/customer's email verification fails",
            cls.EMAIL_VERIFICATION_SUCCESS: "Sent when a user's/customer's email verification succeeds",
            cls.TWO_FACTOR_CODE: "Sent with two-factor authentication code",
            cls.ACCESS_CHANGED: "Sent when a user's/customer's access level is changed",
            cls.TWO_FACTOR_STATUS_CHANGED: "Sent when two-factor authentication status is changed",
            cls.SECURITY_KEY_STATUS_CHANGED: "Sent when security key status is changed",
            
            cls.CUSTOMER_WELCOME_LIVE_EMAIL: "Sent when a customer registers via /live or added as a client in the crm",
            cls.CUSTOMER_WELCOME_DEMO_EMAIL: "Sent when a customer registers via /demo or added as a lead in the crm",
            cls.CUSTOMER_WELCOME_IB_EMAIL: "Sent when a customer registers via /ib or added as a ib in the crm",
            cls.CUSTOMER_AGENT_ASSIGNED: "Sent when a customer is assigned to an agent",
            cls.CUSTOMER_AGENT_UNASSIGNED: "Sent when a customer is unassigned from an agent",
            cls.CUSTOMER_FEEDBACK: "Sent to request customer feedback",
            cls.CUSTOMER_SUPPORT: "Sent in response to customer support requests",
            cls.USER_WELCOME_EMAIL: "Sent when a new user registers/added to the system",
            cls.USER_CUSTOMER_ASSIGNED: "Sent when a user is assigned to a customer",
            cls.USER_CUSTOMER_UNASSIGNED: "Sent when a user is unassigned from a customer",
            cls.USER_CUSTOMER_ADDED: "Sent when a user is assigned to a customer",
            
            cls.ACCOUNT_UPDATED: "Sent when account details are updated",
            cls.ACCOUNT_CREATED: "Sent when a new account is created",
            cls.ACCOUNT_LINKED: "Sent when a new account is linked to a customer",
            cls.ACCOUNT_STATUS_CHANGED: "Sent when an account status is changed",
            cls.ACCOUNT_TRADING_STATUS_CHANGED: "Sent when an account trading status is changed",
            cls.ACCOUNT_PASSWORD_CHANGED: "Sent when an account password is changed",
            cls.ACCOUNT_RESET_PASSWORD: "Sent when an account password is reset",
            cls.ACCOUNT_LEVERAGE_CHANGED: "Sent when an account leverage is changed",
            cls.ACCOUNT_GROUP_CHANGED: "Sent when an account group is changed",
            cls.ACCOUNT_ARCHIVED: "Sent when an account is archived",
            cls.ACCOUNT_RESTORED: "Sent when an account is restored",

            cls.DOCUMENT_UPLOADED: "Sent when a document is uploaded",
            cls.DOCUMENT_STATUS_CHANGED: "Sent when a document status is changed",
            cls.DOCUMENT_VERIFICATION_REQUIRED: "Sent when a document verification is required",

            cls.KYC_SUBMITTED: "Sent when a kyc is submitted",
            cls.KYC_APPROVED: "Sent when a kyc is approved",
            cls.KYC_REJECTED: "Sent when a kyc is rejected",
            cls.KYC_RESUBMITTED: "Sent when a kyc is resubmitted",

            cls.TRANSACTION_CREATED: "Sent when a transaction is created",
            cls.TRANSACTION_STATUS_CHANGED: "Sent when a transaction status is changed",
            cls.TRANSACTION_FAILED: "Sent when a transaction fails",
            cls.TRANSACTION_SUCCESS: "Sent when a transaction is successful",
            cls.TRANSACTION_REJECTED: "Sent when a transaction is rejected",
            cls.TRANSACTION_EVIDENCE_REQUIRED: "Sent when a transaction evidence is required",
            cls.TRANSACTION_EVIDENCE_UPLOADED: "Sent when a transaction evidence is uploaded",
            cls.TRANSACTION_EVIDENCE_VERIFIED: "Sent when a transaction evidence is verified",
            cls.TRANSACTION_EVIDENCE_REJECTED: "Sent when a transaction evidence is rejected",

            cls.REFERRAL_CREATED: "Sent when a referral is created",
            cls.REFERRAL_AQUISITION: "Sent when a referral is acquired",
            cls.REFERRAL_EVENT: "Sent when a referral event occurs",
            cls.REFERRAL_REWARD_EARNED: "Sent when a referral reward is earned",
            cls.REFERRAL_REWARD_PAYMENT_FAILED: "Sent when a referral reward payment fails",
            cls.REFERRAL_REWARD_PAYMENT_SUCCESS: "Sent when a referral reward payment is successful",

            cls.TICKET_CREATED: "Sent when a ticket is created",
            cls.TICKET_STATUS_CHANGED: "Sent when a ticket status is changed",
            cls.TICKET_PRIORITY_CHANGED: "Sent when a ticket priority is changed",
            cls.TICKET_ASSIGNED: "Sent when a ticket is assigned to an agent",
            cls.TICKET_NEW_MESSAGE: "Sent when a new message is added to a ticket",
            cls.TICKET_CLOSED: "Sent when a ticket is closed",

            cls.REQUEST_CREATED: "Sent when a request is created",
            cls.REQUEST_STATUS_CHANGED: "Sent when a request status is changed",
            cls.ACCOUNT_REQUEST_APPROVED: "Sent when an account request is approved",
            cls.LEVERAGE_REQUEST_APPROVED: "Sent when a leverage request is approved",
            cls.IB_REQUEST_APPROVED: "Sent when an ib request is approved",
            cls.REQUEST_REJECTED: "Sent when a request is rejected",

            cls.SYSTEM_ALERT: "Sent for important system alerts",
            cls.MAINTENANCE_NOTIFICATION: "Sent for scheduled maintenance notifications",
            cls.SECURITY_ALERT: "Sent for security-related alerts"
        }

    @classmethod
    def get_trigger_variables(cls) -> dict:
        """Get required variables for each trigger event"""
        return {
            cls.LOGIN_NOTIFICATION: ["name", "ip", "location"],
            cls.LOGIN_FAILED_NOTIFICATION: ["name", "ip", "location"],
            cls.PASSWORD_RESET: ["name", "password"],
            cls.PASSWORD_RESET_REQUEST: ["name", "verification_link", "expiry_time"],
            cls.PASSWORD_CHANGED: ["name"],
            cls.EMAIL_VERIFICATION: ["name", "code", "expiry_time"],
            cls.EMAIL_VERIFICATION_FAILED: ["name", "code", "expiry_time"],
            cls.EMAIL_VERIFICATION_SUCCESS: ["name", "code", "expiry_time"],
            cls.TWO_FACTOR_CODE: ["name", "code", "expiry_time"],
            cls.ACCESS_CHANGED: ["name", "reason", "support_contact", "status"],
            cls.TWO_FACTOR_STATUS_CHANGED: ["name", "status"],
            cls.SECURITY_KEY_STATUS_CHANGED: ["name", "status"],
            
            cls.CUSTOMER_WELCOME_LIVE_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_WELCOME_DEMO_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_WELCOME_IB_EMAIL: ["name", "cp_login_link"],
            cls.CUSTOMER_AGENT_ASSIGNED: ["customer_name", "user_name", "cp_login_link"],
            cls.CUSTOMER_AGENT_UNASSIGNED: ["customer_name", "user_name", "cp_login_link"],
            cls.CUSTOMER_FEEDBACK: ["user_name", "feedback_link"],
            cls.CUSTOMER_SUPPORT: ["ticket_number", "support_message"],

            cls.ACCOUNT_UPDATED: ["user_name", "updated_fields"],
            cls.ACCOUNT_CREATED: ["user_name", "account_number", "account_type", "server", "group_name", "leverage"],
            cls.ACCOUNT_LINKED: ["user_name", "account_number", "account_type", "server", "group_name", "leverage"],

            cls.DOCUMENT_UPLOADED: ["user_name", "document_name", "document_type", "document_status"],
            cls.DOCUMENT_STATUS_CHANGED: ["user_name", "document_name", "document_type", "document_status"],
            cls.DOCUMENT_VERIFICATION_REQUIRED: ["user_name", "document_name", "document_type", "document_status"],

            cls.KYC_SUBMITTED: ["user_name", "kyc_type", "kyc_status"],
            cls.KYC_APPROVED: ["user_name", "kyc_type", "kyc_status"],
            cls.KYC_REJECTED: ["user_name", "kyc_type", "kyc_status"],
            cls.KYC_RESUBMITTED: ["user_name", "kyc_type", "kyc_status"],

            cls.TRANSACTION_CREATED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_STATUS_CHANGED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_FAILED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_SUCCESS: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_REJECTED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_EVIDENCE_REQUIRED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_EVIDENCE_UPLOADED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_EVIDENCE_VERIFIED: ["user_name", "transaction_type", "transaction_status"],
            cls.TRANSACTION_EVIDENCE_REJECTED: ["user_name", "transaction_type", "transaction_status"],

            cls.REFERRAL_CREATED: ["user_name", "referral_type", "referral_status"],
            cls.REFERRAL_AQUISITION: ["user_name", "referral_type", "referral_status"],
            cls.REFERRAL_EVENT: ["user_name", "referral_type", "referral_status"],
            cls.REFERRAL_REWARD_EARNED: ["user_name", "referral_type", "referral_status"],
            cls.REFERRAL_REWARD_PAYMENT_FAILED: ["user_name", "referral_type", "referral_status"],
            cls.REFERRAL_REWARD_PAYMENT_SUCCESS: ["user_name", "referral_type", "referral_status"],

            cls.TICKET_CREATED: ["user_name", "ticket_type", "ticket_status"],
            cls.TICKET_STATUS_CHANGED: ["user_name", "ticket_type", "ticket_status"],
            cls.TICKET_PRIORITY_CHANGED: ["user_name", "ticket_type", "ticket_status"],
            cls.TICKET_ASSIGNED: ["user_name", "ticket_type", "ticket_status"],
            cls.TICKET_NEW_MESSAGE: ["user_name", "ticket_type", "ticket_status"],
            cls.TICKET_CLOSED: ["user_name", "ticket_type", "ticket_status"],

            cls.REQUEST_CREATED: ["user_name", "request_type", "request_status"],
            cls.REQUEST_STATUS_CHANGED: ["user_name", "request_type", "request_status"],
            cls.ACCOUNT_REQUEST_APPROVED: ["user_name", "request_type", "request_status"],
            cls.LEVERAGE_REQUEST_APPROVED: ["user_name", "request_type", "request_status"],
            cls.IB_REQUEST_APPROVED: ["user_name", "request_type", "request_status"],
            cls.REQUEST_REJECTED: ["user_name", "request_type", "request_status"],

            cls.USER_WELCOME_EMAIL: ["name", "crm_login_link"],
            cls.USER_CUSTOMER_ASSIGNED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            cls.USER_CUSTOMER_UNASSIGNED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            cls.USER_CUSTOMER_ADDED: ["customer_name", "user_name", "crm_login_link", "customer_crm_link"],
            
            cls.SYSTEM_ALERT: ["alert_message", "severity", "action_required"],
            cls.MAINTENANCE_NOTIFICATION: ["start_time", "end_time", "affected_services"],
            cls.SECURITY_ALERT: ["alert_type", "alert_message", "recommended_action"]
        }

# Variable classes for different types of emails
class AuthenticationEmailVariables:
    """Variables specific to authentication-related emails"""
    IP_ADDRESS = "ip_address"
    BROWSER = "browser"
    DEVICE = "device"
    LOCATION = "location"
    VERIFICATION_CODE = "verification_code"
    VERIFICATION_LINK = "verification_link"
    EXPIRY_TIME = "expiry_time"
    ACCESS_LEVEL = "access_level"
    PREVIOUS_ACCESS = "previous_access"
    NEW_ACCESS = "new_access"
    SECURITY_STATUS = "security_status"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.IP_ADDRESS: "IP address of the login attempt",
            cls.BROWSER: "Browser used for the login attempt",
            cls.DEVICE: "Device used for the login attempt",
            cls.LOCATION: "Location of the login attempt",
            cls.VERIFICATION_CODE: "Code for email verification or 2FA",
            cls.VERIFICATION_LINK: "Link for email verification or password reset",
            cls.EXPIRY_TIME: "Expiry time for verification code/link",
            cls.ACCESS_LEVEL: "User's access level",
            cls.PREVIOUS_ACCESS: "Previous access level",
            cls.NEW_ACCESS: "New access level",
            cls.SECURITY_STATUS: "Status of security feature"
        }

class CustomerEmailVariables:
    """Variables specific to customer-related emails"""
    ACCOUNT_TYPE = "account_type"
    ACCOUNT_NUMBER = "account_number"
    ACCOUNT_STATUS = "account_status"
    ASSIGNED_AGENT = "assigned_agent"
    PREVIOUS_AGENT = "previous_agent"
    FEEDBACK_LINK = "feedback_link"
    TICKET_NUMBER = "ticket_number"
    TICKET_STATUS = "ticket_status"
    TICKET_PRIORITY = "ticket_priority"
    SUPPORT_MESSAGE = "support_message"
    UPDATED_FIELDS = "updated_fields"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.ACCOUNT_TYPE: "Type of customer account (live/demo/ib)",
            cls.ACCOUNT_NUMBER: "Customer's account number",
            cls.ACCOUNT_STATUS: "Status of customer's account",
            cls.ASSIGNED_AGENT: "Name of assigned agent",
            cls.PREVIOUS_AGENT: "Name of previously assigned agent",
            cls.FEEDBACK_LINK: "Link to provide feedback",
            cls.TICKET_NUMBER: "Support ticket number",
            cls.TICKET_STATUS: "Status of support ticket",
            cls.TICKET_PRIORITY: "Priority of support ticket",
            cls.SUPPORT_MESSAGE: "Support message or response",
            cls.UPDATED_FIELDS: "List of updated account fields"
        }
    

class AccountEmailVariables:
    """Variables specific to account-related emails"""
    LOGIN = "login"
    MASTER_PASSWORD = "master_password"
    INVESTOR_PASSWORD = "investor_password"
    ACCOUNT_TYPE = "account_type"
    SERVER = "server"
    GROUP_NAME = "group_name"
    GROUP = "group"
    LEVERAGE = "leverage"
    STATUS = "status"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.LOGIN: "Login ID of the account",
            cls.MASTER_PASSWORD: "Master password of the account",
            cls.INVESTOR_PASSWORD: "Investor password of the account",
            cls.ACCOUNT_TYPE: "Type of account (live/demo/ib)",
            cls.SERVER: "Server of the account",
            cls.GROUP_NAME: "Group name of the account",
            cls.GROUP: "Group of the account",
            cls.LEVERAGE: "Leverage of the account",
            cls.STATUS: "Status of the account"
        }
    
class DocumentEmailVariables:
    """Variables specific to document-related emails"""
    DOCUMENT_NAME = "document_name"
    DOCUMENT_TYPE = "document_type"
    DOCUMENT_STATUS = "document_status"
    DOCUMENT_MESSAGE = "document_message"
    
    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.DOCUMENT_NAME: "Name of the document",
            cls.DOCUMENT_TYPE: "Type of the document",
            cls.DOCUMENT_STATUS: "Status of the document",
            cls.DOCUMENT_MESSAGE: "Message of the document"
        }
    

class KYCEmailVariables:
    """Variables specific to KYC-related emails"""
    KYC_TYPE = "kyc_type"
    KYC_STATUS = "kyc_status"
    KYC_MESSAGE = "kyc_message"
    KYC_DOCUMENT_TYPE = "kyc_document_type"
    
    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.KYC_TYPE: "Type of KYC",
            cls.KYC_STATUS: "Status of KYC",
            cls.KYC_MESSAGE: "Message of KYC",
            cls.KYC_DOCUMENT_TYPE: "Type of KYC document"
        }
    
class TransactionEmailVariables:
    """Variables specific to transaction-related emails"""
    TRANSACTION_TYPE = "transaction_type"
    TRANSACTION_STATUS = "transaction_status"
    TRANSACTION_MESSAGE = "transaction_message"
    TRANSACTION_DIRECTION = "transaction_direction"
    TRANSACTION_MT5_TICKET = "transaction_mt5_ticket"
    TRANSACTION_ACCOUNT_NUMBER = "transaction_account_number"
    TRANSACTION_ID = "transaction_id"
    TRANSACTION_AMOUNT = "transaction_amount"
    TRANSACTION_CURRENCY = "transaction_currency"
    TRANSACTION_DATE = "transaction_date"
    TRANSACTION_TIME = "transaction_time"
    TRANSACTION_FEE = "transaction_fee"
    TRANSACTION_PAYMENT_METHOD = "transaction_payment_method"
    TRANSACTION_PAYMENT_GATEWAY = "transaction_payment_gateway"
    TRANSACTION_PAYMENT_GATEWAY_ID = "transaction_payment_gateway_id"
    TRANSACTION_PAYMENT_GATEWAY_STATUS = "transaction_payment_gateway_status"
    TRANSACTION_PAYMENT_GATEWAY_MESSAGE = "transaction_payment_gateway_message"
    TRANSACTION_PAYMENT_GATEWAY_ERROR = "transaction_payment_gateway_error"
    TRANSACTION_PAYMENT_GATEWAY_ERROR_MESSAGE = "transaction_payment_gateway_error_message"
    TRANSACTION_PAYMENT_GATEWAY_ERROR_CODE = "transaction_payment_gateway_error_code"
    TRANSACTION_PAYMENT_GATEWAY_ERROR_DETAILS = "transaction_payment_gateway_error_details"
    TRANSACTION_REJECT_REASON = "transaction_reject_reason"
    
    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.TRANSACTION_TYPE: "Type of transaction",
            cls.TRANSACTION_STATUS: "Status of transaction",
            cls.TRANSACTION_MESSAGE: "Message of transaction",
            cls.TRANSACTION_ID: "ID of transaction",
            cls.TRANSACTION_AMOUNT: "Amount of transaction",
            cls.TRANSACTION_CURRENCY: "Currency of transaction",
            cls.TRANSACTION_DATE: "Date of transaction",
            cls.TRANSACTION_TIME: "Time of transaction",
            cls.TRANSACTION_FEE: "Fee of transaction",
            cls.TRANSACTION_DIRECTION: "Direction of transaction",
            cls.TRANSACTION_MT5_TICKET: "MT5 ticket of transaction",
            cls.TRANSACTION_ACCOUNT_NUMBER: "Account number of transaction",
            cls.TRANSACTION_PAYMENT_METHOD: "Payment method of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY: "Payment gateway of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_ID: "Payment gateway ID of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_STATUS: "Payment gateway status of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_MESSAGE: "Payment gateway message of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_ERROR: "Payment gateway error of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_ERROR_MESSAGE: "Payment gateway error message of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_ERROR_CODE: "Payment gateway error code of transaction",
            cls.TRANSACTION_PAYMENT_GATEWAY_ERROR_DETAILS: "Payment gateway error details of transaction"
        }
    
    
class ReferralEmailVariables:
    """Variables specific to referral-related emails"""
    REFERRAL_TYPE = "referral_type"
    REFERRAL_STATUS = "referral_status"
    REFERRAL_CODE = "referral_code"
    REFERRAL_EVENT = "referral_event"
    REFERRAL_MESSAGE = "referral_message"
    REFERRAL_ID = "referral_id"
    REFERRAL_AMOUNT = "referral_amount"
    REFERRAL_CAMPAIGN = "referral_campaign"
    REFERRAL_SOURCE = "referral_source"
    REFERRAL_PAYMENT_METHOD = "referral_payment_method"
    REFERRAL_PAYMENT_GATEWAY = "referral_payment_gateway"
    REFERRAL_CUSTOMER_NAME = "referral_customer_name"
    REFERRAL_CUSTOMER_EMAIL = "referral_customer_email"
    REFERRAL_CUSTOMER_PHONE = "referral_customer_phone"
    REFERRAL_CUSTOMER_COUNTRY = "referral_customer_country"

    REFERRAL_LINK = "referral_link"
    REFERRAL_CURRENCY = "referral_currency"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.REFERRAL_TYPE: "Type of referral",
            cls.REFERRAL_STATUS: "Status of referral",
            cls.REFERRAL_CODE: "Code of referral",
            cls.REFERRAL_EVENT: "Event of referral",
            cls.REFERRAL_MESSAGE: "Message of referral",
            cls.REFERRAL_ID: "ID of referral",
            cls.REFERRAL_AMOUNT: "Amount of referral",
            cls.REFERRAL_CAMPAIGN: "Campaign of referral",
            cls.REFERRAL_SOURCE: "Source of referral",
            cls.REFERRAL_PAYMENT_METHOD: "Payment method of referral",
            cls.REFERRAL_PAYMENT_GATEWAY: "Payment gateway of referral",
            cls.REFERRAL_CUSTOMER_NAME: "Name of referral customer",
            cls.REFERRAL_CUSTOMER_EMAIL: "Email of referral customer",
            cls.REFERRAL_CUSTOMER_PHONE: "Phone of referral customer",
            cls.REFERRAL_CUSTOMER_COUNTRY: "Country of referral customer",
            cls.REFERRAL_LINK: "The unique referral link to share",
            cls.REFERRAL_CURRENCY: "The currency of the referral reward amount",
        }
        

class TicketEmailVariables:
    """Variables specific to ticket-related emails"""
    TICKET_TYPE = "ticket_type"
    TICKET_STATUS = "ticket_status"
    TICKET_MESSAGE = "ticket_message"
    TICKET_ID = "ticket_id"
    TICKET_SUBJECT = "ticket_subject"
    TICKET_CATEGORY = "ticket_category"
    TICKET_PRIORITY = "ticket_priority"
    TICKET_ASSIGNEE = "ticket_assignee"
    TICKET_MESSAGE = "ticket_message"
    TICKET_CREATED_AT = "ticket_created_at"
    TICKET_UPDATED_AT = "ticket_updated_at"
    TICKET_CLOSED_AT = "ticket_closed_at"
    TICKET_RESOLVED_AT = "ticket_resolved_at"
    TICKET_RESOLVED_BY = "ticket_resolved_by"
    TICKET_RESOLVED_MESSAGE = "ticket_resolved_message"
    

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.TICKET_TYPE: "Type of ticket",
            cls.TICKET_STATUS: "Status of ticket",
            cls.TICKET_MESSAGE: "Message of ticket",
            cls.TICKET_ID: "ID of ticket",
            cls.TICKET_SUBJECT: "Subject of ticket",
            cls.TICKET_CATEGORY: "Category of ticket",
            cls.TICKET_PRIORITY: "Priority of ticket",
            cls.TICKET_ASSIGNEE: "Assignee of ticket",
            cls.TICKET_CREATED_AT: "Created at of ticket",
            cls.TICKET_UPDATED_AT: "Updated at of ticket",
            cls.TICKET_CLOSED_AT: "Closed at of ticket",
            cls.TICKET_RESOLVED_AT: "Resolved at of ticket",
            cls.TICKET_RESOLVED_BY: "Resolved by of ticket",
            cls.TICKET_RESOLVED_MESSAGE: "Resolved message of ticket"
        }
    
class RequestEmailVariables:
    """Variables specific to request-related emails"""
    REQUEST_TYPE = "request_type"
    REQUEST_STATUS = "request_status"
    REQUEST_MESSAGE = "request_message"
    REQUEST_ID = "request_id"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.REQUEST_TYPE: "Type of request",
            cls.REQUEST_STATUS: "Status of request",
            cls.REQUEST_MESSAGE: "Message of request",
            cls.REQUEST_ID: "ID of request"
        }

class SystemEmailVariables:
    """Variables specific to system-related emails"""
    ALERT_TYPE = "alert_type"
    ALERT_MESSAGE = "alert_message"
    SEVERITY = "severity"
    ACTION_REQUIRED = "action_required"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    AFFECTED_SERVICES = "affected_services"
    SYSTEM_STATUS = "system_status"
    ERROR_DETAILS = "error_details"
    RESOLUTION_STEPS = "resolution_steps"

    @classmethod
    def get_all_variables(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

    @classmethod
    def get_variable_descriptions(cls) -> dict:
        return {
            cls.ALERT_TYPE: "Type of system alert",
            cls.ALERT_MESSAGE: "Alert message details",
            cls.SEVERITY: "Severity level of the alert",
            cls.ACTION_REQUIRED: "Required action to be taken",
            cls.MAINTENANCE_START: "Start time of maintenance",
            cls.MAINTENANCE_END: "End time of maintenance",
            cls.AFFECTED_SERVICES: "Services affected by maintenance/issue",
            cls.SYSTEM_STATUS: "Current system status",
            cls.ERROR_DETAILS: "Detailed error information",
            cls.RESOLUTION_STEPS: "Steps to resolve the issue"
        }

class TriggerVariableMapping:
    """Maps trigger events to their specific variable classes"""
    MAPPINGS = {
        # Authentication triggers
        "login_notification": AuthenticationEmailVariables,
        "login_failed_notification": AuthenticationEmailVariables,
        "password_reset": AuthenticationEmailVariables,
        "password_reset_request": AuthenticationEmailVariables,
        "email_verification": AuthenticationEmailVariables,
        "two_factor_code": AuthenticationEmailVariables,
        "access_changed": AuthenticationEmailVariables,
        "two_factor_status_changed": AuthenticationEmailVariables,
        "security_key_status_changed": AuthenticationEmailVariables,
        
        # Customer triggers
        "customer_welcome_live_email": CustomerEmailVariables,
        "customer_welcome_demo_email": CustomerEmailVariables,
        "customer_welcome_ib_email": CustomerEmailVariables,
        "customer_agent_assigned": CustomerEmailVariables,
        "customer_agent_unassigned": CustomerEmailVariables,
        "customer_feedback": CustomerEmailVariables,
        "customer_support": CustomerEmailVariables,

        "account_updated": AccountEmailVariables,
        "account_created": AccountEmailVariables,
        "account_linked": AccountEmailVariables,
        "account_status_changed": AccountEmailVariables,
        "account_trading_status_changed": AccountEmailVariables,
        "account_password_changed": AccountEmailVariables,
        "account_reset_password": AccountEmailVariables,
        "account_leverage_changed": AccountEmailVariables,
        "account_group_changed": AccountEmailVariables,
        "account_archived": AccountEmailVariables,
        "account_restored": AccountEmailVariables,

        "document_uploaded": DocumentEmailVariables,
        "document_status_changed": DocumentEmailVariables,
        "document_verification_required": DocumentEmailVariables,

        "kyc_submitted": KYCEmailVariables,
        "kyc_approved": KYCEmailVariables,
        "kyc_rejected": KYCEmailVariables,
        "kyc_resubmitted": KYCEmailVariables,

        "transaction_created": TransactionEmailVariables,
        "transaction_status_changed": TransactionEmailVariables,
        "transaction_failed": TransactionEmailVariables,
        "transaction_success": TransactionEmailVariables,
        "transaction_rejected": TransactionEmailVariables,
        "transaction_evidence_required": TransactionEmailVariables,
        "transaction_evidence_uploaded": TransactionEmailVariables,
        "transaction_evidence_verified": TransactionEmailVariables,
        "transaction_evidence_rejected": TransactionEmailVariables,
        
        "referral_created": ReferralEmailVariables,
        "referral_acquisition": ReferralEmailVariables,
        "referral_event": ReferralEmailVariables,
        "referral_reward_earned": ReferralEmailVariables,
        "referral_reward_payment_failed": ReferralEmailVariables,
        "referral_reward_payment_success": ReferralEmailVariables,

        "ticket_created": TicketEmailVariables,
        "ticket_status_changed": TicketEmailVariables,
        "ticket_priority_changed": TicketEmailVariables,
        "ticket_assigned": TicketEmailVariables,
        "ticket_new_message": TicketEmailVariables,
        "ticket_closed": TicketEmailVariables,
        
        # System triggers
        "system_alert": SystemEmailVariables,
        "maintenance_notification": SystemEmailVariables,
        "security_alert": SystemEmailVariables
    }

    @classmethod
    def get_variables_for_trigger(cls, trigger_event: str) -> tuple:
        """Get all available variables for a trigger event"""
        # Always include base variables
        variables = BaseEmailVariables.get_all_variables()
        descriptions = BaseEmailVariables.get_variable_descriptions()
        
        # Add trigger-specific variables
        if trigger_event in cls.MAPPINGS:
            variable_class = cls.MAPPINGS[trigger_event]
            variables.extend(variable_class.get_all_variables())
            descriptions.update(variable_class.get_variable_descriptions())
        
        return variables, descriptions 
    
class AccountType(str, Enum):
    LIVE = 'LIVE'
    DEMO = 'DEMO'
    IB = 'IB'

    @classmethod
    def get_all_types(cls) -> list:
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]

# --- Flattened AllSystemVariables (Shared Models Version) ---
class AllSystemVariables:
    """Flat access to all system email variables defined in shared_models, prioritizing specific over base."""
    _all_vars = {}

    # Order matters: Start with base, then overwrite with specifics
    _variable_classes = [
        BaseEmailVariables, # Uses BaseEmailVariables from this file
        AuthenticationEmailVariables,
        CustomerEmailVariables,
        SystemEmailVariables,
        AccountEmailVariables,
        DocumentEmailVariables,
        KYCEmailVariables,
        TransactionEmailVariables,
        ReferralEmailVariables, 
        TicketEmailVariables,
        RequestEmailVariables
    ]

    for var_class in _variable_classes:
        # Check if the class itself exists before iterating
        if var_class:
            for attr in dir(var_class):
                if not attr.startswith('_') and isinstance(getattr(var_class, attr, None), str):
                    _all_vars[attr] = getattr(var_class, attr)

    # Dynamically set class attributes from the aggregated dictionary
    for key, value in _all_vars.items():
        locals()[key] = value
        
    # Clean up temporary variables used during class creation
    del _all_vars
    del _variable_classes
    del var_class
    del attr
    del key
    del value

