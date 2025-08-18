from __future__ import annotations

import io
from weakref import WeakValueDictionary

from requests import ReadTimeout
from sapiopylib.rest.ClientCallbackService import ClientCallback
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReport, CustomReportCriteria
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, VeloxStringFieldDefinition, \
    VeloxIntegerFieldDefinition, VeloxDoubleFieldDefinition, FieldDefinitionParser
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import OptionDialogRequest, ListDialogRequest, \
    FormEntryDialogRequest, InputDialogCriteria, TableEntryDialogRequest, ESigningRequestPojo, \
    DataRecordDialogRequest, InputSelectionRequest, FilePromptRequest, MultiFilePromptRequest, \
    TempTableSelectionRequest, DisplayPopupRequest, PopupType
from sapiopylib.rest.pojo.webhook.ClientCallbackResult import ESigningResponsePojo
from sapiopylib.rest.pojo.webhook.WebhookEnums import FormAccessLevel, ScanToSelectCriteria, SearchType
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.FormBuilder import FormBuilder
from sapiopylib.rest.utils.recorddatasinks import InMemoryRecordDataSink
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.files.file_util import FileUtil
from sapiopycommons.general.aliases import FieldMap, SapioRecord, AliasUtil, RecordIdentifier, FieldValue, \
    UserIdentifier
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.general.exceptions import SapioUserCancelledException, SapioException, SapioUserErrorException, \
    SapioDialogTimeoutException
from sapiopycommons.recordmodel.record_handler import RecordHandler


class CallbackUtil:
    user: SapioUser
    callback: ClientCallback
    dt_cache: DataTypeCacheManager
    _original_timeout: int
    timeout_seconds: int
    width_pixels: int | None
    width_percent: float | None

    __instances: WeakValueDictionary[SapioUser, CallbackUtil] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        user = AliasUtil.to_sapio_user(context)
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        if self.__initialized:
            return
        self.__initialized = True

        self.user = AliasUtil.to_sapio_user(context)
        self.callback = DataMgmtServer.get_client_callback(self.user)
        self.dt_cache = DataTypeCacheManager(self.user)
        self._original_timeout = self.user.timeout_seconds
        self.timeout_seconds = self.user.timeout_seconds
        self.width_pixels = None
        self.width_percent = None

    def set_dialog_width(self, width_pixels: int | None = None, width_percent: float | None = None):
        """
        Set the width that dialogs will appear as for those dialogs that support specifying their width.

        :param width_pixels: The number of pixels wide that dialogs will appear as.
        :param width_percent: The percentage (as a value between 0 and 1) of the client's screen width that dialogs
            will appear as.
        """
        if width_pixels is not None and width_percent is not None:
            raise SapioException("Cannot set both width_pixels and width_percent at once.")
        self.width_pixels = width_pixels
        self.width_percent = width_percent

    def set_dialog_timeout(self, timeout: int):
        """
        Alter the timeout time used for callback requests that create dialogs for the user to interact with. By default,
        a CallbackUtil will use the timeout time of the SapioUser provided to it. By altering this, a different timeout
        time is used.

        :param timeout: The number of seconds that must elapse before a SapioDialogTimeoutException is thrown by
            any callback that creates a dialog for the user to interact with.
        """
        self.timeout_seconds = timeout

    def toaster_popup(self, message: str, title: str = "", popup_type: PopupType = PopupType.Info) -> None:
        """
        Display a toaster popup in the bottom right corner of the user's screen.

        :param message: The message to display in the toaster.
        :param title: The title to display at the top of the toaster.
        :param popup_type: The popup type to use for the toaster. This controls the color that the toaster appears with.
            Info is blue, Success is green, Warning is yellow, and Error is red
        """
        self.callback.display_popup(DisplayPopupRequest(title, message, popup_type))

    def display_info(self, message: str) -> None:
        """
        Display an info message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user.
        """
        self.callback.display_info(message)

    def display_warning(self, message: str) -> None:
        """
        Display a warning message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user.
        """
        self.callback.display_warning(message)

    def display_error(self, message: str) -> None:
        """
        Display an error message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user.
        """
        self.callback.display_error(message)

    def option_dialog(self, title: str, msg: str, options: list[str], default_option: int = 0,
                      user_can_cancel: bool = False) -> str:
        """
        Create an option dialog with the given options for the user to choose from.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param options: The button options that the user has to choose from.
        :param default_option: The index of the option in the options list that defaults as the first choice.
        :param user_can_cancel: True if the user is able to click the X to close the dialog. False if the user cannot
            close the dialog without selecting an option. If the user is able to cancel and does so, a
            SapioUserCancelledException is thrown.
        :return: The name of the button that the user selected.
        """
        request = OptionDialogRequest(title, msg, options, default_option, user_can_cancel,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: int | None = self.callback.show_option_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return options[response]

    def ok_dialog(self, title: str, msg: str) -> None:
        """
        Create an option dialog where the only option is "OK". Doesn't allow the user to cancel the
        dialog using the X at the top right corner. Returns nothing.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        """
        self.option_dialog(title, msg, ["OK"], 0, False)

    def ok_cancel_dialog(self, title: str, msg: str, default_ok: bool = True) -> bool:
        """
        Create an option dialog where the only options are "OK" and "Cancel". Doesn't allow the user to cancel the
        dialog using the X at the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param default_ok: If true, "OK" is the default choice. Otherwise, the default choice is "Cancel".
        :return: True if the user selected OK. False if the user selected Cancel.
        """
        return self.option_dialog(title, msg, ["OK", "Cancel"], 0 if default_ok else 1, False) == "OK"

    def yes_no_dialog(self, title: str, msg: str, default_yes: bool = True) -> bool:
        """
        Create an option dialog where the only options are "Yes" and "No". Doesn't allow the user to cancel the
        dialog using the X at the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param default_yes: If true, "Yes" is the default choice. Otherwise, the default choice is "No".
        :return: True if the user selected Yes. False if the user selected No.
        """
        return self.option_dialog(title, msg, ["Yes", "No"], 0 if default_yes else 1, False) == "Yes"

    def list_dialog(self, title: str, options: list[str], multi_select: bool = False,
                    preselected_values: list[str] | None = None) -> list[str]:
        """
        Create a list dialog with the given options for the user to choose from.

        :param title: The title of the dialog.
        :param options: The list options that the user has to choose from.
        :param multi_select: Whether the user is able to select multiple options from the list.
        :param preselected_values: A list of values that will already be selected when the list dialog is created. The
            user can unselect these values if they want to.
        :return: The list of options that the user selected.
        """
        request = ListDialogRequest(title, multi_select, options, preselected_values,
                                    width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[str] | None = self.callback.show_list_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def form_dialog(self,
                    title: str,
                    msg: str,
                    fields: list[AbstractVeloxFieldDefinition],
                    values: FieldMap = None,
                    column_positions: dict[str, tuple[int, int]] = None,
                    *,
                    data_type: str = "Default",
                    display_name: str | None = None,
                    plural_display_name: str | None = None) -> FieldMap:
        """
        Create a form dialog where the user may input data into the fields of the form. Requires that the caller
        provide the definitions of every field in the form.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form.
        :param fields: The definitions of the fields to display in the form. Fields will be displayed in the order they
            are provided in this list.
        :param values: Sets the default values of the fields.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.)
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A dictionary mapping the data field names of the given field definitions to the response value from
            the user for that field.
        """
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"

        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field_def in fields:
            field_name = field_def.data_field_name
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]
            builder.add_field(field_def, column, span)

        request = FormEntryDialogRequest(title, msg, builder.get_temporary_data_type(), values,
                                         width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: FieldMap | None = self.callback.show_form_entry_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def record_form_dialog(self,
                           title: str,
                           msg: str,
                           fields: list[str],
                           record: SapioRecord,
                           column_positions: dict[str, tuple[int, int]] = None,
                           editable: bool | None = True) -> FieldMap:
        """
        Create a form dialog where the user may input data into the fields of the form. The form is constructed from
        a given record. Provided field names must match fields on the definition of the data type of the given record.
        The fields that are displayed will have their default value be that of the fields on the given record.

        Makes webservice calls to get the data type definition and fields of the given record if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param fields: The data field names of the fields from the record to display in the form. Fields will be
            displayed in the order they are provided in this list.
        :param record: The record to display the values of.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.)
        :param editable: If true, all fields are displayed as editable. If false, all fields are displayed as
            uneditable. If none, only those fields that are defined as editable by the data designer will be editable.
        :return: A dictionary mapping the data field names of the given field definitions to the response value from
            the user for that field.
        """
        # Get the field definitions of the data type.
        data_type: str = record.data_type_name
        type_def: DataTypeDefinition = self.dt_cache.get_data_type(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = self.dt_cache.get_fields_for_type(data_type)

        # Make everything visible, because presumably the caller gave a field name because they want it to be seen.
        modifier = FieldModifier(visible=True, editable=editable)

        # Build the form using only those fields that are desired.
        values: dict[str, FieldValue] = {}
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            values[field_name] = record.get_field_value(field_name)
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]
            builder.add_field(modifier.modify_field(field_def), column, span)

        request = FormEntryDialogRequest(title, msg, builder.get_temporary_data_type(), values,
                                         width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: FieldMap | None = self.callback.show_form_entry_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def input_dialog(self, title: str, msg: str, field: AbstractVeloxFieldDefinition) -> FieldValue:
        """
        Create an input dialog where the user must input data for a singular field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field: The definition for a field that the user must provide input to.
        :return: The response value from the user for the given field.
        """
        request = InputDialogCriteria(title, msg, field,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: FieldValue | None = self.callback.show_input_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def string_input_dialog(self, title: str, msg: str, field_name: str, default_value: str | None = None,
                            max_length: int | None = None, editable: bool = True, **kwargs) -> str:
        """
        Create an input dialog where the user must input data for a singular text field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the string field.
        :param default_value: The default value to place into the string field, if any.
        :param max_length: The max length of the string value. If not provided, uses the length of the default value.
            If neither this nor a default value are provided, defaults to 100 characters.
        :param editable: Whether the field is editable by the user.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The string that the user input into the dialog.
        """
        if max_length is None:
            max_length = len(default_value) if default_value else 100
        field = VeloxStringFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                           max_length=max_length, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field)

    def integer_input_dialog(self, title: str, msg: str, field_name: str, default_value: int = None,
                             min_value: int = -10000, max_value: int = 10000, editable: bool = True, **kwargs) -> int:
        """
        Create an input dialog where the user must input data for a singular integer field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the integer field.
        :param default_value: The default value to place into the integer field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param editable: Whether the field is editable by the user.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The integer that the user input into the dialog.
        """
        if default_value is None:
            default_value = max(0, min_value)
        field = VeloxIntegerFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                            min_value=min_value, max_value=max_value, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field)

    def double_input_dialog(self, title: str, msg: str, field_name: str, default_value: float = None,
                            min_value: float = -10000000, max_value: float = 100000000, editable: bool = True,
                            **kwargs) -> float:
        """
        Create an input dialog where the user must input data for a singular double field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the double field.
        :param default_value: The default value to place into the double field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param editable: Whether the field is editable by the user.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The float that the user input into the dialog.
        """
        if default_value is None:
            default_value = max(0., min_value)
        field = VeloxDoubleFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                           min_value=min_value, max_value=max_value, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field)

    def table_dialog(self,
                     title: str,
                     msg: str,
                     fields: list[AbstractVeloxFieldDefinition],
                     values: list[FieldMap],
                     group_by: str | None = None,
                     image_data: list[bytes] | None = None,
                     *,
                     data_type: str = "Default",
                     display_name: str | None = None,
                     plural_display_name: str | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. Requires that the caller
        provide the definitions of every field in the table.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form.
        :param fields: The definitions of the fields to display as table columns. Fields will be displayed in the order
            they are provided in this list.
        :param values: The values to set for each row of the table.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the values list.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"

        # Key fields display their columns in order before all non-key fields.
        # Unmark key fields so that the column order is respected exactly as the caller provides it.
        modifier = FieldModifier(key_field=False)

        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field in fields:
            builder.add_field(modifier.modify_field(field))

        request = TableEntryDialogRequest(title, msg, builder.get_temporary_data_type(), values,
                                          record_image_data_list=image_data, group_by_field=group_by,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[FieldMap] | None = self.callback.show_table_entry_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def record_table_dialog(self,
                            title: str,
                            msg: str,
                            fields: list[str],
                            records: list[SapioRecord],
                            editable: bool | None = True,
                            group_by: str | None = None,
                            image_data: list[bytes] | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a given list of records of a singular type. Provided field names must match fields on the definition of the data
        type of the given records. The fields that are displayed will have their default value be that of the fields on
        the given records.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param records: The records to display as rows in the table.
        :param fields: The names of the fields to display as columns in the table. Fields will be displayed in the order
            they are provided in this list.
        :param editable: If true, all fields are displayed as editable. If false, all fields are displayed as
            uneditable. If none, only those fields that are defined as editable by the data designer will be editable.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list.
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        if not records:
            raise SapioException("No records provided.")
        data_types: set[str] = {x.data_type_name for x in records}
        if len(data_types) > 1:
            raise SapioException("Multiple data type names encountered in records list for record table popup.")
        data_type: str = data_types.pop()
        # Get the field maps from the records.
        field_map_list: list[FieldMap] = AliasUtil.to_field_map_lists(records)
        # Get the field definitions of the data type.
        type_def: DataTypeDefinition = self.dt_cache.get_data_type(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = self.dt_cache.get_fields_for_type(data_type)

        # Key fields display their columns in order before all non-key fields.
        # Unmark key fields so that the column order is respected exactly as the caller provides it.
        # Also make everything visible, because presumably the caller gave a field name because they want it to be seen.
        modifier = FieldModifier(visible=True, key_field=False, editable=editable)

        # Build the form using only those fields that are desired.
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            builder.add_field(modifier.modify_field(field_def))

        request = TableEntryDialogRequest(title, msg, builder.get_temporary_data_type(), field_map_list,
                                          record_image_data_list=image_data, group_by_field=group_by,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[FieldMap] | None = self.callback.show_table_entry_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def multi_type_table_dialog(self,
                                title: str,
                                msg: str,
                                fields: list[(str, str) | AbstractVeloxFieldDefinition],
                                row_contents: list[list[SapioRecord | FieldMap]],
                                *,
                                default_modifier: FieldModifier | None = None,
                                field_modifiers: dict[str, FieldModifier] | None = None,
                                data_type: str = "Default",
                                display_name: str | None = None,
                                plural_display_name: str | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a given list of records of multiple data types or field maps. Provided field names must match with field names
        from the data type definition of the given records. The fields that are displayed will have their default value
        be that of the fields on the given records or field maps.

        Makes webservice calls to get the data type field definitions of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param fields: A list of objects representing the fields in the table. This could either be a two-element tuple
            where the first element is a data type name and the second is a field name, or it could be a field
            definition. If it is the former, a query will be made to find the field definition matching tht data type.
            The data type names of the fields must match the data type names of the records in the row contents.
            See the description of row_contents for what to do if you want to construct a field that pulls from a field
            map.
            If two fields share the same field name, an exception will be thrown. This is even true in the case where
            the data type name of the fields is different. If you wish to display two fields from two data types with
            the same name, then you must provide a FieldModifier for at least one of the fields where prepend_data_type
            is True in order to make that field's name unique again. Note that if you do this for a field, the mapping
            of record to field name will use the unedited field name, but the return results of this function will
            use the edited field name in the results dictionary for a row.
        :param row_contents: A list where each element is another list representing the records or a field map that will
            be used to populate the columns of the table. If the data type of a given record doesn't match any of the
            data type names of the given fields, then it will not be used.
            This list can contain up to one field map, which are fields not tied to a record. This is so that you can
            create abstract field definition not tied to a specific record in the system. If you want to define an
            abstract field that pulls from the field map in the row contents, then you must set the data type name to
            Default.
            If a record of a given data type appears more than once in one of the inner-lists of the row contents, or
            there is more than one field map, then an exception will be thrown, as there is no way of distinguishing
            which record should be used for a field, and not all fields could have their values combined across multiple
            records.
            The row contents may have an inner-list which is missing a record of a data type that matches one of the
            fields. In this case, the field value for that row under that column will be null.
            The inner-list does not need to be sorted in any way, as this function will map the inner-list contents to
            fields as necessary.
            The inner-list may contain null elements; these will simply be discarded by this function.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        # Set the default modifier to make all fields visible and not key if no default was provided.
        if default_modifier is None:
            default_modifier = FieldModifier(visible=True, key_field=False)
        # To make things simpler, treat null field modifiers as an empty dict.
        if field_modifiers is None:
            field_modifiers = {}

        # Construct the final fields list from the possible field objects.
        final_fields: list[AbstractVeloxFieldDefinition] = []
        # Keep track of whether any given field name appears more than once, as two fields could have the same
        # field name but different data types. In this case, the user should provide a field modifier or field
        # definition that changes one of the field names.
        field_names: list[str] = []
        for field in fields:
            # Find the field definition for this field object.
            if isinstance(field, tuple):
                field_def: AbstractVeloxFieldDefinition = self.dt_cache.get_fields_for_type(field[0]).get(field[1])
            elif isinstance(field, AbstractVeloxFieldDefinition):
                field_def: AbstractVeloxFieldDefinition = field
            else:
                raise SapioException("Unrecognized field object.")

            # Locate the modifier for this field and store the modified field.
            name: str = field_def.data_field_name
            modifier: FieldModifier = field_modifiers.get(name, default_modifier)
            field_def: AbstractVeloxFieldDefinition = modifier.modify_field(field_def)
            final_fields.append(field_def)

            # Verify that this field name isn't a duplicate.
            # The field name may have changed due to the modifier.
            name: str = field_def.data_field_name
            if name in field_names:
                raise SapioException(f"The field name \"{name}\" appears more than once in the given fields. "
                                     f"If you have provided two fields with the same name but different data types, "
                                     f"consider providing a FieldModifier where prepend_data_type is true for one of "
                                     f"the fields so that the field names will be different.")
            field_names.append(name)

        # Get the values for each row.
        values: list[dict[str, FieldValue]] = []
        for row in row_contents:
            # The final values for this row:
            row_values: dict[str, FieldValue] = {}

            # Map the records for this row by their data type. If a field map is provided, its data type is Default.
            row_records: dict[str, SapioRecord | FieldMap] = {}
            for rec in row:
                # Toss out null elements.
                if rec is None:
                    continue
                # Map records to their data type name. Map field maps to Default.
                dt: str = "Default" if isinstance(rec, dict) else rec.data_type_name
                # Warn if the same data type name appears more than once.
                if dt in row_records:
                    raise SapioException(f"The data type \"{dt}\" appears more than once in the given row contents.")
                row_records[dt] = rec

            # Get the field values from the above records.
            for field in final_fields:
                # Find the object that corresponds to this field given its data type name.
                record: SapioRecord | FieldMap | None = row_records.get(field.data_type_name)
                # This could be either a record, a field map, or null. Convert any records to field maps.
                if not isinstance(record, dict) and record is not None:
                    record: FieldMap | None = AliasUtil.to_field_map_lists([record])[0]

                # Find out if this field had its data type prepended to it. If this is the case, then we need to find
                # the true data field name before retrieving the value from the field map.
                name: str = field.data_field_name
                if field_modifiers.get(name, default_modifier).prepend_data_type is True:
                    name = name.split(".")[1]

                # Set the value for this particular field.
                row_values[field.data_field_name] = record.get(name) if record else None
            values.append(row_values)

        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"

        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field in final_fields:
            builder.add_field(field)

        request = TableEntryDialogRequest(title, msg, builder.get_temporary_data_type(), values,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[FieldMap] | None = self.callback.show_table_entry_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response
    
    def record_view_dialog(self,
                           title: str,
                           record: SapioRecord,
                           layout: str | DataTypeLayout | None = None,
                           minimized: bool = False,
                           access_level: FormAccessLevel | None = None,
                           plugin_path_list: list[str] | None = None) -> None:
        """
        Create an IDV dialog for the given record. This IDV may use an existing layout already defined in the system,
        and can be created to allow the user to edit the field in the IDV, or to be read-only for the user to review.
        This returns no value, but if the user cancels the dialog instead of clicking the "OK" button, then a
        SapioUserCancelledException will be thrown.

        :param title: The title of the dialog.
        :param record: The record to be displayed in the dialog.
        :param layout: The layout that will be used to display the record in the dialog. If this is not
            provided, then the layout assigned to the current user's group for this data type will be used. If this
            is provided as a string, then a webservice call will be made to retrieve the data type layout matching
            the name of that string for the given record's data type.
        :param minimized: If true, then the dialog will only show key fields and required fields initially
            until the expand button is clicked (similar to when using the built-in add buttons to create new records).
        :param access_level: The level of access that the user will have on this field entry dialog. This attribute
            determines whether the user will be able to edit the fields in the dialog, use core features, or use toolbar
            buttons. If no value is provided, then the form will be editable.
        :param plugin_path_list: A white list of plugins that should be displayed in the dialog. This white list
            includes plugins that would be displayed on sub-tables/components in the layout.
        """
        # Ensure that the given record is a DataRecord.
        record: DataRecord = AliasUtil.to_data_record(record)

        # Get the corresponding DataTypeLayout for the provided name.
        if isinstance(layout, str):
            # TODO: Replace with dt_cache if the DataTypeCacheManager ever starts caching layouts.
            dt_man = DataMgmtServer.get_data_type_manager(self.user)
            data_type: str = record.get_data_type_name()
            layouts: dict[str, DataTypeLayout] = {x.layout_name: x for x in dt_man.get_data_type_layout_list(data_type)}
            layout_name: str = layout
            layout: DataTypeLayout | None = layouts.get(layout_name)
            # If a name was provided then the caller expects that name to exist. Throw an exception if it doesn't.
            if not layout:
                raise SapioException(f"The data type \"{data_type}\" does not have a layout by the name "
                                     f"\"{layout_name}\" in the system.")

        request = DataRecordDialogRequest(title, record, layout, minimized, access_level, plugin_path_list,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: bool = self.callback.data_record_form_view_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if not response:
            raise SapioUserCancelledException()
    
    def selection_dialog(self,
                         msg: str,
                         fields: list[AbstractVeloxFieldDefinition],
                         values: list[FieldMap],
                         multi_select: bool = True,
                         *,
                         data_type: str = "Default",
                         display_name: str | None = None,
                         plural_display_name: str | None = None) -> list[FieldMap]:
        """
        Create a selection dialog for a list of field maps for the user to choose from. Requires that the caller
        provide the definitions of every field in the table.

        :param msg: The message to display in the dialog.
        :param fields: The definitions of the fields to display as table columns. Fields will be displayed in the order
            they are provided in this list.
        :param values: The values to set for each row of the table.
        :param multi_select: Whether the user is able to select multiple rows from the list.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A list of field maps corresponding to the chosen input field maps.
        """
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"

        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field in fields:
            builder.add_field(field)

        request = TempTableSelectionRequest(builder.get_temporary_data_type(), msg, values,
                                            multi_select=multi_select)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[FieldMap] | None = self.callback.show_temp_table_selection_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response
    
    def record_selection_dialog(self, msg: str, fields: list[str], records: list[SapioRecord],
                                multi_select: bool = True) -> list[SapioRecord]:
        """
        Create a record selection dialog for a list of records for the user to choose from. Provided field names must
        match fields on the definition of the data type of the given records.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param msg: The message to display in the dialog.
        :param fields: The names of the fields to display as columns in the table. Fields will be displayed in the order
            they are provided in this list.
        :param records: The records to display as rows in the table.
        :param multi_select: Whether the user is able to select multiple records from the list.
        :return: A list of the selected records.
        """
        if not records:
            raise SapioException("No records provided.")
        data_types: set[str] = {x.data_type_name for x in records}
        if len(data_types) > 1:
            raise SapioException("Multiple data type names encountered in records list for record table popup.")
        data_type: str = data_types.pop()
        # Get the field maps from the records.
        field_map_list: list[FieldMap] = AliasUtil.to_field_map_lists(records)
        # Put the record ID of each record in its corresponding field map so that we can map the field maps back to
        # the records when we return them to the caller.
        for record, field_map in zip(records, field_map_list):
            field_map.update({"RecId": record.record_id})
        # Get the field definitions of the data type.
        type_def: DataTypeDefinition = self.dt_cache.get_data_type(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = self.dt_cache.get_fields_for_type(data_type)

        # Key fields display their columns in order before all non-key fields.
        # Unmark key fields so that the column order is respected exactly as the caller provides it.
        # Also make everything visible, because presumably the caller give a field name because they want it to be seen.
        modifier = FieldModifier(visible=True, key_field=False)

        # Build the form using only those fields that are desired.
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            builder.add_field(modifier.modify_field(field_def))

        request = TempTableSelectionRequest(builder.get_temporary_data_type(), msg, field_map_list,
                                            multi_select=multi_select)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[FieldMap] | None = self.callback.show_temp_table_selection_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        # Map the field maps in the response back to the record they come from, returning the chosen record instead of
        # the chosen field map.
        records_by_id: dict[int, SapioRecord] = RecordHandler.map_by_id(records)
        ret_list: list[SapioRecord] = []
        for field_map in response:
            ret_list.append(records_by_id.get(field_map.get("RecId")))
        return ret_list

    def input_selection_dialog(self,
                               wrapper_type: type[WrappedType],
                               msg: str,
                               multi_select: bool = True,
                               only_key_fields: bool = False,
                               search_types: list[SearchType] | None = None,
                               scan_criteria: ScanToSelectCriteria | None = None,
                               custom_search: CustomReport | CustomReportCriteria | str | None = None,
                               preselected_records: list[RecordIdentifier] | None = None,
                               record_blacklist: list[RecordIdentifier] | None = None,
                               record_whitelist: list[RecordIdentifier] | None = None) -> list[WrappedType]:
        """
        Display a table of records that exist in the system matching the given data type and filter criteria and have
        the user select one or more records from the table.

        :param wrapper_type: The record model wrapper for the records to display in the dialog.
        :param msg: The message to show near the top of the dialog, below the title. This can be used to
            instruct the user on what is desired from the dialog.
        :param multi_select: Whether the user may select multiple items at once in this dialog.
        :param only_key_fields: Whether only key fields of the selected data type should be displayed in the table
            of data in the dialog. If false, allows all possible fields to be displayed as columns in the table.
        :param search_types: The type of search that will be made available to the user through the dialog. This
            includes quick searching a list of records, allowing the user to create an advanced search, or allowing
            the user to browse the record tree.
        :param scan_criteria: If present, the dialog will show a scan-to-select editor in the quick search
            section that allows for picking a field to match on and scanning a value to more easily select records.
            If quick search is not an allowable search type from the search_types parameter, then this
            parameter will have no effect.
        :param custom_search: An alternate search to be used in the quick search section to pre-filter the displayed
            records. If not provided or if the search is cross data type or not a report of the type specified, all
            records of the type will be shown (which is the normal quick search results behavior).
            If quick search is not an allowable search type from the search_types parameter, then this
            parameter will have no effect.
            If the search is provided as a string, then a webservice call will be made to retrieve the custom report
            criteria for the system report/predefined search in the system matching that name.
        :param preselected_records: The records that should be selected in the dialog when it is initially
            displayed to the user. The user will be allowed to deselect these records if they so wish. If preselected
            record IDs are provided, the dialog will automatically allow multi-selection of records.
        :param record_blacklist: A list of records that should not be seen as possible options in the dialog.
        :param record_whitelist: A list of records that will be seen as possible options in the dialog. Records not in
            this whitelist will not be displayed if a whitelist is provided.
        :return: A list of the records selected by the user in the dialog, wrapped as record models using the provided
            wrapper.
        """
        data_type: str = wrapper_type.get_wrapper_data_type_name()

        # Reduce the provided lists of records down to lists of record IDs.
        if preselected_records:
            preselected_records: list[int] = AliasUtil.to_record_ids(preselected_records)
        if record_blacklist:
            record_blacklist: list[int] = AliasUtil.to_record_ids(record_blacklist)
        if record_whitelist:
            record_whitelist: list[int] = AliasUtil.to_record_ids(record_whitelist)

        # If CustomReportCriteria was provided, it must be wrapped as a CustomReport.
        if isinstance(custom_search, CustomReportCriteria):
            custom_search: CustomReport = CustomReport(False, [], custom_search)
        # If a string was provided, locate the report criteria for the predefined search in the system matching this
        # name.
        if isinstance(custom_search, str):
            custom_search: CustomReport = CustomReportUtil.get_system_report_criteria(self.user, custom_search)

        request = InputSelectionRequest(data_type, msg, search_types, only_key_fields, record_blacklist,
                                        record_whitelist, preselected_records, custom_search, scan_criteria,
                                        multi_select)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: list[DataRecord] | None = self.callback.show_input_selection_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return RecordHandler(self.user).wrap_models(response, wrapper_type)
    
    def esign_dialog(self, title: str, msg: str, show_comment: bool = True,
                     additional_fields: list[AbstractVeloxFieldDefinition] = None) -> ESigningResponsePojo:
        """
        Create an e-sign dialog for the user to interact with.
        
        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param show_comment: Whether the "Meaning of Action" field should appear in the e-sign dialog. If true, the
            user is required to provide an action.
        :param additional_fields: Field definitions for additional fields to display in the dialog, for if there is
            other information you wish to gather from the user alongside the e-sign.
        :return: An e-sign response object containing information about the e-sign attempt.
        """
        temp_dt = None
        if additional_fields:
            builder = FormBuilder()
            for field in additional_fields:
                builder.add_field(field)
            temp_dt = builder.get_temporary_data_type()
        request = ESigningRequestPojo(title, msg, show_comment, temp_dt,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: ESigningResponsePojo | None = self.callback.show_esign_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if response is None:
            raise SapioUserCancelledException()
        return response

    def request_file(self, title: str, exts: list[str] | None = None,
                     show_image_editor: bool = False, show_camera_button: bool = False) -> tuple[str, bytes]:
        """
        Request a single file from the user.

        :param title: The title of the dialog.
        :param exts: The allowable file extensions of the uploaded file. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
            rather than selecting an existing file.
        :return: The file name and bytes of the uploaded file.
        """
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts: list[str] = []

        # Use a data sink to consume the data. In order to get both the file name and the file data,
        # I've recreated a part of sink.upload_single_file_to_webhook_server() in this function, as
        # calling that sink function throws out the file name of the uploaded file.
        sink = InMemoryRecordDataSink(self.user)
        with sink as io_obj:
            def do_consume(chunk: bytes) -> None:
                return sink.consume_data(chunk, io_obj)

            request = FilePromptRequest(title, show_image_editor, ",".join(exts), show_camera_button)
            try:
                self.user.timeout_seconds = self.timeout_seconds
                file_path: str | None = self.callback.show_file_dialog(request, do_consume)
            except ReadTimeout:
                raise SapioDialogTimeoutException()
            finally:
                self.user.timeout_seconds = self._original_timeout
        if file_path is None:
            raise SapioUserCancelledException()

        self.__verify_file(file_path, sink.data, exts)
        return file_path, sink.data

    def request_files(self, title: str, exts: list[str] | None = None,
                      show_image_editor: bool = False, show_camera_button: bool = False) -> dict[str, bytes]:
        """
        Request multiple files from the user.

        :param title: The title of the dialog.
        :param exts: The allowable file extensions of the uploaded files. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
            rather than selecting an existing file.
        :return: A dictionary of file name to file bytes for each file the user uploaded.
        """
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts: list[str] = []

        request = MultiFilePromptRequest(title, show_image_editor, ",".join(exts), show_camera_button)
        try:
            self.user.timeout_seconds = self.timeout_seconds
            file_paths: list[str] | None = self.callback.show_multi_file_dialog(request)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        if not file_paths:
            raise SapioUserCancelledException()

        ret_dict: dict[str, bytes] = {}
        for file_path in file_paths:
            sink = InMemoryRecordDataSink(self.user)
            sink.consume_client_callback_file_path_data(file_path)
            self.__verify_file(file_path, sink.data, exts)
            ret_dict.update({file_path: sink.data})

        return ret_dict

    @staticmethod
    def __verify_file(file_path: str, file_bytes: bytes, allowed_extensions: list[str]) -> None:
        """
        Verify that the provided file was read (i.e. the file path and file bytes aren't None or empty) and that it
        has the correct file extension. Raises a user error exception if something about the file is incorrect.

        :param file_path: The name of the file to verify.
        :param file_bytes: The bytes of the file to verify.
        :param allowed_extensions: The file extensions that the file path is allowed to have.
        """
        if file_path is None or len(file_path) == 0 or file_bytes is None or len(file_bytes) == 0:
            raise SapioUserErrorException("Empty file provided or file unable to be read.")
        if len(allowed_extensions) != 0:
            matches: bool = False
            for ext in allowed_extensions:
                if file_path.endswith("." + ext.lstrip(".")):
                    matches = True
                    break
            if matches is False:
                raise SapioUserErrorException("Unsupported file type. Expecting the following extension(s): "
                                              + (",".join(allowed_extensions)))

    def write_file(self, file_name: str, file_data: str | bytes) -> None:
        """
        Send a file to the user for them to download.

        :param file_name: The name of the file.
        :param file_data: The data of the file, provided as either a string or as a bytes array.
        """
        data = io.BytesIO(file_data.encode() if isinstance(file_data, str) else file_data)
        self.callback.send_file(file_name, False, data)

    def write_zip_file(self, zip_name: str, files: dict[str, str | bytes]) -> None:
        """
        Send a collection of files to the user in a zip file.

        :param zip_name: The name of the zip file.
        :param files: A dictionary of the files to add to the zip file.
        """
        data = io.BytesIO(FileUtil.zip_files(files))
        self.callback.send_file(zip_name, False, data)


class FieldModifier:
    """
    A FieldModifier can be used to update the settings of a field definition from the system.
    """
    prepend_data_type: bool
    display_name: str | None
    required: bool | None
    editable: bool | None
    visible: bool | None
    key_field: bool | None
    column_width: int | None

    def __init__(self, *, prepend_data_type: bool = False,
                 display_name: str | None = None, required: bool | None = None, editable: bool | None = None,
                 visible: bool | None = None, key_field: bool | None = None, column_width: int | None = None):
        """
        If any values are given as None then that value will not be changed on the given field.

        :param prepend_data_type: If true, prepends the data type name of the field to the data field name. For example,
            if a field has a data type name X and a data field name Y, then the field name would become "X.Y". This is
            useful for cases where you have the same field name on two different data types and want to distinguish one
            or both of them.
        :param display_name: Change the display name.
        :param required: Change the required status.
        :param editable: Change the editable status.
        :param visible: Change the visible status.
        :param key_field: Change the key field status.
        :param column_width: Change the column width.
        """
        self.prepend_data_type = prepend_data_type
        self.display_name = display_name
        self.required = required
        self.editable = editable
        self.visible = visible
        self.key_field = key_field
        self.column_width = column_width

    def modify_field(self, field: AbstractVeloxFieldDefinition) -> AbstractVeloxFieldDefinition:
        """
        Apply modifications to a given field.

        :param field: The field to modify.
        :return: A copy of the input field with the modifications applied.
        """
        field = copy_field(field)
        if self.prepend_data_type is True:
            field._data_field_name = field.data_type_name + "." + field.data_field_name
        if self.display_name is not None:
            field.display_name = self.display_name
        if self.required is not None:
            field.required = self.required
        if self.editable is not None:
            field.editable = self.editable
        if self.visible is not None:
            field.visible = self.visible
        if self.key_field is not None:
            field.key_field = self.key_field
        if self.column_width is not None:
            field.default_table_column_width = self.column_width
        return field


def copy_field(field: AbstractVeloxFieldDefinition) -> AbstractVeloxFieldDefinition:
    """
    Create a copy of a given field definition. This is used to modify field definitions from the server for existing
    data types without also modifying the field definition in the cache.
    """
    return FieldDefinitionParser.to_field_definition(field.to_json())
