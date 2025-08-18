import traceback
from abc import abstractmethod
from logging import Logger

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.WebhookService import AbstractWebhookHandler
from sapiopylib.rest.pojo.Message import VeloxLogMessage, VeloxLogLevel
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookEnums import WebhookEndpointType
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager

from sapiopycommons.callbacks.callback_util import CallbackUtil
from sapiopycommons.eln.experiment_handler import ExperimentHandler
from sapiopycommons.general.exceptions import SapioUserErrorException, SapioCriticalErrorException, \
    SapioUserCancelledException, SapioException, SapioDialogTimeoutException
from sapiopycommons.general.sapio_links import SapioNavigationLinker
from sapiopycommons.recordmodel.record_handler import RecordHandler
from sapiopycommons.rules.eln_rule_handler import ElnRuleHandler
from sapiopycommons.rules.on_save_rule_handler import OnSaveRuleHandler


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class CommonsWebhookHandler(AbstractWebhookHandler):
    """
    A subclass of AbstractWebhookHandler that provides additional quality of life features, including exception
    handling for special sapiopycommons exceptions, logging, easy access invocation type methods, and the context and
    record managers accessible through self.
    """
    logger: Logger

    user: SapioUser
    context: SapioWebhookContext

    dr_man: DataRecordManager
    rec_man: RecordModelManager
    inst_man: RecordModelInstanceManager
    rel_man: RecordModelRelationshipManager
    # FR-46329: Add the ancestor manager to CommonsWebhookHandler.
    an_man: RecordModelAncestorManager

    dt_cache: DataTypeCacheManager
    rec_handler: RecordHandler
    callback: CallbackUtil
    exp_handler: ExperimentHandler | None
    rule_handler: OnSaveRuleHandler | ElnRuleHandler | None

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        self.user = context.user
        self.context = context

        self.logger = self.user.logger

        self.dr_man = context.data_record_manager
        self.rec_man = RecordModelManager(self.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = RecordModelAncestorManager(self.rec_man)

        self.dt_cache = DataTypeCacheManager(self.user)
        self.rec_handler = RecordHandler(context)
        self.callback = CallbackUtil(context)
        if context.eln_experiment is not None:
            self.exp_handler = ExperimentHandler(context)
        else:
            self.exp_handler = None
        if self.is_on_save_rule():
            self.rule_handler = OnSaveRuleHandler(context)
        elif self.is_eln_rule():
            self.rule_handler = ElnRuleHandler(context)
        else:
            self.rule_handler = None

        # Wrap the execution of each webhook in a try/catch. If an exception occurs, handle any special sapiopycommons
        # exceptions. Otherwise, return a generic message stating that an error occurred.
        try:
            self.initialize(context)
            result = self.execute(context)
            if result is None:
                raise SapioException("Your execute function returned a None result! Don't forget your return statement!")
            return result
        except SapioUserErrorException as e:
            return self.handle_user_error_exception(e)
        except SapioCriticalErrorException as e:
            return self.handle_critical_error_exception(e)
        except SapioUserCancelledException as e:
            return self.handle_user_cancelled_exception(e)
        except SapioDialogTimeoutException as e:
            return self.handle_dialog_timeout_exception(e)
        except Exception as e:
            return self.handle_unexpected_exception(e)

    def initialize(self, context: SapioWebhookContext) -> None:
        """
        A function that can be optionally overridden by your webhooks to initialize additional instance variables,
        or set up whatever else you wish to set up before the execute function is ran. Default behavior does nothing.
        """
        pass

    @abstractmethod
    def execute(self, context: SapioWebhookContext) -> SapioWebhookResult:
        """
        The business logic of the webhook, implemented in all subclasses that are called as endpoints.
        """
        pass

    # CR-46153: Make CommonsWebhookHandler exception handling more easily overridable by splitting them out of
    # the run method and into their own functions.
    def handle_user_error_exception(self, e: SapioUserErrorException) -> SapioWebhookResult:
        """
        Handle a SapioUserErrorException.

        Default behavior returns a false result and the error message as display text in a webhook result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        return SapioWebhookResult(False, display_text=e.args[0])

    def handle_critical_error_exception(self, e: SapioCriticalErrorException) -> SapioWebhookResult:
        """
        Handle a SapioCriticalErrorException.

        Default behavior makes a display_error client callback with the error message and returns a false result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        # This error can be thrown by endpoints that can't send client callbacks. If that happens, fall back onto
        # sending display text instead.
        if self.can_send_client_callback():
            self.callback.display_error(e.args[0])
        else:
            return SapioWebhookResult(False, e.args[0])
        return SapioWebhookResult(False)

    def handle_user_cancelled_exception(self, e: SapioUserCancelledException) -> SapioWebhookResult:
        """
        Handle a SapioUserCancelledException.

        Default behavior simply ends the webhook session with a true result (since the user cancelling is a valid
        action).

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        return SapioWebhookResult(True)

    def handle_dialog_timeout_exception(self, e: SapioDialogTimeoutException) -> SapioWebhookResult:
        """
        Handle a SapioDialogTimeoutException.

        Default behavior displays an OK popup notifying the user that the dialog has timed out and returns a false
        webhook result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        # This dialog could time out too! Ignore it if it does.
        # No need to check can_send_client_callback() here, as this exception should only be thrown by endpoints that
        # are capable of sending callbacks.
        try:
            self.callback.ok_dialog("Notice", "You have remained idle for too long and this dialog has timed out. "
                                              "Close and re-initiate it to continue.")
        except SapioDialogTimeoutException:
            pass
        return SapioWebhookResult(False)

    def handle_unexpected_exception(self, e: Exception) -> SapioWebhookResult:
        """
        Handle a generic exception which isn't one of the handled Sapio exceptions.

        Default behavior returns a false webhook result with a generic error message as display text informing the user
        to contact Sapio support. Additionally, the stack trace of the exception that was thrown is logged to the
        execution log for the webhook call in the system.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        msg: str = traceback.format_exc()
        self.log_error(msg)
        # FR-47079: Also log all unexpected exception messages to the webhook execution log within the platform.
        self.log_error_to_webhook_execution_log(msg)
        return SapioWebhookResult(False, display_text="Unexpected error occurred during webhook execution. "
                                                      "Please contact Sapio support.")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def handle_any_exception(self, e: Exception) -> SapioWebhookResult | None:
        """
        An exception handler which runs regardless of the type of exception that was raised. Can be used to "rollback"
        the client if an error occurs. Default behavior does nothing and returns None.

        :param e: The exception that was raised.
        :return: An optional SapioWebhookResult. May return a custom message to the client that wouldn't have been
            sent by one of the normal exception handlers, or may return None if no result needs returned. If a result is
            returned, then the default behavior of other exception handlers is skipped.
        """
        return None

    def log_info(self, msg: str) -> None:
        """
        Write an info message to the webhook server log. Log destination is stdout. This message will include
        information about the user's group, their location in the system, the webhook invocation type, and other
        important information that can be gathered from the context that is useful for debugging.
        """
        self.logger.info(self._format_log(msg, "log_info call"))

    def log_error(self, msg: str) -> None:
        """
        Write an info message to the webhook server log. Log destination is stdout. This message will include
        information about the user's group, their location in the system, the webhook invocation type, and other
        important information that can be gathered from the context that is useful for debugging.
        """
        # PR-46209: Use logger.error instead of logger.info when logging errors.
        self.logger.error(self._format_log(msg, "log_error call"))

    def log_error_to_webhook_execution_log(self, msg: str) -> None:
        """
        Write an error message to the platform's webhook execution log. This can be reviewed by navigating to the
        webhook configuration where the webhook that called this function is defined and clicking the "View Log"
        button. From there, select one of the rows for the webhook executions and click "Download Log" from the right
        side table.
        """
        messenger = DataMgmtServer.get_messenger(self.user)
        messenger.log_message(VeloxLogMessage(message=self._format_log(msg, "Error occurred during webhook execution."),
                                              log_level=VeloxLogLevel.ERROR,
                                              originating_class=self.__class__.__name__))

    def _format_log(self, msg: str, prefix: str | None = None) -> str:
        """
        Given a message to log, populate it with some metadata about this particular webhook execution, including
        the group of the user and the invocation type of the webhook call.
        """
        # If we're able to, provide a link to the location that the error occurred at.
        navigator = SapioNavigationLinker(self.context)
        if self.context.eln_experiment is not None:
            link = navigator.experiment(self.context.eln_experiment)
        elif self.context.data_record and not self.context.data_record_list:
            link = navigator.data_record(self.context.data_record)
        elif self.context.base_data_record:
            link = navigator.data_record(self.context.base_data_record)
        else:
            link = None

        message: str = ""
        if prefix:
            message += prefix + "\n"
        message += f"Webhook invocation type: {self.context.end_point_type.display_name}\n"
        message += f"Username: {self.user.username}\n"
        # CR-46333: Add the user's group to the logging message.
        message += f"User group: {self.user.session_additional_data.current_group_name}\n"
        if link:
            message += f"User location: {link}\n"
        message += msg
        return message

    def is_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONMENU

    def is_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.FORMTOOLBAR

    def is_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TABLETOOLBAR

    def is_temp_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_FORM_TOOLBAR

    def is_temp_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_TABLE_TOOLBAR

    def is_eln_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOXELNRULEACTION

    def is_on_save_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an on save rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOX_RULE_ACTION
        # TODO: This VELOXONSAVERULEACTION endpoint type exists, but I don't see it actually getting sent by on save
        #  rule action invocations, instead seeing the above VELOX_RULE_ACTION type. Probably worth investigation.
        # return self.context.end_point_type == WebhookEndpointType.VELOXONSAVERULEACTION

    def is_eln_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTMAINTOOLBAR

    def is_eln_entry_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN entry toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.EXPERIMENTENTRYTOOLBAR

    def is_selection_list(self) -> bool:
        """
        :return: True if this endpoint was invoked as a selection list populator.
        """
        return self.context.end_point_type == WebhookEndpointType.SELECTIONDATAFIELD

    def is_report_builder(self) -> bool:
        """
        :return: True if this endpoint was invoked as a report builder template data populator.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORT_BUILDER_TEMPLATE_DATA_POPULATOR

    def is_scheduled_action(self) -> bool:
        """
        :return: True if this endpoint was invoked as a scheduled action.
        """
        return self.context.end_point_type == WebhookEndpointType.SCHEDULEDPLUGIN

    def is_action_button_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action button field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONDATAFIELD

    def is_action_text_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action text field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTION_TEXT_FIELD

    def is_custom(self) -> bool:
        """
        :return: True if this endpoint was invoked from a custom point, such as a custom queue.
        """
        return self.context.end_point_type == WebhookEndpointType.CUSTOM

    def is_calendar_event_click_handler(self) -> bool:
        """
        :return: True if this endpoint was invoked from a calendar event click handler.
        """
        return self.context.end_point_type == WebhookEndpointType.CALENDAR_EVENT_CLICK_HANDLER

    def is_eln_menu_grabber(self) -> bool:
        """
        :return: True if this endpoint was invoked as a notebook entry grabber.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTGRABBER

    def is_conversation_bot(self) -> bool:
        """
        :return: True if this endpoint was invoked as from a conversation bot.
        """
        return self.context.end_point_type == WebhookEndpointType.CONVERSATION_BOT

    def is_multi_data_type_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a multi data type table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORTTOOLBAR

    def can_send_client_callback(self) -> bool:
        """
        :return: Whether client callbacks and directives can be sent from this webhook's endpoint type.
        """
        return self.context.is_client_callback_available
