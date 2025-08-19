from enum import Enum
from typing import List, NamedTuple


class PermissionAction(str, Enum):
    VIEW_PAR = "VIEW_PAR"
    EDIT_PAR = "EDIT_PAR"
    PM_CREATE_PAR = "PM_CREATE_PAR"
    PM_SUBMIT_PROTRACK = "PM_SUBMIT_PROTRACK"
    DOWNLOAD_PAR = "DOWNLOAD_PAR"
    PM_VIEW_STATUS = "PM_VIEW_STATUS"
    PM_RECEIVE_NOTIFICATIONS = "PM_RECEIVE_NOTIFICATIONS"
    FO_PERFORM_RAD = "FO_PERFORM_RAD"
    FO_RAD_APPROVE = "FO_RAD_APPROVE"
    FO_PERFORM_OCFO = "FO_PERFORM_OCFO"
    FO_OCFO_APPROVE = "FO_OCFO_APPROVE"
    FO_SUBMIT_FHWA = "FO_SUBMIT_FHWA"
    BA_EDIT_FUNDING_SOURCE = "BA_EDIT_FUNDING_SOURCE"
    BA_SET_FUNDING_RATE = "BA_SET_FUNDING_RATE"
    BA_MANAGE_PROGRAM_CODES = "BA_MANAGE_PROGRAM_CODES"
    BA_VIEW_BUDGET_SUMMARY = "BA_VIEW_BUDGET_SUMMARY"
    BA_EXPORT_BUDGET = "BA_EXPORT_BUDGET"
    BA_SUBMIT_BUDGET_VALIDATION = "BA_SUBMIT_BUDGET_VALIDATION"
    OBV_VIEW_BUDGET = "OBV_VIEW_BUDGET"
    OBV_VALIDATE_CALCULATIONS = "OBV_VALIDATE_CALCULATIONS"
    OBV_APPROVE_BUDGET = "OBV_APPROVE_BUDGET"
    OBV_REJECT_BUDGET = "OBV_REJECT_BUDGET"
    OBV_VIEW_PROGRAM_CODES = "OBV_VIEW_PROGRAM_CODES"
    SA_USER_MANAGEMENT = "SA_USER_MANAGEMENT"
    SA_ROLE_MANAGEMENT = "SA_ROLE_MANAGEMENT"
    SA_VIEW_AUDIT_LOGS = "SA_VIEW_AUDIT_LOGS"
    SA_MANAGE_INTEGRATIONS = "SA_MANAGE_INTEGRATIONS"
    SA_SECURITY_SETTINGS = "SA_SECURITY_SETTINGS"
    SA_SYSTEM_MONITORING = "SA_SYSTEM_MONITORING"
    API_PROTRACK_READ = "API_PROTRACK_READ"
    API_PROTRACK_WRITE = "API_PROTRACK_WRITE"
    API_FMIS_READ = "API_FMIS_READ"
    API_FMIS_WRITE = "API_FMIS_WRITE"
    API_DIFS_READ = "API_DIFS_READ"
    API_DIFS_WRITE = "API_DIFS_WRITE"
    CREATE = "CREATE"
    VIEW = "VIEW"
    EDIT = "EDIT"
    DELETE = "DELETE"
    MANAGE = "MANAGE"
    DOWNLOAD = "DOWNLOAD"
    CONFIGURE_IMPORTANCE = "CONFIGURE_IMPORTANCE"
    VIEW_FIELD_RESULTS = "VIEW_FIELD_RESULTS"
    UPDATE_STATUS = "UPDATE_STATUS"
    CONFIGURE = "CONFIGURE"
    TEST = "TEST"
    VIEW_FIELD_STATISTICS = "VIEW_FIELD_STATISTICS"
    FETCH = "FETCH"
    CREATE_DRAFT = "CREATE_DRAFT"
    SEND_DRAFT = "SEND_DRAFT"
    EDIT_EMAIL_SETTINGS = "EDIT_EMAIL_SETTINGS"
    REASSIGN_DEPT_TEAM = "REASSIGN_DEPT_TEAM"
    VIEW_EMAIL_QUEUE = "VIEW_EMAIL_QUEUE"
    FILTER_EMAILS = "FILTER_EMAILS"
    UPDATE_DRAFT = "UPDATE_DRAFT"
    MANAGE_DEPARTMENTS = "MANAGE_DEPARTMENTS"
    MANAGE_CATEGORIES = "MANAGE_CATEGORIES"
    MANAGE_TEAM_MEMBERS = "MANAGE_TEAM_MEMBERS"
    MANAGE_REMINDERS = "MANAGE_REMINDERS"
    MANAGE_KNOWLEDGE_BASE = "MANAGE_KNOWLEDGE_BASE"
    VIEW_DASHBOARD = "VIEW_DASHBOARD"
    VIEW_INSIGHTS = "VIEW_INSIGHTS"
    RUN_ANALYSIS = "RUN_ANALYSIS"
    GENERATE_REPORT = "GENERATE_REPORT"
    PUBLISH = "PUBLISH"
    UPLOAD = "UPLOAD"
    GENERATE = "GENERATE"
    VIEW_STATS = "VIEW_STATS"
    FILTER_BY_DEPARTMENT = "FILTER_BY_DEPARTMENT"
    EXPORT_REPORTS = "EXPORT_REPORTS"
    VIEW_RECENT_COMPLAINTS = "VIEW_RECENT_COMPLAINTS"
    VIEW_RESPONSE_TIMES = "VIEW_RESPONSE_TIMES"
    SEARCH = "SEARCH"
    VIEW_METADATA = "VIEW_METADATA"
    EDIT_METADATA = "EDIT_METADATA"
    VIEW_DOCUMENT = "VIEW_DOCUMENT"
    CREATE_DOCUMENT = "CREATE_DOCUMENT"
    EDIT_DOCUMENT = "EDIT_DOCUMENT"
    DELETE_DOCUMENT = "DELETE_DOCUMENT"
    DOWNLOAD_DOCUMENT = "DOWNLOAD_DOCUMENT"
    PREVIEW_DOCUMENT = "PREVIEW_DOCUMENT"
    ASK_QUESTIONS = "ASK_QUESTIONS"
    VIEW_STATISTICS = "VIEW_STATISTICS"
    APPLY_FILTERS = "APPLY_FILTERS"
    MANAGE_DOCUMENTS = "MANAGE_DOCUMENTS"
    MANAGE_CONTAINERS = "MANAGE_CONTAINERS"
    MANAGE_DATA_SOURCES = "MANAGE_DATA_SOURCES"
    MANAGE_INSTRUCTIONS = "MANAGE_INSTRUCTIONS"
    MANAGE_TOOLS = "MANAGE_TOOLS"
    MANAGE_TRIGGERS = "MANAGE_TRIGGERS"
    OPERATE = "OPERATE"
    MODIFY_PUBLISHED = "MODIFY_PUBLISHED"
    INITIALIZE = "INITIALIZE"
    ACCESS_SHAREPOINT = "ACCESS_SHAREPOINT"
    ACCESS_AZURE_STORAGE = "ACCESS_AZURE_STORAGE"
    ASSIGN = "ASSIGN"
    ADD_NOTE = "ADD_NOTE"
    VIEW_ALL_MESSAGES="VIEW_ALL_MESSAGES"
    VIEW_DEPARTMENT_MESSAGES="VIEW_DEPARTMENT_MESSAGES"
    VIEW_OWN_MESSAGES="VIEW_OWN_MESSAGES"
    VIEW_ALL_DEPARTMENT_DATA="VIEW_ALL_DEPARTMENT_DATA"
    VIEW_OWN_DEPARTMENT_DATA="VIEW_OWN_DEPARTMENT_DATA"
    CONFIGURE_EMAIL_SETTINGS="CONFIGURE_EMAIL_SETTINGS"
    ADD_KNOWLEDGE="ADD_KNOWLEDGE"
    CHANGE_DEPARTMENT_SETTINGS="CHANGE_DEPARTMENT_SETTINGS"
    ASSIGN_USERS_TO_DEPARTMENTS="ASSIGN_USERS_TO_DEPARTMENTS"
    ASSIGN_USERS_WITHIN_DEPARTMENT="ASSIGN_USERS_WITHIN_DEPARTMENT"
    LOGIN_ACCESS="LOGIN_ACCESS"
    FORM_ONLY_ACCESS="FORM_ONLY_ACCESS"
    TRACK_USER_ACTIONS="TRACK_USER_ACTIONS"
    GENERATE_ALL_REPORTS="GENERATE_ALL_REPORTS"
    GENERATE_DEPARTMENT_REPORTS="GENERATE_DEPARTMENT_REPORTS"
    VIEW_ALL_ANALYTICS="VIEW_ALL_ANALYTICS"
    VIEW_DEPARTMENT_ANALYTICS="VIEW_DEPARTMENT_ANALYTICS"
    MANAGE_DEPARTMENT_ROUTING="MANAGE_DEPARTMENT_ROUTING"
    SYNC_EMAILS="SYNC_EMAILS"
    SEND_EMAIL_RESPONSES="SEND_EMAIL_RESPONSES"
    ACCESS_VOICEMAIL_SYSTEM="ACCESS_VOICEMAIL_SYSTEM"
    TRANSCRIBE_VOICEMAILS="TRANSCRIBE_VOICEMAILS"
    CALLBACK_CONSTITUENTS="CALLBACK_CONSTITUENTS"
    SCAN_PHYSICAL_MAIL="SCAN_PHYSICAL_MAIL"
    OCR_DOCUMENT_PROCESSING="OCR_DOCUMENT_PROCESSING"
    HANDLE_PHYSICAL_RESPONSES="HANDLE_PHYSICAL_RESPONSES"
    CONFIGURE_FORMS="CONFIGURE_FORMS"
    VIEW_FORM_SUBMISSIONS="VIEW_FORM_SUBMISSIONS"
    SUBMIT_FORMS="SUBMIT_FORMS"
    SEND_DRAFTS = "SEND_DRAFTS"
    HANDLE_VOICEMAIL_RESPONSES = "HANDLE_VOICEMAIL_RESPONSES"
    PROCESS_PHYSICAL_MAIL = "PROCESS_PHYSICAL_MAIL"
    RESPOND_VIA_FORMS = "RESPOND_VIA_FORMS"
    INITIATE_OUTBOUND_COMMUNICATIONS = "INITIATE_OUTBOUND_COMMUNICATIONS"
    CREATE_EMAIL_CHANNELS = "CREATE_EMAIL_CHANNELS"
    SYNC_EMAIL_CHANNELS = "SYNC_EMAIL_CHANNELS"
    SETUP_VOICEMAIL_CHANNELS = "SETUP_VOICEMAIL_CHANNELS"
    CONFIGURE_PHYSICAL_MAIL_INTAKE = "CONFIGURE_PHYSICAL_MAIL_INTAKE"
    SETUP_FORM_CHANNELS = "SETUP_FORM_CHANNELS"
    CREATE_MESSAGES = "CREATE_MESSAGES"
    UPDATE_MESSAGES = "UPDATE_MESSAGES"
    DELETE_MESSAGES = "DELETE_MESSAGES"
    REASSIGN_MESSAGES = "REASSIGN_MESSAGES"
    ARCHIVE_MESSAGES = "ARCHIVE_MESSAGES"
    VIEW_BILLING = "VIEW_BILLING"
    DELETE_BILLING = "DELETE_BILLING"
    EDIT_BILLING = "EDIT_BILLING"
    CREATE_BILLING = "CREATE_BILLING"
    VIEW_ASL = "VIEW_ASL"
    CONNECT_ACCOUNT = "CONNECT_ACCOUNT"
    VIEW_IMPORT_DATA = "VIEW_IMPORT_DATA"
    VIEW_WORKFLOW = "VIEW_WORKFLOW"
    VIEW_ERROR_DATA = "VIEW_ERROR_DATA"




class PermissionModule(str, Enum):
    AUTOMATION_BUILDER = "AUTOMATION_BUILDER"
    EDS_EPAR = "EDS_EPAR"
    PERMIT_PROCESSING = "PERMIT_PROCESSING"
    EMAIL_PROCESS = "EMAIL_PROCESS"
    CONTRACT_ANALYSIS = "CONTRACT_ANALYSIS"
    CONSTITUENT_COMPLAINTS = "CONSTITUENT_COMPLAINTS"
    LEGAL_ASSISTANT = "LEGAL_ASSISTANT"
    REPORTING = "REPORTING"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    AI_EMS="AI_EMS"
    ENTITY_MANAGER="ENTITY_MANAGER"
    ASL = "ASL"
    EDS = "EDS"
    WORKFORCE_AGENT = "WORKFORCE_AGENT"



class PermissionResource(str, Enum):
    DASHBOARD = "DASHBOARDS"
    WORKFORCE_AGENT = "WORKFORCE_AGENT"
    EPAR = "EPAR"
    EPARS = "EPARS"
    OCFO = "OCFO"
    EDS_ASSISTANT = "EDS_ASSISTANT"
    REPORTS = "REPORTS"
    WORKFLOW = "WORKFLOW"
    FEEDBACK = "FEEDBACK"
    OCFO_TUTORIALS = "OCFO_TUTORIALS"
    EPAR_TUTORIALS = "EPAR_TUTORIALS"
    RECENT_REVIEW_EPARS = "RECENT_REVIEW_EPARS"
    EPAR_PROTRACK_INTEGRATION = "EPAR_PROTRACK_INTEGRATION"
    EPAR_DASHBOARD = "EPAR_DASHBOARD"
    NOTIFICATIONS = "NOTIFICATIONS"
    FINANCIAL_REVIEW = "FINANCIAL_REVIEW"
    EPAR_FHWA_INTEGRATION = "EPAR_FHWA_INTEGRATION"
    FEDERAL_FUNDING = "FEDERAL_FUNDING"
    BUDGET_ANALYSIS = "BUDGET_ANALYSIS"
    BUDGET_WORKFLOW = "BUDGET_WORKFLOW"
    BUDGET_VALIDATION = "BUDGET_VALIDATION"
    ADMINISTRATION = "ADMINISTRATION"
    SECURITY = "SECURITY"
    SYSTEM_INTEGRATION = "SYSTEM_INTEGRATION"
    PERMIT_PROCESS = "PERMIT_PROCESS"
    PERMIT_CRITERIA = "PERMIT_CRITERIA"
    PERMIT_TEMPLATE = "PERMIT_TEMPLATE"
    PERMIT_FIELD = "PERMIT_FIELD"
    PERMIT_INTEGRATION = "PERMIT_INTEGRATION"
    PERMIT_EVALUATION = "PERMIT_EVALUATION"
    PERMIT_NOTIFICATION = "PERMIT_NOTIFICATION"
    PERMIT_DASHBOARD = "PERMIT_DASHBOARD"
    PERMIT_DETERMINATION = "PERMIT_DETERMINATION"
    PERMIT_FIELD_API = "PERMIT_FIELD_API"
    PERMIT_AUDIT = "PERMIT_AUDIT"
    PERMIT_REPORT = "PERMIT_REPORT"
    PERMIT_EXPLANATION = "PERMIT_EXPLANATION"
    EMAIL_PROCESS = "EMAIL_PROCESS"
    RBAC = "RBAC"
    CONTRACT = "CONTRACT"
    CONTRACT_ANALYSIS = "CONTRACT_ANALYSIS"
    AUDIT = "AUDIT"
    RFP = "RFP"
    FINANCIAL_ANALYTICS = "FINANCIAL_ANALYTICS"
    DEPARTMENT_DISTRIBUTION = "DEPARTMENT_DISTRIBUTION"
    CONTRACT_FILTERS = "CONTRACT_FILTERS"
    VENDOR_PERFORMANCE = "VENDOR_PERFORMANCE"
    CONTRACT_NOTE = "CONTRACT_NOTE"
    CONTRACT_DOCUMENT = "CONTRACT_DOCUMENT"
    NETWORK_ANALYSIS = "NETWORK_ANALYSIS"
    PREDICTIVE_ANALYSIS = "PREDICTIVE_ANALYSIS"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    UTILIZATION_ASSESSMENT = "UTILIZATION_ASSESSMENT"
    AI_INSIGHTS = "AI_INSIGHTS"
    REPORTING = "REPORTING"
    SETTINGS = "SETTINGS"
    CONSTITUENT_COMPLAINTS = "CONSTITUENT_COMPLAINTS"
    MESSAGE_MANAGEMENT_PERMISSIONS="MESSAGE_MANAGEMENT_PERMISSIONS"
    DEPARTMENT_MANAGEMENT_PERMISSIONS="DEPARTMENT_MANAGEMENT_PERMISSIONS"
    CHANNEL_SPECIFIC_PERMISSIONS="CHANNEL_SPECIFIC_PERMISSIONS"
    LEGAL_ASSISTANT = "LEGAL_ASSISTANT"
    KNOWLEDGE_SOURCE = "KNOWLEDGE_SOURCE"
    AGENT_CONFIG = "AGENT_CONFIG"
    AGENT_DEPLOYMENT = "AGENT_DEPLOYMENT"
    AGENT_SYSTEM = "AGENT_SYSTEM"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    ROLE_MANAGEMENT = "ROLE_MANAGEMENT"
    FACILITIES = "FACILITIES"
    PATIENT_RECORDS = "PATIENT_RECORDS"
    CALLS_AND_SMS = "CALLS_AND_SMS"
    ANALYTICS = "ANALYTICS"
    HELP = "HELP"
    SYSTEM_ACCESS_TRACKING_PERMISSIONS="SYSTEM_ACCESS_TRACKING_PERMISSIONS"
    ENTITY_MANAGER="ENTITY_MANAGER"
    COMMUNICATION_ACTIONS="COMMUNICATION_ACTIONS"
    COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS="COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS"
    BILLING_MANAGEMENT = "BILLING_MANAGEMENT"
    ASL = "ASL"
    DATA_IMPORT = "DATA_IMPORT"
    INTEGRATION = "INTEGRATION"
    AUTOMATION = "AUTOMATION"
    AUTOMATION_TRIGGER = "AUTOMATION_TRIGGER"
    AUTOMATION_ACTION = "AUTOMATION_ACTION"
    AUTOMATION_INPUT = "AUTOMATION_INPUT"
    AUTOMATION_HISTORY = "AUTOMATION_HISTORY"


class PermissionData(NamedTuple):
    name: str
    description: str
    module: str
    resource: str
    action: str


class PermissionConstants:
    # Automation Builder Permissions
    AUTOMATION_HISTORY_VIEW = PermissionData(
        name="View Automation History",
        description="Permission to view automation history",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_HISTORY,
        action=PermissionAction.VIEW,
    )
    AUTOMATION_CREATE = PermissionData(
        name="Create Automation",
        description="Permission to create automation",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION,
        action=PermissionAction.CREATE,
    )
    AUTOMATION_VIEW = PermissionData(
        name="View Automation",
        description="Permission to view automation",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION,
        action=PermissionAction.VIEW,
    )
    AUTOMATION_EDIT = PermissionData(
        name="Edit Automation",
        description="Permission to edit automation",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION,
        action=PermissionAction.EDIT,
    )
    AUTOMATION_DELETE = PermissionData(
        name="Delete Automation",
        description="Permission to delete automation",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION,
        action=PermissionAction.DELETE,
    )
    AUTOMATION_INPUT_CREATE = PermissionData(
        name="Create Automation Input",
        description="Permission to create automation input",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_INPUT,
        action=PermissionAction.CREATE,
    )
    AUTOMATION_INPUT_VIEW = PermissionData(
        name="View Automation Input",
        description="Permission to view automation input",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_INPUT,
        action=PermissionAction.VIEW,
    )
    AUTOMATION_INPUT_EDIT = PermissionData(
        name="Edit Automation Input",
        description="Permission to edit automation input",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_INPUT,
        action=PermissionAction.EDIT,
    )
    AUTOMATION_INPUT_DELETE = PermissionData(
        name="Delete Automation Input",
        description="Permission to delete automation input",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_INPUT,
        action=PermissionAction.DELETE,
    )
    AUTOMATION_ACTION_CREATE = PermissionData(
        name="Create Automation Action",
        description="Permission to create automation action",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_ACTION,
        action=PermissionAction.CREATE,
    )
    AUTOMATION_ACTION_VIEW = PermissionData(
        name="View Automation Action",
        description="Permission to view automation action",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_ACTION,
        action=PermissionAction.VIEW,
    )   
    AUTOMATION_ACTION_EDIT = PermissionData(
        name="Edit Automation Action",
        description="Permission to edit automation action",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_ACTION,
        action=PermissionAction.EDIT,
    )
    AUTOMATION_ACTION_DELETE = PermissionData(
        name="Delete Automation Action",
        description="Permission to delete automation action",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_ACTION,
        action=PermissionAction.DELETE,
    )
    AUTOMATION_TRIGGER_CREATE = PermissionData(
        name="Create Automation Trigger",
        description="Permission to create automation trigger",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_TRIGGER,
        action=PermissionAction.CREATE,
    )
    AUTOMATION_TRIGGER_VIEW = PermissionData(
        name="View Automation Trigger",
        description="Permission to view automation trigger",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_TRIGGER,
        action=PermissionAction.VIEW,
    )
    AUTOMATION_TRIGGER_EDIT = PermissionData(
        name="Edit Automation Trigger",
        description="Permission to edit automation trigger",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_TRIGGER,
        action=PermissionAction.EDIT,
    )
    AUTOMATION_TRIGGER_DELETE = PermissionData(
        name="Delete Automation Trigger",
        description="Permission to delete automation trigger",
        module=PermissionModule.AUTOMATION_BUILDER,
        resource=PermissionResource.AUTOMATION_TRIGGER,
        action=PermissionAction.DELETE,
    )

    # EDS Data Import Permissions
    EDS_DATA_IMPORT_CONNECT_ACCOUNT = PermissionData(
        name="Connect Account",
        description="Connect Account",
        module=PermissionModule.EDS,
        resource=PermissionResource.DATA_IMPORT,
        action=PermissionAction.CONNECT_ACCOUNT
    )

    EDS_DATA_IMPORT_VIEW_IMPORT_DATA = PermissionData(
        name="View Import Data",
        description="View Import Data",
        module=PermissionModule.EDS,
        resource=PermissionResource.DATA_IMPORT,
        action=PermissionAction.VIEW_IMPORT_DATA
    )

    EDS_DATA_IMPORT_VIEW_WORKFLOW = PermissionData(
        name="View Workflow",
        description="View Workflow",
        module=PermissionModule.EDS,
        resource=PermissionResource.DATA_IMPORT,
        action=PermissionAction.VIEW_WORKFLOW
    )

    EDS_DATA_IMPORT_VIEW_ERROR_DATA = PermissionData(
        name="View Error Data",
        description="View Error Data",
        module=PermissionModule.EDS,
        resource=PermissionResource.DATA_IMPORT,
        action=PermissionAction.VIEW_ERROR_DATA
    )

    # EDS Integration Permissions
    EDS_INTEGRATION_CONNECT_ACCOUNT = PermissionData(
        name="Connect Account",
        description="Connect Account",
        module=PermissionModule.EDS,
        resource=PermissionResource.INTEGRATION,
        action=PermissionAction.CONNECT_ACCOUNT
    )

    EDS_DASHBOARD_VIEW = PermissionData(
        name="View EDS Dashboard",
        description="View EDS Dashboard",
        module=PermissionModule.EDS,
        resource=PermissionResource.DASHBOARD,
        action=PermissionAction.VIEW,
    )
    EDS_EPARS_VIEW = PermissionData(
        name="View EPARs",
        description="View EPARs",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPARS,
        action=PermissionAction.VIEW,
    )
    EDS_OCFO_VIEW = PermissionData(
        name="View OCFO",
        description="View OCFO",
        module=PermissionModule.EDS,
        resource=PermissionResource.OCFO,
        action=PermissionAction.VIEW,
    )
    EDS_EDS_ASSISTANT_VIEW = PermissionData(
        name="View EDS Assistant",
        description="View EDS Assistant",
        module=PermissionModule.EDS,
        resource=PermissionResource.EDS_ASSISTANT,
        action=PermissionAction.VIEW,
    )
    EDS_REPORTS_VIEW = PermissionData(
        name="View Reports",
        description="View Reports",
        module=PermissionModule.EDS,
        resource=PermissionResource.REPORTS,
        action=PermissionAction.VIEW,
    )
    EDS_EAPR_CREATE = PermissionData(
        name="Create EPAR",
        description="Create EPAR",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPAR,
        action=PermissionAction.CREATE,
    )
    EDS_EPAR_EDIT = PermissionData(
        name="Edit EPAR",
        description="Edit EPAR",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPAR,
        action=PermissionAction.EDIT,
    )
    EDS_EPAR_DOWNLOAD = PermissionData(
        name="Download EPAR",
        description="Download EPAR",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPAR,
        action=PermissionAction.DOWNLOAD,
    )
    EDS_EPAR_VIEW = PermissionData(
        name="View EPAR",
        description="View EPAR",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPAR,
        action=PermissionAction.VIEW,
    )
    EDS_WORKFLOW_VIEW = PermissionData(
        name="View Workflow",
        description="View Workflow",
        module=PermissionModule.EDS,
        resource=PermissionResource.WORKFLOW,
        action=PermissionAction.VIEW,
    )
    EDS_FEEDBACK_VIEW = PermissionData(
        name="View Feedback",
        description="View Feedback",
        module=PermissionModule.EDS,
        resource=PermissionResource.FEEDBACK,
        action=PermissionAction.VIEW,
    )
    EDS_OCFO_TUTORIALS_VIEW = PermissionData(
        name="View OCFO Tutorials",
        description="View OCFO Tutorials",
        module=PermissionModule.EDS,
        resource=PermissionResource.OCFO_TUTORIALS,
        action=PermissionAction.VIEW,
    )
    EDS_EPAR_TUTORIALS_VIEW = PermissionData(
        name="View EPAR Tutorials",
        description="View EPAR Tutorials",
        module=PermissionModule.EDS,
        resource=PermissionResource.EPAR_TUTORIALS,
        action=PermissionAction.VIEW,
    )
    EDS_RECENT_REVIEW_EPARS_VIEW = PermissionData(
        name="View Recent Review EPARs",
        description="View Recent Review EPARs",
        module=PermissionModule.EDS,
        resource=PermissionResource.RECENT_REVIEW_EPARS,
        action=PermissionAction.VIEW,
    )
    VIEW_BILLING = PermissionData(
        name="View Billing",
        description="View Billing accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.BILLING_MANAGEMENT,
        action=PermissionAction.VIEW_BILLING,
    )

    DELETE_BILLING = PermissionData(
        name="Delete Billing",
        description="Delete Billing accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.BILLING_MANAGEMENT,
        action=PermissionAction.DELETE_BILLING,
    )

    EDIT_BILLING = PermissionData(
        name="Edit Billing",
        description="Edit existing Billing accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.BILLING_MANAGEMENT,
        action=PermissionAction.EDIT_BILLING,
    )

    CREATE_BILLING = PermissionData(
        name="Create Billing",
        description="Create new Billing accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.BILLING_MANAGEMENT,
        action=PermissionAction.CREATE_BILLING,
    )

    VIEW_ASL = PermissionData(
        name="View ASL",
        description="View ASL",
        module=PermissionModule.ASL,
        resource=PermissionResource.ASL,
        action=PermissionAction.VIEW_ASL,
    )

    SEND_EMAIL_RESPONSES = PermissionData(
        name="Send Email Responses",
        description="Permission to send email responses",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.SEND_EMAIL_RESPONSES,
    )

    SEND_DRAFTS = PermissionData(
        name="Send Drafts",
        description="Permission to send drafts",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.SEND_DRAFTS,
    )

    HANDLE_VOICEMAIL_RESPONSES = PermissionData(
        name="Handle Voicemail Responses",
        description="Permission to handle voicemail responses",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.HANDLE_VOICEMAIL_RESPONSES,
    )

    PROCESS_PHYSICAL_MAIL = PermissionData(
        name="Process Physical Mail",
        description="Permission to process physical mail",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.PROCESS_PHYSICAL_MAIL,
    )

    RESPOND_VIA_FORMS = PermissionData(
        name="Respond via Forms",
        description="Permission to respond via forms",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.RESPOND_VIA_FORMS,
    )

    INITIATE_OUTBOUND_COMMUNICATIONS = PermissionData(
        name="Initiate Outbound Communications",
        description="Permission to initiate outbound communications",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_ACTIONS,
        action=PermissionAction.INITIATE_OUTBOUND_COMMUNICATIONS,
    )

    CREATE_EMAIL_CHANNELS = PermissionData(
        name="Create Email Channels",
        description="Permission to create email channels",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.CREATE_EMAIL_CHANNELS,
    )

    SYNC_EMAIL_CHANNELS = PermissionData(
        name="Sync Email Channels",
        description="Permission to sync email channels",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.SYNC_EMAIL_CHANNELS,
    )

    SETUP_VOICEMAIL_CHANNELS = PermissionData(
        name="Setup Voicemail Channels",
        description="Permission to set up voicemail channels",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.SETUP_VOICEMAIL_CHANNELS,
    )

    CONFIGURE_PHYSICAL_MAIL_INTAKE = PermissionData(
        name="Configure Physical Mail Intake",
        description="Permission to configure physical mail intake",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.CONFIGURE_PHYSICAL_MAIL_INTAKE,
    )

    SETUP_FORM_CHANNELS = PermissionData(
        name="Setup Form Channels",
        description="Permission to set up form channels",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.COMMUNICATION_CHANNEL_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.SETUP_FORM_CHANNELS,
    )

    VIEW_ALL_MESSAGES = PermissionData(
        name="View All Messages",
        description="Permission to view all messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_ALL_MESSAGES,
    )

    VIEW_DEPARTMENT_MESSAGES = PermissionData(
        name="View Department Messages",
        description="Permission to view department messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_DEPARTMENT_MESSAGES,
    )

    VIEW_OWN_MESSAGES = PermissionData(
        name="View Own Messages",
        description="Permission to view own messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_OWN_MESSAGES,
    )

    CREATE_MESSAGES = PermissionData(
        name="Create Messages",
        description="Permission to create messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.CREATE_MESSAGES,
    )

    UPDATE_MESSAGES = PermissionData(
        name="Update Message",
        description="Permission to update messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.UPDATE_MESSAGES,
    )

    DELETE_MESSAGES = PermissionData(
        name="Delete Messages",
        description="Permission to delete messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.DELETE_MESSAGES,
    )

    REASSIGN_MESSAGES = PermissionData(
        name="Reassign Messages",
        description="Permission to reassign messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.REASSIGN_MESSAGES,
    )

    ARCHIVE_MESSAGES = PermissionData(
        name="Archive Messages",
        description="Permission to archive messages",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.ARCHIVE_MESSAGES,
    )


    # AI EMS Permissions
    AI_EMS_FACILITIES_CREATE = PermissionData(
        name="Create AI EMS",
        description="Permission to create AI EMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.FACILITIES,
        action=PermissionAction.CREATE,
    )
    AI_EMS_FACILITIES_VIEW = PermissionData(
        name="View AI EMS",
        description="Permission to view AI EMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.FACILITIES,
        action=PermissionAction.VIEW,
    )
    AI_EMS_FACILITIES_EDIT = PermissionData(
        name="Edit AI EMS",
        description="Permission to edit AI EMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.FACILITIES,
        action=PermissionAction.EDIT,
    )
    AI_EMS_FACILITIES_DELETE = PermissionData(
        name="Delete AI EMS",
        description="Permission to delete AI EMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.FACILITIES,
        action=PermissionAction.DELETE,
    )

    AI_EMS_PATIENT_RECORDS_CREATE = PermissionData(
        name="Create AI EMS Patient Records",
        description="Permission to create AI EMS patient records",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.PATIENT_RECORDS,
        action=PermissionAction.CREATE,
    )
    AI_EMS_PATIENT_RECORDS_VIEW = PermissionData(
        name="View AI EMS Patient Records",
        description="Permission to view AI EMS patient records",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.PATIENT_RECORDS,
        action=PermissionAction.VIEW,
    )
    AI_EMS_PATIENT_RECORDS_EDIT = PermissionData(
        name="Edit AI EMS Patient Records",
        description="Permission to edit AI EMS patient records",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.PATIENT_RECORDS,
        action=PermissionAction.EDIT,
    )
    AI_EMS_PATIENT_RECORDS_DELETE = PermissionData(
        name="Delete AI EMS Patient Records",
        description="Permission to delete AI EMS patient records",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.PATIENT_RECORDS,
        action=PermissionAction.DELETE,
    )
    AI_EMS_CALLS_AND_SMS_CREATE = PermissionData(
        name="Create AI EMS Calls and SMS",
        description="Permission to create AI EMS calls and SMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.CALLS_AND_SMS,
        action=PermissionAction.CREATE,
    )
    AI_EMS_CALLS_AND_SMS_VIEW = PermissionData(
        name="View AI EMS Calls and SMS",
        description="Permission to view AI EMS calls and SMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.CALLS_AND_SMS,
        action=PermissionAction.VIEW,
    )
    AI_EMS_CALLS_AND_SMS_EDIT = PermissionData(
        name="Edit AI EMS Calls and SMS",
        description="Permission to edit AI EMS calls and SMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.CALLS_AND_SMS,
        action=PermissionAction.EDIT,
    )
    AI_EMS_CALLS_AND_SMS_DELETE = PermissionData(
        name="Delete AI EMS Calls and SMS",
        description="Permission to delete AI EMS calls and SMS",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.CALLS_AND_SMS,
        action=PermissionAction.DELETE,
    )

    AI_EMS_ANALYTICS_VIEW = PermissionData(
        name="View AI EMS Analytics",
        description="Permission to view AI EMS analytics",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.ANALYTICS,
        action=PermissionAction.VIEW,
    )
    AI_EMS_ANALYTICS_EDIT = PermissionData(
        name="Edit AI EMS Analytics",
        description="Permission to edit AI EMS analytics",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.ANALYTICS,
        action=PermissionAction.EDIT,
    )
    AI_EMS_ANALYTICS_DELETE = PermissionData(
        name="Delete AI EMS Analytics",
        description="Permission to delete AI EMS analytics",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.ANALYTICS,
        action=PermissionAction.DELETE,
    )

    AI_EMS_HELP_VIEW = PermissionData(
        name="View AI EMS Help",
        description="Permission to view AI EMS help",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.HELP,
        action=PermissionAction.VIEW,
    )
    AI_EMS_HELP_EDIT = PermissionData(
        name="Edit AI EMS Help",
        description="Permission to edit AI EMS help",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.HELP,
        action=PermissionAction.EDIT,
    )
    AI_EMS_HELP_DELETE = PermissionData(
        name="Delete AI EMS Help",
        description="Permission to delete AI EMS help",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.HELP,
        action=PermissionAction.DELETE,
    )
    AI_EMS_HELP_CREATE = PermissionData(
        name="Create AI EMS Help",
        description="Permission to create AI EMS help",
        module=PermissionModule.AI_EMS,
        resource=PermissionResource.HELP,
        action=PermissionAction.CREATE,
    )

    # Workforce Agent Permissions
    WORKFORCE_AGENT_CREATE = PermissionData(
        name="Create Workforce Agent",
        description="Permission to create workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.CREATE,
    )

    WORKFORCE_AGENT_VIEW = PermissionData(
        name="View Workforce Agent",
        description="Permission to view workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.VIEW,
    )

    WORKFORCE_AGENT_EDIT = PermissionData(
        name="Edit Workforce Agent",
        description="Permission to edit workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.EDIT,
    )

    WORKFORCE_AGENT_DELETE = PermissionData(
        name="Delete Workforce Agent",
        description="Permission to delete workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.DELETE,
    )

    WORKFORCE_AGENT_MANAGE_DOCUMENTS = PermissionData(
        name="Manage Agent Documents",
        description="Permission to manage workforce agent documents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_DOCUMENTS,
    )

    WORKFORCE_AGENT_MANAGE_CONTAINERS = PermissionData(
        name="Manage Agent Containers",
        description="Permission to manage workforce agent containers",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_CONTAINERS,
    )

    WORKFORCE_AGENT_MANAGE_DATA_SOURCES = PermissionData(
        name="Manage Agent Data Sources",
        description="Permission to manage workforce agent data sources",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_DATA_SOURCES,
    )

    WORKFORCE_AGENT_MANAGE_INSTRUCTIONS = PermissionData(
        name="Manage Agent Instructions",
        description="Permission to manage workforce agent instructions",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_INSTRUCTIONS,
    )

    WORKFORCE_AGENT_MANAGE_TOOLS = PermissionData(
        name="Manage Agent Tools",
        description="Permission to manage workforce agent tools",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_TOOLS,
    )

    WORKFORCE_AGENT_MANAGE_TRIGGERS = PermissionData(
        name="Manage Agent Triggers",
        description="Permission to manage workforce agent triggers",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MANAGE_TRIGGERS,
    )

    WORKFORCE_AGENT_PUBLISH = PermissionData(
        name="Publish Agent",
        description="Permission to publish workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.PUBLISH,
    )

    WORKFORCE_AGENT_OPERATE = PermissionData(
        name="Operate Agent",
        description="Permission to operate workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.OPERATE,
    )

    WORKFORCE_AGENT_MODIFY_PUBLISHED = PermissionData(
        name="Modify Published Agent",
        description="Permission to modify published workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.MODIFY_PUBLISHED,
    )

    WORKFORCE_AGENT_INITIALIZE = PermissionData(
        name="Initialize Agent",
        description="Permission to initialize workforce agents",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.INITIALIZE,
    )

    WORKFORCE_AGENT_ACCESS_SHAREPOINT = PermissionData(
        name="Access SharePoint",
        description="Permission for workforce agents to access SharePoint",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.ACCESS_SHAREPOINT,
    )

    WORKFORCE_AGENT_ACCESS_AZURE_STORAGE = PermissionData(
        name="Access Azure Storage",
        description="Permission for workforce agents to access Azure Storage",
        module=PermissionModule.WORKFORCE_AGENT,
        resource=PermissionResource.WORKFORCE_AGENT,
        action=PermissionAction.ACCESS_AZURE_STORAGE,
    )

    # Constituent Complaints Permissions
    COMPLAINT_VIEW = PermissionData(
        name="View Complaints",
        description="Permission to view constituent complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.VIEW,
    )
    COMPLAINT_CREATE = PermissionData(
        name="Create Complaint",
        description="Permission to create new constituent complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.CREATE,
    )
    COMPLAINT_EDIT = PermissionData(
        name="Edit Complaint",
        description="Permission to edit existing constituent complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.EDIT,
    )
    COMPLAINT_DELETE = PermissionData(
        name="Delete Complaint",
        description="Permission to delete constituent complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.DELETE,
    )
    COMPLAINT_ASSIGN = PermissionData(
        name="Assign Complaint",
        description="Permission to assign complaints to team members",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.ASSIGN,
    )
    COMPLAINT_UPDATE_STATUS = PermissionData(
        name="Update Complaint Status",
        description="Permission to update the status of complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.UPDATE_STATUS,
    )
    COMPLAINT_ADD_NOTE = PermissionData(
        name="Add Complaint Note",
        description="Permission to add notes to complaints",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.ADD_NOTE,
    )
    COMPLAINT_VIEW_STATISTICS = PermissionData(
        name="View Complaint Statistics",
        description="Permission to view complaint statistics and analytics",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.VIEW_STATISTICS,
    )
    COMPLAINT_EXPORT_REPORTS = PermissionData(
        name="Export Complaint Reports",
        description="Permission to export complaint reports",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CONSTITUENT_COMPLAINTS,
        action=PermissionAction.EXPORT_REPORTS,
    )

    # Legal Assistant Permissions
    LEGAL_ASSISTANT_VIEW = PermissionData(
        name="View Legal Assistant",
        description="Permission to view legal assistant features",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.VIEW,
    )
    LEGAL_ASSISTANT_CREATE = PermissionData(
        name="Create Legal Document",
        description="Permission to create new legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.CREATE,
    )
    LEGAL_ASSISTANT_EDIT = PermissionData(
        name="Edit Legal Document",
        description="Permission to edit existing legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.EDIT,
    )
    LEGAL_ASSISTANT_DELETE = PermissionData(
        name="Delete Legal Document",
        description="Permission to delete legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.DELETE,
    )
    LEGAL_ASSISTANT_VIEW_DOCUMENT = PermissionData(
        name="View Legal Document",
        description="Permission to view legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.VIEW_DOCUMENT,
    )
    LEGAL_ASSISTANT_CREATE_DOCUMENT = PermissionData(
        name="Create Legal Document",
        description="Permission to create new legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.CREATE_DOCUMENT,
    )
    LEGAL_ASSISTANT_EDIT_DOCUMENT = PermissionData(
        name="Edit Legal Document",
        description="Permission to edit existing legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.EDIT_DOCUMENT,
    )
    LEGAL_ASSISTANT_DELETE_DOCUMENT = PermissionData(
        name="Delete Legal Document",
        description="Permission to delete legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.DELETE_DOCUMENT,
    )
    LEGAL_ASSISTANT_DOWNLOAD_DOCUMENT = PermissionData(
        name="Download Legal Document",
        description="Permission to download legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.DOWNLOAD_DOCUMENT,
    )
    LEGAL_ASSISTANT_PREVIEW_DOCUMENT = PermissionData(
        name="Preview Legal Document",
        description="Permission to preview legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.PREVIEW_DOCUMENT,
    )
    LEGAL_ASSISTANT_ASK_QUESTIONS = PermissionData(
        name="Ask Legal Questions",
        description="Permission to ask questions to the legal assistant",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.ASK_QUESTIONS,
    )
    LEGAL_ASSISTANT_VIEW_STATISTICS = PermissionData(
        name="View Legal Statistics",
        description="Permission to view legal assistant statistics",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.VIEW_STATISTICS,
    )
    LEGAL_ASSISTANT_APPLY_FILTERS = PermissionData(
        name="Apply Legal Filters",
        description="Permission to apply filters to legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.APPLY_FILTERS,
    )
    LEGAL_ASSISTANT_MANAGE_DOCUMENTS = PermissionData(
        name="Manage Legal Documents",
        description="Permission to manage legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_DOCUMENTS,
    )
    LEGAL_ASSISTANT_MANAGE_CONTAINERS = PermissionData(
        name="Manage Legal Containers",
        description="Permission to manage legal document containers",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_CONTAINERS,
    )
    LEGAL_ASSISTANT_MANAGE_DATA_SOURCES = PermissionData(
        name="Manage Legal Data Sources",
        description="Permission to manage legal data sources",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_DATA_SOURCES,
    )
    LEGAL_ASSISTANT_MANAGE_INSTRUCTIONS = PermissionData(
        name="Manage Legal Instructions",
        description="Permission to manage legal instructions",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_INSTRUCTIONS,
    )
    LEGAL_ASSISTANT_MANAGE_TOOLS = PermissionData(
        name="Manage Legal Tools",
        description="Permission to manage legal tools",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_TOOLS,
    )
    LEGAL_ASSISTANT_MANAGE_TRIGGERS = PermissionData(
        name="Manage Legal Triggers",
        description="Permission to manage legal triggers",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MANAGE_TRIGGERS,
    )
    LEGAL_ASSISTANT_OPERATE = PermissionData(
        name="Operate Legal Assistant",
        description="Permission to operate the legal assistant",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.OPERATE,
    )
    LEGAL_ASSISTANT_MODIFY_PUBLISHED = PermissionData(
        name="Modify Published Legal Documents",
        description="Permission to modify published legal documents",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.MODIFY_PUBLISHED,
    )
    LEGAL_ASSISTANT_INITIALIZE = PermissionData(
        name="Initialize Legal Assistant",
        description="Permission to initialize the legal assistant",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.INITIALIZE,
    )
    LEGAL_ASSISTANT_ACCESS_SHAREPOINT = PermissionData(
        name="Access Legal SharePoint",
        description="Permission to access legal SharePoint",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.ACCESS_SHAREPOINT,
    )
    LEGAL_ASSISTANT_ACCESS_AZURE_STORAGE = PermissionData(
        name="Access Legal Azure Storage",
        description="Permission to access legal Azure storage",
        module=PermissionModule.LEGAL_ASSISTANT,
        resource=PermissionResource.LEGAL_ASSISTANT,
        action=PermissionAction.ACCESS_AZURE_STORAGE,
    )

    # Contract Analysis Permissions
    CONTRACT_VIEW = PermissionData(
        name="View Contracts",
        description="Permission to view contracts in the system",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT,
        action=PermissionAction.VIEW,
    )
    CONTRACT_CREATE = PermissionData(
        name="Create Contract",
        description="Permission to create new contracts",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT,
        action=PermissionAction.CREATE,
    )
    CONTRACT_EDIT = PermissionData(
        name="Edit Contract",
        description="Permission to edit existing contract information",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT,
        action=PermissionAction.EDIT,
    )
    CONTRACT_DELETE = PermissionData(
        name="Delete Contract",
        description="Permission to delete contracts from the system",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT,
        action=PermissionAction.DELETE,
    )
    CONTRACT_ANALYSIS_VIEW_DASHBOARD = PermissionData(
        name="View Analysis Dashboard",
        description="Permission to view the contract analysis dashboard",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_ANALYSIS,
        action=PermissionAction.VIEW_DASHBOARD,
    )
    CONTRACT_ANALYSIS_VIEW_INSIGHTS = PermissionData(
        name="View Analysis Insights",
        description="Permission to view AI-generated insights and analysis",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_ANALYSIS,
        action=PermissionAction.VIEW_INSIGHTS,
    )
    CONTRACT_ANALYSIS_RUN_ANALYSIS = PermissionData(
        name="Run Analysis",
        description="Permission to initiate AI analysis on contracts",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_ANALYSIS,
        action=PermissionAction.RUN_ANALYSIS,
    )

    # Audit Permissions
    AUDIT_CREATE = PermissionData(
        name="Create Audit",
        description="Permission to create new contract audits",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AUDIT,
        action=PermissionAction.CREATE,
    )
    AUDIT_VIEW = PermissionData(
        name="View Audit",
        description="Permission to view audit information and results",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AUDIT,
        action=PermissionAction.VIEW,
    )
    AUDIT_EDIT = PermissionData(
        name="Edit Audit",
        description="Permission to modify audit criteria and settings",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AUDIT,
        action=PermissionAction.EDIT,
    )
    AUDIT_DELETE = PermissionData(
        name="Delete Audit",
        description="Permission to delete audit data",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AUDIT,
        action=PermissionAction.DELETE,
    )
    AUDIT_GENERATE_REPORT = PermissionData(
        name="Generate Audit Report",
        description="Permission to generate audit reports",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AUDIT,
        action=PermissionAction.GENERATE_REPORT,
    )

    # RFP Permissions
    RFP_CREATE = PermissionData(
        name="Create RFP",
        description="Permission to create new RFP documents",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.RFP,
        action=PermissionAction.CREATE,
    )
    RFP_VIEW = PermissionData(
        name="View RFP",
        description="Permission to view RFP information",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.RFP,
        action=PermissionAction.VIEW,
    )
    RFP_EDIT = PermissionData(
        name="Edit RFP",
        description="Permission to edit RFP documents",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.RFP,
        action=PermissionAction.EDIT,
    )
    RFP_DELETE = PermissionData(
        name="Delete RFP",
        description="Permission to delete RFP documents",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.RFP,
        action=PermissionAction.DELETE,
    )
    RFP_PUBLISH = PermissionData(
        name="Publish RFP",
        description="Permission to publish an RFP",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.RFP,
        action=PermissionAction.PUBLISH,
    )

    # Financial Analytics Permissions
    FINANCIAL_ANALYTICS_VIEW = PermissionData(
        name="View Financial Analytics",
        description="Permission to view financial trends and analytics",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.FINANCIAL_ANALYTICS,
        action=PermissionAction.VIEW,
    )

    # Department Distribution Permissions
    DEPARTMENT_DISTRIBUTION_VIEW = PermissionData(
        name="View Department Distribution",
        description="Permission to view department distribution data",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.DEPARTMENT_DISTRIBUTION,
        action=PermissionAction.VIEW,
    )

    # Contract Filters Permissions
    CONTRACT_FILTERS_MANAGE = PermissionData(
        name="Manage Contract Filters",
        description="Permission to create and apply filters to contract views",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_FILTERS,
        action=PermissionAction.MANAGE,
    )

    # Vendor Performance Permissions
    VENDOR_PERFORMANCE_VIEW = PermissionData(
        name="View Vendor Performance",
        description="Permission to view vendor performance comparison data",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.VENDOR_PERFORMANCE,
        action=PermissionAction.VIEW,
    )

    # Contract Note Permissions
    CONTRACT_NOTE_VIEW = PermissionData(
        name="View Contract Notes",
        description="Permission to create notes for contracts",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_NOTE,
        action=PermissionAction.VIEW,
    )
    CONTRACT_NOTE_EDIT = PermissionData(
        name="Edit Contract Notes",
        description="Permission to edit contract notes",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_NOTE,
        action=PermissionAction.EDIT,
    )
    CONTRACT_NOTE_DELETE = PermissionData(
        name="Delete Contract Notes",
        description="Permission to delete contract notes",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_NOTE,
        action=PermissionAction.DELETE,
    )

    # Contract Document Permissions
    CONTRACT_DOCUMENT_UPLOAD = PermissionData(
        name="Upload Contract Documents",
        description="Permission to upload documents related to contracts",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_DOCUMENT,
        action=PermissionAction.UPLOAD,
    )
    CONTRACT_DOCUMENT_VIEW = PermissionData(
        name="View Contract Documents",
        description="Permission to view uploaded contract documents",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_DOCUMENT,
        action=PermissionAction.VIEW,
    )
    CONTRACT_DOCUMENT_DELETE = PermissionData(
        name="Delete Contract Documents",
        description="Permission to delete contract documents",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.CONTRACT_DOCUMENT,
        action=PermissionAction.DELETE,
    )

    # Analysis Permissions
    NETWORK_ANALYSIS_VIEW = PermissionData(
        name="View Network Analysis",
        description="Permission to view network analysis insights",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.NETWORK_ANALYSIS,
        action=PermissionAction.VIEW,
    )
    PREDICTIVE_ANALYSIS_VIEW = PermissionData(
        name="View Predictive Analysis",
        description="Permission to view predictive analysis insights",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.PREDICTIVE_ANALYSIS,
        action=PermissionAction.VIEW,
    )
    ANOMALY_DETECTION_VIEW = PermissionData(
        name="View Anomaly Detection",
        description="Permission to view anomaly detection results",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.ANOMALY_DETECTION,
        action=PermissionAction.VIEW,
    )
    UTILIZATION_ASSESSMENT_VIEW = PermissionData(
        name="View Utilization Assessment",
        description="Permission to view utilization assessment data",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.UTILIZATION_ASSESSMENT,
        action=PermissionAction.VIEW,
    )
    AI_INSIGHTS_VIEW = PermissionData(
        name="View AI Insights",
        description="Permission to view AI-generated insights",
        module=PermissionModule.CONTRACT_ANALYSIS,
        resource=PermissionResource.AI_INSIGHTS,
        action=PermissionAction.VIEW,
    )

    # Permit Processing Permissions
    PERMIT_PROCESS_VIEW = PermissionData(
        name="View Permit Process",
        description="Permission to view permit processing information",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_PROCESS,
        action=PermissionAction.VIEW,
    )
    PERMIT_PROCESS_CREATE = PermissionData(
        name="Create Permit Process",
        description="Permission to create new permit processes",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_PROCESS,
        action=PermissionAction.CREATE,
    )
    PERMIT_PROCESS_EDIT = PermissionData(
        name="Edit Permit Process",
        description="Permission to edit existing permit processes",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_PROCESS,
        action=PermissionAction.EDIT,
    )
    PERMIT_PROCESS_DELETE = PermissionData(
        name="Delete Permit Process",
        description="Permission to delete permit processes",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_PROCESS,
        action=PermissionAction.DELETE,
    )

    # Permit Criteria Permissions
    PERMIT_CRITERIA_VIEW = PermissionData(
        name="View Permit Criteria",
        description="Permission to view permit criteria",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_CRITERIA,
        action=PermissionAction.VIEW,
    )
    PERMIT_CRITERIA_CREATE = PermissionData(
        name="Create Permit Criteria",
        description="Permission to create new permit criteria",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_CRITERIA,
        action=PermissionAction.CREATE,
    )
    PERMIT_CRITERIA_EDIT = PermissionData(
        name="Edit Permit Criteria",
        description="Permission to edit existing permit criteria",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_CRITERIA,
        action=PermissionAction.EDIT,
    )
    PERMIT_CRITERIA_DELETE = PermissionData(
        name="Delete Permit Criteria",
        description="Permission to delete permit criteria",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_CRITERIA,
        action=PermissionAction.DELETE,
    )

    # Permit Template Permissions
    PERMIT_TEMPLATE_VIEW = PermissionData(
        name="View Permit Template",
        description="Permission to view permit templates",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_TEMPLATE,
        action=PermissionAction.VIEW,
    )
    PERMIT_TEMPLATE_CREATE = PermissionData(
        name="Create Permit Template",
        description="Permission to create new permit templates",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_TEMPLATE,
        action=PermissionAction.CREATE,
    )
    PERMIT_TEMPLATE_EDIT = PermissionData(
        name="Edit Permit Template",
        description="Permission to edit existing permit templates",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_TEMPLATE,
        action=PermissionAction.EDIT,
    )
    PERMIT_TEMPLATE_DELETE = PermissionData(
        name="Delete Permit Template",
        description="Permission to delete permit templates",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_TEMPLATE,
        action=PermissionAction.DELETE,
    )

    # Permit Field Permissions
    PERMIT_FIELD_VIEW = PermissionData(
        name="View Permit Field",
        description="Permission to view permit fields",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD,
        action=PermissionAction.VIEW,
    )
    PERMIT_FIELD_CREATE = PermissionData(
        name="Create Permit Field",
        description="Permission to create new permit fields",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD,
        action=PermissionAction.CREATE,
    )
    PERMIT_FIELD_EDIT = PermissionData(
        name="Edit Permit Field",
        description="Permission to edit existing permit fields",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD,
        action=PermissionAction.EDIT,
    )
    PERMIT_FIELD_DELETE = PermissionData(
        name="Delete Permit Field",
        description="Permission to delete permit fields",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD,
        action=PermissionAction.DELETE,
    )

    # Permit Integration Permissions
    PERMIT_INTEGRATION_VIEW = PermissionData(
        name="View Permit Integration",
        description="Permission to view permit integrations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_INTEGRATION,
        action=PermissionAction.VIEW,
    )
    PERMIT_INTEGRATION_CREATE = PermissionData(
        name="Create Permit Integration",
        description="Permission to create new permit integrations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_INTEGRATION,
        action=PermissionAction.CREATE,
    )
    PERMIT_INTEGRATION_EDIT = PermissionData(
        name="Edit Permit Integration",
        description="Permission to edit existing permit integrations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_INTEGRATION,
        action=PermissionAction.EDIT,
    )
    PERMIT_INTEGRATION_DELETE = PermissionData(
        name="Delete Permit Integration",
        description="Permission to delete permit integrations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_INTEGRATION,
        action=PermissionAction.DELETE,
    )

    # Permit Evaluation Permissions
    PERMIT_EVALUATION_VIEW = PermissionData(
        name="View Permit Evaluation",
        description="Permission to view permit evaluations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EVALUATION,
        action=PermissionAction.VIEW,
    )
    PERMIT_EVALUATION_CREATE = PermissionData(
        name="Create Permit Evaluation",
        description="Permission to create new permit evaluations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EVALUATION,
        action=PermissionAction.CREATE,
    )
    PERMIT_EVALUATION_EDIT = PermissionData(
        name="Edit Permit Evaluation",
        description="Permission to edit existing permit evaluations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EVALUATION,
        action=PermissionAction.EDIT,
    )
    PERMIT_EVALUATION_DELETE = PermissionData(
        name="Delete Permit Evaluation",
        description="Permission to delete permit evaluations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EVALUATION,
        action=PermissionAction.DELETE,
    )

    # Permit Notification Permissions
    PERMIT_NOTIFICATION_VIEW = PermissionData(
        name="View Permit Notification",
        description="Permission to view permit notifications",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_NOTIFICATION,
        action=PermissionAction.VIEW,
    )
    PERMIT_NOTIFICATION_CREATE = PermissionData(
        name="Create Permit Notification",
        description="Permission to create new permit notifications",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_NOTIFICATION,
        action=PermissionAction.CREATE,
    )
    PERMIT_NOTIFICATION_EDIT = PermissionData(
        name="Edit Permit Notification",
        description="Permission to edit existing permit notifications",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_NOTIFICATION,
        action=PermissionAction.EDIT,
    )
    PERMIT_NOTIFICATION_DELETE = PermissionData(
        name="Delete Permit Notification",
        description="Permission to delete permit notifications",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_NOTIFICATION,
        action=PermissionAction.DELETE,
    )

    # Permit Dashboard Permissions
    PERMIT_DASHBOARD_VIEW = PermissionData(
        name="View Permit Dashboard",
        description="Permission to view permit dashboard",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_DASHBOARD,
        action=PermissionAction.VIEW,
    )

    # Permit Determination Permissions
    PERMIT_DETERMINATION_VIEW = PermissionData(
        name="View Permit Determination",
        description="Permission to view permit determinations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_DETERMINATION,
        action=PermissionAction.VIEW,
    )
    PERMIT_DETERMINATION_CREATE = PermissionData(
        name="Create Permit Determination",
        description="Permission to create new permit determinations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_DETERMINATION,
        action=PermissionAction.CREATE,
    )
    PERMIT_DETERMINATION_EDIT = PermissionData(
        name="Edit Permit Determination",
        description="Permission to edit existing permit determinations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_DETERMINATION,
        action=PermissionAction.EDIT,
    )
    PERMIT_DETERMINATION_DELETE = PermissionData(
        name="Delete Permit Determination",
        description="Permission to delete permit determinations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_DETERMINATION,
        action=PermissionAction.DELETE,
    )

    # Permit Field API Permissions
    PERMIT_FIELD_API_VIEW = PermissionData(
        name="View Permit Field API",
        description="Permission to view permit field API",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD_API,
        action=PermissionAction.VIEW,
    )
    PERMIT_FIELD_API_CREATE = PermissionData(
        name="Create Permit Field API",
        description="Permission to create new permit field API",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD_API,
        action=PermissionAction.CREATE,
    )
    PERMIT_FIELD_API_EDIT = PermissionData(
        name="Edit Permit Field API",
        description="Permission to edit existing permit field API",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD_API,
        action=PermissionAction.EDIT,
    )
    PERMIT_FIELD_API_DELETE = PermissionData(
        name="Delete Permit Field API",
        description="Permission to delete permit field API",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_FIELD_API,
        action=PermissionAction.DELETE,
    )

    # Permit Audit Permissions
    PERMIT_AUDIT_VIEW = PermissionData(
        name="View Permit Audit",
        description="Permission to view permit audits",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_AUDIT,
        action=PermissionAction.VIEW,
    )
    PERMIT_AUDIT_CREATE = PermissionData(
        name="Create Permit Audit",
        description="Permission to create new permit audits",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_AUDIT,
        action=PermissionAction.CREATE,
    )
    PERMIT_AUDIT_EDIT = PermissionData(
        name="Edit Permit Audit",
        description="Permission to edit existing permit audits",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_AUDIT,
        action=PermissionAction.EDIT,
    )
    PERMIT_AUDIT_DELETE = PermissionData(
        name="Delete Permit Audit",
        description="Permission to delete permit audits",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_AUDIT,
        action=PermissionAction.DELETE,
    )

    # Permit Report Permissions
    PERMIT_REPORT_VIEW = PermissionData(
        name="View Permit Report",
        description="Permission to view permit reports",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_REPORT,
        action=PermissionAction.VIEW,
    )
    PERMIT_REPORT_CREATE = PermissionData(
        name="Create Permit Report",
        description="Permission to create new permit reports",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_REPORT,
        action=PermissionAction.CREATE,
    )
    PERMIT_REPORT_EDIT = PermissionData(
        name="Edit Permit Report",
        description="Permission to edit existing permit reports",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_REPORT,
        action=PermissionAction.EDIT,
    )
    PERMIT_REPORT_DELETE = PermissionData(
        name="Delete Permit Report",
        description="Permission to delete permit reports",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_REPORT,
        action=PermissionAction.DELETE,
    )

    # Permit Explanation Permissions
    PERMIT_EXPLANATION_VIEW = PermissionData(
        name="View Permit Explanation",
        description="Permission to view permit explanations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EXPLANATION,
        action=PermissionAction.VIEW,
    )
    PERMIT_EXPLANATION_CREATE = PermissionData(
        name="Create Permit Explanation",
        description="Permission to create new permit explanations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EXPLANATION,
        action=PermissionAction.CREATE,
    )
    PERMIT_EXPLANATION_EDIT = PermissionData(
        name="Edit Permit Explanation",
        description="Permission to edit existing permit explanations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EXPLANATION,
        action=PermissionAction.EDIT,
    )
    PERMIT_EXPLANATION_DELETE = PermissionData(
        name="Delete Permit Explanation",
        description="Permission to delete permit explanations",
        module=PermissionModule.PERMIT_PROCESSING,
        resource=PermissionResource.PERMIT_EXPLANATION,
        action=PermissionAction.DELETE,
    )

    # Email Process Permissions
    EMAIL_PROCESS_FETCH = PermissionData(
        name="Fetch Emails",
        description="Permission to Logged in user to fetch emails from outlook by Microsoft token",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.FETCH,
    )
    EMAIL_PROCESS_CREATE_DRAFT = PermissionData(
        name="Create Draft",
        description="Permission to Create Draft by AI",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.CREATE_DRAFT,
    )
    EMAIL_PROCESS_SEND_DRAFT = PermissionData(
        name="Send Draft",
        description="Permission to Send Draft after editing to the email sender",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.SEND_DRAFT,
    )
    EMAIL_PROCESS_EDIT_SETTINGS = PermissionData(
        name="Edit Email Settings",
        description="Permission to Email Settings include CRUD operations in Departments, Assign Member, Timmer, Knowledge",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.EDIT_EMAIL_SETTINGS,
    )
    EMAIL_PROCESS_REASSIGN_DEPT_TEAM = PermissionData(
        name="Reassign Department Team",
        description="Permission to Reassign department and their associated team member",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.REASSIGN_DEPT_TEAM,
    )
    EMAIL_PROCESS_VIEW_QUEUE = PermissionData(
        name="View Email Queue",
        description="Permission to view the email processing queue with pending emails",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.VIEW_EMAIL_QUEUE,
    )
    EMAIL_PROCESS_FILTER_EMAILS = PermissionData(
        name="Filter Emails",
        description="Permission to filter and search emails in the processing queue",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.FILTER_EMAILS,
    )
    EMAIL_PROCESS_UPDATE_DRAFT = PermissionData(
        name="Update Draft",
        description="Permission to update an existing AI-generated draft response",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.UPDATE_DRAFT,
    )
    EMAIL_PROCESS_MANAGE_DEPARTMENTS = PermissionData(
        name="Manage Departments",
        description="Permission to create, edit, and delete departments for email routing",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.MANAGE_DEPARTMENTS,
    )
    EMAIL_PROCESS_MANAGE_CATEGORIES = PermissionData(
        name="Manage Categories",
        description="Permission to add and manage categories within departments",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.MANAGE_CATEGORIES,
    )
    EMAIL_PROCESS_MANAGE_TEAM_MEMBERS = PermissionData(
        name="Manage Team Members",
        description="Permission to add, edit, and remove team members for email handling",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.MANAGE_TEAM_MEMBERS,
    )
    EMAIL_PROCESS_MANAGE_REMINDERS = PermissionData(
        name="Manage Reminders",
        description="Permission to configure response time thresholds and reminder settings",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.MANAGE_REMINDERS,
    )
    EMAIL_PROCESS_MANAGE_KNOWLEDGE_BASE = PermissionData(
        name="Manage Knowledge Base",
        description="Permission to connect and manage knowledge base resources for AI responses",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.EMAIL_PROCESS,
        action=PermissionAction.MANAGE_KNOWLEDGE_BASE,
    )

    # EPAR Permissions
    PAR_VIEW = PermissionData(
        name="View PAR PM",
        description="Access to view PAR details in read-only mode",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.VIEW_PAR,
    )
    PAR_EDIT = PermissionData(
        name="Edit PAR PM",
        description="Ability to update existing PAR information",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.EDIT_PAR,
    )
    PAR_CREATE = PermissionData(
        name="Create PAR",
        description="Ability to initiate new PARs in the system",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.PM_CREATE_PAR,
    )
    PAR_DOWNLOAD = PermissionData(
        name="Download PAR PM",
        description="Export PAR details as CSV/Excel file",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.DOWNLOAD_PAR,
    )

    # Integration Permissions
    PAR_SUBMIT_TO_PROTRACK = PermissionData(
        name="Submit to Protrack",
        description="Permission to send completed PARs to Protrack+",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR_PROTRACK_INTEGRATION,
        action=PermissionAction.PM_SUBMIT_PROTRACK,
    )

    # Dashboard Permissions
    PAR_VIEW_STATUS = PermissionData(
        name="View PAR Status",
        description="Access to view current status and history of PARs",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR_DASHBOARD,
        action=PermissionAction.PM_VIEW_STATUS,
    )

    # Notification Permissions
    PAR_RECEIVE_NOTIFICATIONS = PermissionData(
        name="Receive Notifications",
        description="Receive system alerts about PAR status changes",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.NOTIFICATIONS,
        action=PermissionAction.PM_RECEIVE_NOTIFICATIONS,
    )

    # Financial Officer Permissions
    FO_VIEW_PAR = PermissionData(
        name="View PAR FO",
        description="Access to view PAR details including financial sections",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.VIEW_PAR,
    )
    FO_EDIT_PAR = PermissionData(
        name="Edit PAR FO",
        description="Ability to update PAR information including financial details",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.EDIT_PAR,
    )
    FO_PERFORM_RAD = PermissionData(
        name="Perform RAD Review",
        description="Conduct Resource Allocation Division review on PARs",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FINANCIAL_REVIEW,
        action=PermissionAction.FO_PERFORM_RAD,
    )
    FO_RAD_APPROVE = PermissionData(
        name="RAD Approval",
        description="Approve PARs following RAD review",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FINANCIAL_REVIEW,
        action=PermissionAction.FO_RAD_APPROVE,
    )
    FO_PERFORM_OCFO = PermissionData(
        name="Perform OCFO Review",
        description="Conduct Office of Chief Financial Officer review",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FINANCIAL_REVIEW,
        action=PermissionAction.FO_PERFORM_OCFO,
    )
    FO_OCFO_APPROVE = PermissionData(
        name="OCFO Approval",
        description="Authorize PAR following OCFO review",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FINANCIAL_REVIEW,
        action=PermissionAction.FO_OCFO_APPROVE,
    )
    FO_SUBMIT_FHWA = PermissionData(
        name="Submit to FHWA/FMIS",
        description="Forward approved PARs to Federal Highway Administration",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR_FHWA_INTEGRATION,
        action=PermissionAction.FO_SUBMIT_FHWA,
    )
    FO_DOWNLOAD_PAR = PermissionData(
        name="Download PAR FO",
        description="Export PAR details including financial data",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.DOWNLOAD_PAR,
    )

    # Budget Analyst Permissions
    BA_VIEW_PAR = PermissionData(
        name="View PAR BA",
        description="Access to view PAR details with focus on budget sections",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.EPAR,
        action=PermissionAction.VIEW_PAR,
    )
    BA_EDIT_FUNDING_SOURCE = PermissionData(
        name="Edit Funding Source",
        description="Ability to select between Federal/Local funding",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FEDERAL_FUNDING,
        action=PermissionAction.BA_EDIT_FUNDING_SOURCE,
    )
    BA_SET_FUNDING_RATE = PermissionData(
        name="Set Funding Rate",
        description="Select rate options (100%, 90/10, 83.15/16.85, 80/20)",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FEDERAL_FUNDING,
        action=PermissionAction.BA_SET_FUNDING_RATE,
    )
    BA_MANAGE_PROGRAM_CODES = PermissionData(
        name="Manage Program Codes",
        description="Add/edit program codes from FMIS 60 report",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FEDERAL_FUNDING,
        action=PermissionAction.BA_MANAGE_PROGRAM_CODES,
    )
    BA_VIEW_BUDGET_SUMMARY = PermissionData(
        name="View Budget Summary",
        description="Access integrated view of current/requested funding",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_ANALYSIS,
        action=PermissionAction.BA_VIEW_BUDGET_SUMMARY,
    )
    BA_EXPORT_BUDGET = PermissionData(
        name="Export Budget Summary",
        description="Download budget calculations as Excel file",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_ANALYSIS,
        action=PermissionAction.BA_EXPORT_BUDGET,
    )
    BA_SUBMIT_BUDGET_VALIDATION = PermissionData(
        name="Submit Budget for Validation",
        description="Forward calculations to OCFO for verification",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_WORKFLOW,
        action=PermissionAction.BA_SUBMIT_BUDGET_VALIDATION,
    )

    # Budget Validation Officer Permissions
    OBV_VIEW_BUDGET = PermissionData(
        name="View Budget Calculations",
        description="Access to review submitted budget details",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_VALIDATION,
        action=PermissionAction.OBV_VIEW_BUDGET,
    )
    OBV_VALIDATE_CALCULATIONS = PermissionData(
        name="Validate Calculations",
        description="Verify mathematical accuracy of budget allocations",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_VALIDATION,
        action=PermissionAction.OBV_VALIDATE_CALCULATIONS,
    )
    OBV_APPROVE_BUDGET = PermissionData(
        name="Approve Budget",
        description="Authorize budget calculations as valid",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_VALIDATION,
        action=PermissionAction.OBV_APPROVE_BUDGET,
    )
    OBV_REJECT_BUDGET = PermissionData(
        name="Reject Budget",
        description="Return budget for corrections with feedback",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.BUDGET_VALIDATION,
        action=PermissionAction.OBV_REJECT_BUDGET,
    )
    OBV_VIEW_PROGRAM_CODES = PermissionData(
        name="View Program Codes",
        description="Access to FMIS program codes and descriptions",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.FEDERAL_FUNDING,
        action=PermissionAction.OBV_VIEW_PROGRAM_CODES,
    )

    # System Administrator Permissions
    SA_USER_MANAGEMENT = PermissionData(
        name="Manage Users",
        description="Create/edit user accounts and assign roles",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.ADMINISTRATION,
        action=PermissionAction.SA_USER_MANAGEMENT,
    )
    SA_ROLE_MANAGEMENT = PermissionData(
        name="Manage Roles",
        description="Define and modify role permissions",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.ADMINISTRATION,
        action=PermissionAction.SA_ROLE_MANAGEMENT,
    )
    SA_VIEW_AUDIT_LOGS = PermissionData(
        name="View Audit Logs",
        description="Access to system activity and change history",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SECURITY,
        action=PermissionAction.SA_VIEW_AUDIT_LOGS,
    )
    SA_MANAGE_INTEGRATIONS = PermissionData(
        name="Manage Integrations",
        description="Configure connections with external systems",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.SA_MANAGE_INTEGRATIONS,
    )
    SA_SECURITY_SETTINGS = PermissionData(
        name="Manage Security Settings",
        description="Configure encryption, MFA, and other security controls",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SECURITY,
        action=PermissionAction.SA_SECURITY_SETTINGS,
    )
    SA_SYSTEM_MONITORING = PermissionData(
        name="System Monitoring",
        description="View system performance and access reports",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.ADMINISTRATION,
        action=PermissionAction.SA_SYSTEM_MONITORING,
    )

    # API Integration Permissions
    API_PROTRACK_READ = PermissionData(
        name="Protrack Read Access",
        description="Retrieve data from Protrack+",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_PROTRACK_READ,
    )
    API_PROTRACK_WRITE = PermissionData(
        name="Protrack Write Access",
        description="Send data updates to Protrack+",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_PROTRACK_WRITE,
    )
    API_FMIS_READ = PermissionData(
        name="FMIS Read Access",
        description="Retrieve program codes and budget data from FMIS",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_FMIS_READ,
    )
    API_FMIS_WRITE = PermissionData(
        name="FMIS Write Access",
        description="Submit approved PARs to FMIS",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_FMIS_WRITE,
    )
    API_DIFS_READ = PermissionData(
        name="DIFS Read Access",
        description="Retrieve DC funding availability data",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_DIFS_READ,
    )
    API_DIFS_WRITE = PermissionData(
        name="DIFS Write Access",
        description="Send approved allocations to DIFS",
        module=PermissionModule.EDS_EPAR,
        resource=PermissionResource.SYSTEM_INTEGRATION,
        action=PermissionAction.API_DIFS_WRITE,
    )

    RBAC_USER_MANAGEMENT_MANAGE = PermissionData(
        name="User Management",
        description="Manage user accounts and permissions",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.USER_MANAGEMENT,
        action=PermissionAction.MANAGE,
    )
    RBAC_USER_MANAGEMENT_CREATE = PermissionData(
        name="Create User",
        description="Create new user accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.USER_MANAGEMENT,
        action=PermissionAction.CREATE,
    )
    RBAC_USER_MANAGEMENT_EDIT = PermissionData(
        name="Edit User",
        description="Edit existing user accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.USER_MANAGEMENT,
        action=PermissionAction.EDIT,
    )
    RBAC_USER_MANAGEMENT_DELETE = PermissionData(
        name="Delete User",
        description="Delete user accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.USER_MANAGEMENT,
        action=PermissionAction.DELETE,
    )
    RBAC_USER_MANAGEMENT_VIEW = PermissionData(
        name="View User",
        description="View user accounts",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.USER_MANAGEMENT,
        action=PermissionAction.VIEW,
    )


    RBAC_ROLE_MANAGEMENT_MANAGE = PermissionData(
        name="Role Management",
        description="Manage roles and permissions",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.ROLE_MANAGEMENT,
        action=PermissionAction.MANAGE,
    )
    RBAC_ROLE_MANAGEMENT_CREATE = PermissionData(
        name="Create Role",
        description="Create new roles",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.ROLE_MANAGEMENT,
        action=PermissionAction.CREATE,
    )
    RBAC_ROLE_MANAGEMENT_EDIT = PermissionData(
        name="Edit Role",
        description="Edit existing roles",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.ROLE_MANAGEMENT,
        action=PermissionAction.EDIT,
    )
    RBAC_ROLE_MANAGEMENT_DELETE = PermissionData(
        name="Delete Role",
        description="Delete roles",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.ROLE_MANAGEMENT,
        action=PermissionAction.DELETE,
    )
    RBAC_ROLE_MANAGEMENT_VIEW = PermissionData(
        name="View Role",
        description="View roles",
        module=PermissionModule.USER_MANAGEMENT,
        resource=PermissionResource.ROLE_MANAGEMENT,
        action=PermissionAction.VIEW,
    )
    
    # Message Management Permissions
    MESSAGE_MANAGEMENT_VIEW_ALL = PermissionData(
        name="View All Messages",
        description="Permission to view all messages across departments",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_ALL_MESSAGES,
    )
    MESSAGE_MANAGEMENT_VIEW_DEPARTMENT = PermissionData(
        name="View Department Messages",
        description="Permission to view messages within own department",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_DEPARTMENT_MESSAGES,
    )
    MESSAGE_MANAGEMENT_VIEW_OWN = PermissionData(
        name="View Own Messages",
        description="Permission to view own messages",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.MESSAGE_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_OWN_MESSAGES,
    )

    # Department Management Permissions
    DEPARTMENT_MANAGEMENT_VIEW_ALL = PermissionData(
        name="View All Department Data",
        description="Permission to view data from all departments",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_ALL_DEPARTMENT_DATA,
    )
    DEPARTMENT_MANAGEMENT_VIEW_OWN = PermissionData(
        name="View Own Department Data",
        description="Permission to view data from own department",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_OWN_DEPARTMENT_DATA,
    )

    # Channel Specific Permissions
    CHANNEL_SPECIFIC_CONFIGURE_EMAIL = PermissionData(
        name="Configure Email Settings",
        description="Permission to configure email channel settings",
        module=PermissionModule.CONSTITUENT_COMPLAINTS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.CONFIGURE_EMAIL_SETTINGS,
    )

    ADD_KNOWLEDGE_EMAIL_PROCESS = PermissionData(
        name="Add Knowledge",
        description="Permission to add knowledge in department",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.ADD_KNOWLEDGE
    )

    CHANGE_DEPARTMENT_SETTINGS_EMAIL_PROCESS = PermissionData(
        name="Change Department Settings",
        description="Permission to change department settings",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.CHANGE_DEPARTMENT_SETTINGS
    )

    ASSIGN_USERS_TO_DEPARTMENTS_EMAIL_PROCESS = PermissionData(
        name="Assign Users to Departments",
        description="Permission to assign users to departments",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.ASSIGN_USERS_TO_DEPARTMENTS
    )

    ASSIGN_USERS_WITHIN_DEPARTMENT_EMAIL_PROCESS = PermissionData(
        name="Assign Users Within Department",
        description="Permission to assign users within their own department",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.ASSIGN_USERS_WITHIN_DEPARTMENT
    )

    VIEW_ALL_DEPARTMENT_DATA_EMAIL_PROCESS = PermissionData(
        name="View All Department Data",
        description="Permission to view all department data",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_ALL_DEPARTMENT_DATA
    )

    VIEW_OWN_DEPARTMENT_DATA_EMAIL_PROCESS = PermissionData(
        name="View Own Department Data",
        description="Permission to view own department's data",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.VIEW_OWN_DEPARTMENT_DATA
    )

    MANAGE_DEPARTMENT_ROUTING_EMAIL_PROCESS = PermissionData(
        name="Manage Department Routing",
        description="Permission to manage routing settings for departments",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.DEPARTMENT_MANAGEMENT_PERMISSIONS,
        action=PermissionAction.MANAGE_DEPARTMENT_ROUTING
    )

    # System Access Tracking Permissions
    LOGIN_ACCESS_EMAIL_PROCESS = PermissionData(
        name="Login Access",
        description="Permission for login access",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.LOGIN_ACCESS
    )

    FORM_ONLY_ACCESS_EMAIL_PROCESS = PermissionData(
        name="Form Only Access",
        description="Permission to access only forms",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.FORM_ONLY_ACCESS
    )

    TRACK_USER_ACTIONS_EMAIL_PROCESS = PermissionData(
        name="Track User Actions",
        description="Permission to track user actions",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.TRACK_USER_ACTIONS
    )

    GENERATE_ALL_REPORTS_EMAIL_PROCESS = PermissionData(
        name="Generate All Reports",
        description="Permission to generate all reports",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.GENERATE_ALL_REPORTS
    )

    GENERATE_DEPARTMENT_REPORTS_EMAIL_PROCESS = PermissionData(
        name="Generate Department Reports",
        description="Permission to generate department-specific reports",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.GENERATE_DEPARTMENT_REPORTS
    )

    VIEW_ALL_ANALYTICS_EMAIL_PROCESS = PermissionData(
        name="View All Analytics",
        description="Permission to view analytics across the system",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.VIEW_ALL_ANALYTICS
    )

    VIEW_DEPARTMENT_ANALYTICS_EMAIL_PROCESS = PermissionData(
        name="View Department Analytics",
        description="Permission to view department-specific analytics",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.SYSTEM_ACCESS_TRACKING_PERMISSIONS,
        action=PermissionAction.VIEW_DEPARTMENT_ANALYTICS
    )
    VIEW_ENTITY_MANAGER_ENTITY_MANAGER = PermissionData(
        name="View Entity Manager Apps",
        description="Permission to view entity manager apps",
        module=PermissionModule.ENTITY_MANAGER,
        resource=PermissionResource.ENTITY_MANAGER,
        action=PermissionAction.VIEW
    )
    SYNC_EMAILS = PermissionData(
        name="Sync Emails",
        description="Permission to sync emails",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.SYNC_EMAILS
    )

    CONFIGURE_EMAIL_SETTINGS = PermissionData(
        name="Configure Email Settings",
        description="Permission to configure email settings",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.CONFIGURE_EMAIL_SETTINGS
    )

    SEND_EMAIL_RESPONSES = PermissionData(
        name="Send Email Responses",
        description="Permission to send email responses",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.SEND_EMAIL_RESPONSES
    )

    ACCESS_VOICEMAIL_SYSTEM = PermissionData(
        name="Access Voicemail System",
        description="Permission to access voicemail system",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.ACCESS_VOICEMAIL_SYSTEM
    )

    TRANSCRIBE_VOICEMAILS = PermissionData(
        name="Transcribe Voicemails",
        description="Permission to transcribe voicemails",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.TRANSCRIBE_VOICEMAILS
    )

    CALLBACK_CONSTITUENTS = PermissionData(
        name="Callback Constituents",
        description="Permission to callback constituents",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.CALLBACK_CONSTITUENTS
    )

    SCAN_PHYSICAL_MAIL = PermissionData(
        name="Scan Physical Mail",
        description="Permission to scan physical mail",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.SCAN_PHYSICAL_MAIL
    )

    OCR_DOCUMENT_PROCESSING = PermissionData(
        name="OCR Document Processing",
        description="Permission to process documents using OCR",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.OCR_DOCUMENT_PROCESSING
    )

    HANDLE_PHYSICAL_RESPONSES = PermissionData(
        name="Handle Physical Responses",
        description="Permission to handle physical mail responses",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.HANDLE_PHYSICAL_RESPONSES
    )

    CONFIGURE_FORMS = PermissionData(
        name="Configure Forms",
        description="Permission to configure forms",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.CONFIGURE_FORMS
    )

    VIEW_FORM_SUBMISSIONS = PermissionData(
        name="View Form Submissions",
        description="Permission to view form submissions",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.VIEW_FORM_SUBMISSIONS
    )

    SUBMIT_FORMS = PermissionData(
        name="Submit Forms",
        description="Permission to submit forms",
        module=PermissionModule.EMAIL_PROCESS,
        resource=PermissionResource.CHANNEL_SPECIFIC_PERMISSIONS,
        action=PermissionAction.SUBMIT_FORMS
    )


    @classmethod
    def get_all_permissions(cls) -> List[PermissionData]:
        """Get all defined permissions"""
        return [
            value
            for name, value in cls.__dict__.items()
            if isinstance(value, PermissionData)
        ]
