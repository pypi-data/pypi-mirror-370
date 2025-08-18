from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrapperField


class ActiveTaskPseudoDef:
    DATA_TYPE_NAME: str = "ActiveTask"
    ACTIVE_TASK_ID__FIELD_NAME = WrapperField("ActiveTaskId", FieldType.LONG)
    ACTIVE_WORKFLOW_ID__FIELD_NAME = WrapperField("ActiveWorkflowId", FieldType.LONG)
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE)
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING)
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.ENUM)
    TASK_USAGE_ID__FIELD_NAME = WrapperField("TaskUsageId", FieldType.LONG)


class ActiveWorkflowPseudoDef:
    DATA_TYPE_NAME: str = "ActiveWorkflow"
    ACTIVE_WORKFLOW_ID__FIELD_NAME = WrapperField("ActiveWorkflowId", FieldType.LONG)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.STRING)
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING)
    ESTIMATED_ATTACHMENTS__FIELD_NAME = WrapperField("EstimatedAttachments", FieldType.LONG)
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING)
    RELATED_RECORD_ID__FIELD_NAME = WrapperField("RelatedRecordId", FieldType.LONG)
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.ENUM)
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG)


class AuditLogPseudoDef:
    DATA_TYPE_NAME: str = "AuditLog"
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    EVENT_TYPE__FIELD_NAME = WrapperField("EventType", FieldType.ENUM)
    FULL_NAME__FIELD_NAME = WrapperField("FullName", FieldType.STRING)
    NEW_VALUE__FIELD_NAME = WrapperField("NewValue", FieldType.STRING)
    ORIGINAL_VALUE__FIELD_NAME = WrapperField("OriginalValue", FieldType.STRING)
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG)
    RECORD_NAME__FIELD_NAME = WrapperField("RecordName", FieldType.STRING)
    TIME_STAMP__FIELD_NAME = WrapperField("TimeStamp", FieldType.DATE)
    USER_COMMENT__FIELD_NAME = WrapperField("UserComment", FieldType.STRING)
    USER_NAME__FIELD_NAME = WrapperField("UserName", FieldType.STRING)


class DataFieldDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "DataFieldDefinition"
    APPROVE_EDIT__FIELD_NAME = WrapperField("ApproveEdit", FieldType.BOOLEAN)
    AUTO_CLEAR_FIELD_LIST__FIELD_NAME = WrapperField("AutoClearFieldList", FieldType.STRING)
    AUTO_SORT__FIELD_NAME = WrapperField("AutoSort", FieldType.BOOLEAN)
    COLOR_MAPPING_ID__FIELD_NAME = WrapperField("ColorMappingId", FieldType.LONG)
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING)
    DATA_FIELD_TAG__FIELD_NAME = WrapperField("DataFieldTag", FieldType.STRING)
    DATA_FIELD_TYPE__FIELD_NAME = WrapperField("DataFieldType", FieldType.STRING)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DECIMAL_DIGITS__FIELD_NAME = WrapperField("DecimalDigits", FieldType.INTEGER)
    DEFAULT_VALUE__FIELD_NAME = WrapperField("DefaultValue", FieldType.STRING)
    DEPENDENT_FIELDS__FIELD_NAME = WrapperField("Dependent_Fields", FieldType.STRING)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    DIRECT_EDIT__FIELD_NAME = WrapperField("DirectEdit", FieldType.BOOLEAN)
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING)
    EDITABLE__FIELD_NAME = WrapperField("Editable", FieldType.BOOLEAN)
    ENUM_VALUES__FIELD_NAME = WrapperField("EnumValues", FieldType.STRING)
    FORM_COL__FIELD_NAME = WrapperField("FormCol", FieldType.SHORT)
    FORM_COL_SPAN__FIELD_NAME = WrapperField("FormColSpan", FieldType.SHORT)
    FORM_NAME__FIELD_NAME = WrapperField("FormName", FieldType.STRING)
    HTML_EDITOR__FIELD_NAME = WrapperField("HtmlEditor", FieldType.BOOLEAN)
    IDENTIFIER__FIELD_NAME = WrapperField("Identifier", FieldType.BOOLEAN)
    INDEX_FOR_SEARCH__FIELD_NAME = WrapperField("IndexForSearch", FieldType.BOOLEAN)
    LINK_OUT__FIELD_NAME = WrapperField("LinkOut", FieldType.BOOLEAN)
    LINK_OUT_URL__FIELD_NAME = WrapperField("LinkOutUrl", FieldType.BOOLEAN)
    MAX_LENGTH__FIELD_NAME = WrapperField("MaxLength", FieldType.INTEGER)
    MAXIMUM_VALUE__FIELD_NAME = WrapperField("MaximumValue", FieldType.DOUBLE)
    MINIMUM_VALUE__FIELD_NAME = WrapperField("MinimumValue", FieldType.DOUBLE)
    MULT_SELECT__FIELD_NAME = WrapperField("MultSelect", FieldType.BOOLEAN)
    NUM_LINES__FIELD_NAME = WrapperField("NumLines", FieldType.INTEGER)
    REQUIRED__FIELD_NAME = WrapperField("Required", FieldType.BOOLEAN)
    SORT_KEY__FIELD_NAME = WrapperField("SortKey", FieldType.BOOLEAN)
    STATIC_DATE__FIELD_NAME = WrapperField("StaticDate", FieldType.BOOLEAN)
    UNIQUE_VALUE__FIELD_NAME = WrapperField("UniqueValue", FieldType.BOOLEAN)
    VISIBLE__FIELD_NAME = WrapperField("Visible", FieldType.BOOLEAN)
    WORKFLOW_ONLY_EDITING__FIELD_NAME = WrapperField("WorkflowOnlyEditing", FieldType.BOOLEAN)


class DataTypeDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "DataTypeDefinition"
    ADDABLE__FIELD_NAME = WrapperField("Addable", FieldType.BOOLEAN)
    ATTACHMENT__FIELD_NAME = WrapperField("Attachment", FieldType.BOOLEAN)
    ATTACHMENT_TYPE__FIELD_NAME = WrapperField("AttachmentType", FieldType.STRING)
    DATA_TYPE_TAG__FIELD_NAME = WrapperField("DATA_TYPE_TAG", FieldType.STRING)
    DATA_TYPE_ID__FIELD_NAME = WrapperField("DataTypeId", FieldType.LONG)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DELETABLE__FIELD_NAME = WrapperField("Deletable", FieldType.BOOLEAN)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING)
    EXTENSION_TYPE__FIELD_NAME = WrapperField("ExtensionType", FieldType.BOOLEAN)
    GROUP_ADDABLE__FIELD_NAME = WrapperField("GroupAddable", FieldType.BOOLEAN)
    HIDE_DATA_RECORDS__FIELD_NAME = WrapperField("HideDataRecords", FieldType.BOOLEAN)
    HIGH_VOLUME__FIELD_NAME = WrapperField("HighVolume", FieldType.BOOLEAN)
    IS_HIDE_IN_MOBILE__FIELD_NAME = WrapperField("IS_HIDE_IN_MOBILE", FieldType.BOOLEAN)
    IS_HVDT_ON_SAVE_ENABLED__FIELD_NAME = WrapperField("IS_HVDT_ON_SAVE_ENABLED", FieldType.BOOLEAN)
    IS_PUBLIC_ATTACHMENT__FIELD_NAME = WrapperField("IS_PUBLIC_ATTACHMENT", FieldType.BOOLEAN)
    ICON_COLOR__FIELD_NAME = WrapperField("IconColor", FieldType.STRING)
    ICON_NAME__FIELD_NAME = WrapperField("IconName", FieldType.STRING)
    IMPORTABLE__FIELD_NAME = WrapperField("Importable", FieldType.BOOLEAN)
    IS_ACTIVE__FIELD_NAME = WrapperField("IsActive", FieldType.BOOLEAN)
    IS_HIDDEN__FIELD_NAME = WrapperField("IsHidden", FieldType.BOOLEAN)
    MAX_TABLE_ROW_COUNT__FIELD_NAME = WrapperField("MaxTableRowCount", FieldType.LONG)
    PLURAL_DISPLAY_NAME__FIELD_NAME = WrapperField("PluralDisplayName", FieldType.STRING)
    RECORD_ASSIGNABLE__FIELD_NAME = WrapperField("RecordAssignable", FieldType.BOOLEAN)
    RECORD_IMAGE_ASSIGNABLE__FIELD_NAME = WrapperField("RecordImageAssignable", FieldType.BOOLEAN)
    RECORD_IMAGE_MANUALLY_ADDABLE__FIELD_NAME = WrapperField("RecordImageManuallyAddable", FieldType.BOOLEAN)
    REMOVABLE__FIELD_NAME = WrapperField("Removable", FieldType.BOOLEAN)
    RESTRICTED__FIELD_NAME = WrapperField("Restricted", FieldType.BOOLEAN)
    SHOW_ON_HOME_SCREEN__FIELD_NAME = WrapperField("ShowOnHomeScreen", FieldType.BOOLEAN)
    SHOW_SUB_TABLES__FIELD_NAME = WrapperField("ShowSubTables", FieldType.BOOLEAN)
    SHOW_TABS__FIELD_NAME = WrapperField("ShowTabs", FieldType.BOOLEAN)
    SINGLE_PARENT__FIELD_NAME = WrapperField("SingleParent", FieldType.BOOLEAN)
    UNDER_CONTAINER__FIELD_NAME = WrapperField("UnderContainer", FieldType.BOOLEAN)


class EnbDataTypeDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "EnbDataTypeDefinition"
    DATA_TYPE_ID__FIELD_NAME = WrapperField("DataTypeId", FieldType.LONG)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING)
    ENB_DATA_TYPE_NAME__FIELD_NAME = WrapperField("EnbDataTypeName", FieldType.STRING)
    ICON_COLOR__FIELD_NAME = WrapperField("IconColor", FieldType.STRING)
    ICON_NAME__FIELD_NAME = WrapperField("IconName", FieldType.STRING)
    NOTEBOOK_EXPERIMENT_ID__FIELD_NAME = WrapperField("Notebook_Experiment_ID", FieldType.LONG)
    PLURAL_DISPLAY_NAME__FIELD_NAME = WrapperField("PluralDisplayName", FieldType.STRING)


class EnbEntryPseudoDef:
    DATA_TYPE_NAME: str = "EnbEntry"
    APPROVAL_DUE_DATE__FIELD_NAME = WrapperField("ApprovalDueDate", FieldType.DATE)
    COLUMN_ORDER__FIELD_NAME = WrapperField("ColumnOrder", FieldType.INTEGER)
    COLUMN_SPAN__FIELD_NAME = WrapperField("ColumnSpan", FieldType.INTEGER)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    DEPENDENT_ENTRY_ID_LIST__FIELD_NAME = WrapperField("DependentEntryIdList", FieldType.STRING)
    ENTRY_DESCRIPTION__FIELD_NAME = WrapperField("EntryDescription", FieldType.STRING)
    ENTRY_HEIGHT__FIELD_NAME = WrapperField("EntryHeight", FieldType.INTEGER)
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG)
    ENTRY_NAME__FIELD_NAME = WrapperField("EntryName", FieldType.STRING)
    ENTRY_ORDER__FIELD_NAME = WrapperField("EntryOrder", FieldType.INTEGER)
    ENTRY_REQUIRES_E_SIGN__FIELD_NAME = WrapperField("EntryRequiresESign", FieldType.BOOLEAN)
    ENTRY_SINGLETON_ID__FIELD_NAME = WrapperField("EntrySingletonId", FieldType.STRING)
    ENTRY_STATUS__FIELD_NAME = WrapperField("EntryStatus", FieldType.STRING)
    ENTRY_TYPE__FIELD_NAME = WrapperField("EntryType", FieldType.STRING)
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG)
    HAS_COMMENTS__FIELD_NAME = WrapperField("HasComments", FieldType.BOOLEAN)
    IS_CREATED_FROM_TEMPLATE__FIELD_NAME = WrapperField("IsCreatedFromTemplate", FieldType.BOOLEAN)
    IS_REQUIRED_ENTRY__FIELD_NAME = WrapperField("IsRequiredEntry", FieldType.BOOLEAN)
    IS_SHOWN_IN_TEMPLATE__FIELD_NAME = WrapperField("IsShownInTemplate", FieldType.BOOLEAN)
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING)
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.DATE)
    RELATED_ENTRY_ID_LIST__FIELD_NAME = WrapperField("RelatedEntryIdList", FieldType.STRING)
    REQUIRES_GRABBER_PLUGIN__FIELD_NAME = WrapperField("RequriesGrabberPlugin", FieldType.BOOLEAN)
    SOURCE_ENTRY_ID__FIELD_NAME = WrapperField("SourceEntryId", FieldType.LONG)
    SUBMITTED_BY__FIELD_NAME = WrapperField("SubmittedBy", FieldType.STRING)
    SUBMITTED_DATE__FIELD_NAME = WrapperField("SubmittedDate", FieldType.DATE)
    TAB_ID__FIELD_NAME = WrapperField("TabId", FieldType.LONG)
    TEMPLATE_ITEM_FULFILLED_TIME_STAMP__FIELD_NAME = WrapperField("TemplateItemFulfilledTimeStamp", FieldType.LONG)


class EnbEntryOptionsPseudoDef:
    DATA_TYPE_NAME: str = "EnbEntryOptions"
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG)
    ENTRY_OPTION_VALUE__FIELD_NAME = WrapperField("EntryOptionValue", FieldType.STRING)
    ENTRY_OPTION_KEY__FIELD_NAME = WrapperField("EntryOptionkey", FieldType.STRING)


class ExperimentEntryRecordPseudoDef:
    DATA_TYPE_NAME: str = "ExperimentEntryRecord"
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG)
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG)


class LimsUserPseudoDef:
    DATA_TYPE_NAME: str = "LimsUser"
    API_USER__FIELD_NAME = WrapperField("ApiUser", FieldType.BOOLEAN)
    EMAIL_ADDRESS__FIELD_NAME = WrapperField("EmailAddress", FieldType.STRING)
    FIRST_NAME__FIELD_NAME = WrapperField("FirstName", FieldType.STRING)
    LAST_NAME__FIELD_NAME = WrapperField("LastName", FieldType.STRING)
    MIDDLE_NAME__FIELD_NAME = WrapperField("MiddleName", FieldType.STRING)
    PWD_EXPIRE_DATE__FIELD_NAME = WrapperField("PwdExpireDate", FieldType.DATE)
    PWD_EXPIRE_INTERVAL__FIELD_NAME = WrapperField("PwdExpireInterval", FieldType.INTEGER)
    USER_NAME__FIELD_NAME = WrapperField("UserName", FieldType.STRING)


class NotebookExperimentPseudoDef:
    DATA_TYPE_NAME: str = "NotebookExperiment"
    ACCESS_LEVEL__FIELD_NAME = WrapperField("AccessLevel", FieldType.STRING)
    APPROVAL_DUE_DATE__FIELD_NAME = WrapperField("ApprovalDueDate", FieldType.DATE)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG)
    EXPERIMENT_NAME__FIELD_NAME = WrapperField("ExperimentName", FieldType.STRING)
    EXPERIMENT_OWNER__FIELD_NAME = WrapperField("ExperimentOwner", FieldType.STRING)
    EXPERIMENT_RECORD_ID__FIELD_NAME = WrapperField("ExperimentRecordId", FieldType.LONG)
    EXPERIMENT_TYPE_NAME__FIELD_NAME = WrapperField("ExperimentTypeName", FieldType.STRING)
    IS_ACTIVE__FIELD_NAME = WrapperField("IsActive", FieldType.BOOLEAN)
    IS_MODIFIABLE__FIELD_NAME = WrapperField("IsModifiable", FieldType.BOOLEAN)
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN)
    IS_PROTOCOL_TEMPLATE__FIELD_NAME = WrapperField("Is_Protocol_Template", FieldType.BOOLEAN)
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING)
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.DATE)
    SOURCE_TEMPLATE_ID__FIELD_NAME = WrapperField("SourceTemplateId", FieldType.LONG)
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.STRING)


class NotebookExperimentOptionPseudoDef:
    DATA_TYPE_NAME: str = "NotebookExperimentOption"
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG)
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING)
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING)


class SystemLogPseudoDef:
    DATA_TYPE_NAME: str = "SystemLog"
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    EVENT_ID__FIELD_NAME = WrapperField("EventId", FieldType.LONG)
    EVENT_TYPE__FIELD_NAME = WrapperField("EventType", FieldType.STRING)
    FULL_NAME__FIELD_NAME = WrapperField("FullName", FieldType.STRING)
    NEW_VALUE__FIELD_NAME = WrapperField("NewValue", FieldType.STRING)
    ORIGINAL_VALUE__FIELD_NAME = WrapperField("OriginalValue", FieldType.STRING)
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG)
    RECORD_NAME__FIELD_NAME = WrapperField("RecordName", FieldType.STRING)
    TIMESTAMP__FIELD_NAME = WrapperField("Timestamp", FieldType.DATE)
    USER_COMMENT__FIELD_NAME = WrapperField("UserComment", FieldType.STRING)
    USERNAME__FIELD_NAME = WrapperField("Username", FieldType.STRING)


class SystemObjectChangeLogPseudoDef:
    DATA_TYPE_NAME: str = "System_Object_Change_Log"
    ALT_ID__FIELD_NAME = WrapperField("Alt_Id", FieldType.STRING)
    ATTRIBUTE_NAME__FIELD_NAME = WrapperField("Attribute_Name", FieldType.STRING)
    CHANGE_TYPE__FIELD_NAME = WrapperField("Change_Type", FieldType.STRING)
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("Data_Field_Name", FieldType.STRING)
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("Data_Type_Name", FieldType.STRING)
    EVENT_ID__FIELD_NAME = WrapperField("Event_Id", FieldType.STRING)
    NEW_VALUE__FIELD_NAME = WrapperField("New_Value", FieldType.STRING)
    OBJECT_ID__FIELD_NAME = WrapperField("Object_Id", FieldType.STRING)
    OBJECT_TYPE__FIELD_NAME = WrapperField("Object_Type", FieldType.STRING)
    OLD_VALUE__FIELD_NAME = WrapperField("Old_Value", FieldType.STRING)
    TIMESTAMP__FIELD_NAME = WrapperField("Timestamp", FieldType.DATE)
    USERNAME__FIELD_NAME = WrapperField("Username", FieldType.STRING)


class TaskPseudoDef:
    DATA_TYPE_NAME: str = "Task"
    ATTACHMENT_REQUIRED__FIELD_NAME = WrapperField("AttachmentRequired", FieldType.BOOLEAN)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    CUSTOM_ACTION__FIELD_NAME = WrapperField("CustomAction", FieldType.STRING)
    DATA_TYPE_NAME_LIST__FIELD_NAME = WrapperField("DataTypeNameList", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE)
    DISPLAY_TYPE__FIELD_NAME = WrapperField("DisplayType", FieldType.ENUM)
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING)
    INPUT_DATA_TYPE_NAME__FIELD_NAME = WrapperField("InputDataTypeName", FieldType.STRING)
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN)
    LONG_DESC__FIELD_NAME = WrapperField("LongDesc", FieldType.STRING)
    MENU_TASK_ID__FIELD_NAME = WrapperField("MenuTaskId", FieldType.ENUM)
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING)
    SHORT_DESC__FIELD_NAME = WrapperField("ShortDesc", FieldType.STRING)
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG)
    TASK_VERSION__FIELD_NAME = WrapperField("TaskVersion", FieldType.LONG)
    TEMPLATE_TASK_ID__FIELD_NAME = WrapperField("TemplateTaskId", FieldType.LONG)
    TYPE__FIELD_NAME = WrapperField("Type", FieldType.ENUM)


class TaskAttachmentPseudoDef:
    DATA_TYPE_NAME: str = "TaskAttachment"
    ACTIVE_TASK_ID__FIELD_NAME = WrapperField("ActiveTaskId", FieldType.LONG)
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG)


class TaskOptionPseudoDef:
    DATA_TYPE_NAME: str = "TaskOption"
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING)
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING)
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG)


class TaskUsagePseudoDef:
    DATA_TYPE_NAME: str = "TaskUsage"
    FORCE_ATTACH__FIELD_NAME = WrapperField("ForceAttach", FieldType.BOOLEAN)
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN)
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG)
    TASK_ORDER__FIELD_NAME = WrapperField("TaskOrder", FieldType.INTEGER)
    TASK_USAGE_ID__FIELD_NAME = WrapperField("TaskUsageId", FieldType.LONG)
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG)


class VeloxWebhookPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK"
    CUSTOM_PLUGIN_POINT__FIELD_NAME = WrapperField("CUSTOM_PLUGIN_POINT", FieldType.STRING)
    DATA_TYPE_NAME_SET__FIELD_NAME = WrapperField("DATA_TYPE_NAME_SET", FieldType.STRING)
    DESCRIPTION__FIELD_NAME = WrapperField("DESCRIPTION", FieldType.STRING)
    ENB_ENTRY_TYPE__FIELD_NAME = WrapperField("ENB_ENTRY_TYPE", FieldType.STRING)
    EXPERIMENT_ENTRY_NAME_SET__FIELD_NAME = WrapperField("EXPERIMENT_ENTRY_NAME_SET", FieldType.STRING)
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING)
    ICON_COLOR__FIELD_NAME = WrapperField("ICON_COLOR", FieldType.STRING)
    ICON_GUID__FIELD_NAME = WrapperField("ICON_GUID", FieldType.STRING)
    IS_RETRY_ON_FAILURE__FIELD_NAME = WrapperField("IS_RETRY_ON_FAILURE", FieldType.BOOLEAN)
    IS_TRANSACTIONAL__FIELD_NAME = WrapperField("IS_TRANSACTIONAL", FieldType.BOOLEAN)
    LINE_1_TEXT__FIELD_NAME = WrapperField("LINE_1_TEXT", FieldType.STRING)
    LINE_2_TEXT__FIELD_NAME = WrapperField("LINE_2_TEXT", FieldType.STRING)
    PLUGIN_ORDER__FIELD_NAME = WrapperField("PLUGIN_ORDER", FieldType.INTEGER)
    PLUGIN_POINT__FIELD_NAME = WrapperField("PLUGIN_POINT", FieldType.STRING)
    SECTION_NAME_PATH__FIELD_NAME = WrapperField("SECTION_NAME_PATH", FieldType.STRING)
    TEMPLATE_NAME__FIELD_NAME = WrapperField("TEMPLATE_NAME", FieldType.STRING)
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING)


class VeloxWebhookExecutionPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION"
    EXECUTION_TIMESTAMP__FIELD_NAME = WrapperField("EXECUTION_TIMESTAMP", FieldType.DATE)
    EXECUTION_USERNAME__FIELD_NAME = WrapperField("EXECUTION_USERNAME", FieldType.STRING)
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING)
    LAST_ATTEMPT_NUMBER__FIELD_NAME = WrapperField("LAST_ATTEMPT_NUMBER", FieldType.INTEGER)
    LAST_ATTEMPT_RESULT__FIELD_NAME = WrapperField("LAST_ATTEMPT_RESULT", FieldType.STRING)
    REQUEST_BODY__FIELD_NAME = WrapperField("REQUEST_BODY", FieldType.STRING)
    WEBHOOK_GUID__FIELD_NAME = WrapperField("WEBHOOK_GUID", FieldType.STRING)
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING)


class VeloxWebhookExecutionAttemptPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION_ATTEMPT"
    ATTEMPT_DURATION__FIELD_NAME = WrapperField("ATTEMPT_DURATION", FieldType.INTEGER)
    ATTEMPT_NUMBER__FIELD_NAME = WrapperField("ATTEMPT_NUMBER", FieldType.INTEGER)
    ATTEMPT_RESULT__FIELD_NAME = WrapperField("ATTEMPT_RESULT", FieldType.STRING)
    ATTEMPT_TIMESTAMP__FIELD_NAME = WrapperField("ATTEMPT_TIMESTAMP", FieldType.DATE)
    EXECUTION_GUID__FIELD_NAME = WrapperField("EXECUTION_GUID", FieldType.STRING)
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING)
    RESPONSE_BODY__FIELD_NAME = WrapperField("RESPONSE_BODY", FieldType.STRING)
    RESPONSE_CODE__FIELD_NAME = WrapperField("RESPONSE_CODE", FieldType.INTEGER)
    WEBHOOK_GUID__FIELD_NAME = WrapperField("WEBHOOK_GUID", FieldType.STRING)
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING)


class VeloxWebhookExecutionLogPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION_LOG"
    ATTEMPT_GUID__FIELD_NAME = WrapperField("ATTEMPT_GUID", FieldType.STRING)
    LOG_LEVEL__FIELD_NAME = WrapperField("LOG_LEVEL", FieldType.STRING)
    LOG_LINE_NUM__FIELD_NAME = WrapperField("LOG_LINE_NUM", FieldType.INTEGER)
    LOG_MESSAGE__FIELD_NAME = WrapperField("LOG_MESSAGE", FieldType.STRING)
    LOG_TIMESTAMP__FIELD_NAME = WrapperField("LOG_TIMESTAMP", FieldType.DATE)


class VeloxRuleCostPseudoDef:
    DATA_TYPE_NAME: str = "VELOX_RULE_COST"
    ACTION_COST__FIELD_NAME = WrapperField("ACTION_COST", FieldType.LONG)
    ACTION_COUNT__FIELD_NAME = WrapperField("ACTION_COUNT", FieldType.LONG)
    ANCESTOR_DESCENDANT_COUNT__FIELD_NAME = WrapperField("ANCESTOR_DESCENDANT_COUNT", FieldType.LONG)
    PARENT_CHILD_COUNT__FIELD_NAME = WrapperField("PARENT_CHILD_COUNT", FieldType.LONG)
    PROCESSING_TIME__FIELD_NAME = WrapperField("PROCESSING_TIME", FieldType.LONG)
    RULE_GUID__FIELD_NAME = WrapperField("RULE_GUID", FieldType.STRING)
    SOURCE_RECORD_COUNT__FIELD_NAME = WrapperField("SOURCE_RECORD_COUNT", FieldType.LONG)
    TIMESTAMP__FIELD_NAME = WrapperField("TIMESTAMP", FieldType.DATE)
    TOTAL_COST__FIELD_NAME = WrapperField("TOTAL_COST", FieldType.LONG)
    TRANSACTION_GUID__FIELD_NAME = WrapperField("TRANSACTION_GUID", FieldType.STRING)
    USERNAME__FIELD_NAME = WrapperField("USERNAME", FieldType.STRING)


class VeloxConversationPseudoDef:
    DATA_TYPE_NAME: str = "VeloxConversation"
    CONVERSATION_DESCRIPTION__FIELD_NAME = WrapperField("ConversationDescription", FieldType.STRING)
    CONVERSATION_GUID__FIELD_NAME = WrapperField("ConversationGuid", FieldType.STRING)
    CONVERSATION_NAME__FIELD_NAME = WrapperField("ConversationName", FieldType.STRING)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    SERVER_PLUGIN_PATH__FIELD_NAME = WrapperField("Server_Plugin_Path", FieldType.STRING)


class VeloxConversationMessagePseudoDef:
    DATA_TYPE_NAME: str = "VeloxConversationMessage"
    CONVERSATION_GUID__FIELD_NAME = WrapperField("ConversationGuid", FieldType.STRING)
    MESSAGE__FIELD_NAME = WrapperField("Message", FieldType.STRING)
    MESSAGE_GUID__FIELD_NAME = WrapperField("MessageGuid", FieldType.STRING)
    MESSAGE_SENDER__FIELD_NAME = WrapperField("MessageSender", FieldType.STRING)
    MESSAGE_TIMESTAMP__FIELD_NAME = WrapperField("MessageTimestamp", FieldType.DATE)


class VeloxScriptPseudoDef:
    DATA_TYPE_NAME: str = "VeloxScript"
    CODE__FIELD_NAME = WrapperField("Code", FieldType.STRING)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.LONG)
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING)
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.LONG)
    PATH__FIELD_NAME = WrapperField("Path", FieldType.STRING)
    PLUGIN_DESCRIPTION__FIELD_NAME = WrapperField("PluginDescription", FieldType.STRING)
    PLUGIN_LINE1_TEXT__FIELD_NAME = WrapperField("PluginLine1Text", FieldType.STRING)
    PLUGIN_LINE2_TEXT__FIELD_NAME = WrapperField("PluginLine2Text", FieldType.STRING)
    PLUGIN_ORDER__FIELD_NAME = WrapperField("PluginOrder", FieldType.INTEGER)
    PLUGIN_POINT__FIELD_NAME = WrapperField("PluginPoint", FieldType.STRING)
    PROJECT_GUID__FIELD_NAME = WrapperField("ProjectGuid", FieldType.STRING)
    SCRIPT_GUID__FIELD_NAME = WrapperField("ScriptGuid", FieldType.STRING)


class VeloxScriptProjectPseudoDef:
    DATA_TYPE_NAME: str = "VeloxScriptProject"
    CLASS_PATH__FIELD_NAME = WrapperField("ClassPath", FieldType.STRING)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.LONG)
    DEPLOYMENT_OUT_OF_DATE__FIELD_NAME = WrapperField("DeploymentOutOfDate", FieldType.BOOLEAN)
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING)
    PROJECT_GUID__FIELD_NAME = WrapperField("ProjectGuid", FieldType.STRING)
    PROJECT_NAME__FIELD_NAME = WrapperField("ProjectName", FieldType.STRING)
    SCRIPT_LANGUAGE__FIELD_NAME = WrapperField("ScriptLanguage", FieldType.STRING)


class WorkflowPseudoDef:
    DATA_TYPE_NAME: str = "Workflow"
    ALL_ACCESS__FIELD_NAME = WrapperField("AllAccess", FieldType.BOOLEAN)
    CATEGORY__FIELD_NAME = WrapperField("Category", FieldType.STRING)
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE)
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE)
    DIRECT_LAUNCH__FIELD_NAME = WrapperField("DirectLaunch", FieldType.BOOLEAN)
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING)
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN)
    LONG_DESC__FIELD_NAME = WrapperField("LongDesc", FieldType.STRING)
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING)
    SHORT_DESC__FIELD_NAME = WrapperField("ShortDesc", FieldType.STRING)
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG)
    WORKFLOW_VERSION__FIELD_NAME = WrapperField("WorkflowVersion", FieldType.LONG)


class WorkflowOptionPseudoDef:
    DATA_TYPE_NAME: str = "WorkflowOption"
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING)
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING)
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG)
