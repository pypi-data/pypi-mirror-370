from collections.abc import Iterable
from typing import Any

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.Protocols import ElnExperimentProtocol, ElnEntryStep
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedRecordModel, WrappedType, WrapperField

from sapiopycommons.general.exceptions import SapioException

FieldValue = int | float | str | bool | None
"""Allowable values for fields in the system."""
RecordModel = PyRecordModel | WrappedRecordModel
"""Different forms that a record model could take."""
SapioRecord = DataRecord | RecordModel
"""A record could be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel (WrappedType)."""
RecordIdentifier = SapioRecord | int
"""A RecordIdentifier is either a record type or an integer for the record's record ID."""
DataTypeIdentifier = SapioRecord | type[WrappedType] | str
"""A DataTypeIdentifier is either a SapioRecord, a record model wrapper type, or a string."""
FieldIdentifier = WrapperField | str | tuple[str, FieldType]
"""A FieldIdentifier is either wrapper field from a record model wrapper, a string, or a tuple of string
and field type."""
FieldIdentifierKey = WrapperField | str
"""A FieldIdentifierKey is a FieldIdentifier, except it can't be a tuple, s tuples can't be used as keys in
dictionaries.."""
HasFieldWrappers = type[WrappedType] | WrappedRecordModel
"""An identifier for classes that have wrapper fields."""
ExperimentIdentifier = ElnExperimentProtocol | ElnExperiment | int
"""An ExperimentIdentifier is either an experiment protocol, experiment, or an integer for the experiment's notebook
ID."""
ExperimentEntryIdentifier = ElnEntryStep | ExperimentEntry | int
"""An ExperimentEntryIdentifier is either an ELN entry step, experiment entry, or an integer for the entry's ID."""
FieldMap = dict[str, FieldValue]
"""A field map is simply a dict of data field names to values. The purpose of aliasing this is to help distinguish
any random dict in a webhook from one which is explicitly used for record fields."""
FieldIdentifierMap = dict[FieldIdentifierKey, FieldValue]
"""A field identifier map is the same thing as a field map, except the keys can be field identifiers instead
of just strings. Note that although one of the allowed field identifiers is a tuple, you can't use tuples as
keys in a dictionary."""
UserIdentifier = SapioWebhookContext | SapioUser
"""An identifier for classes from which a user object can be used for sending requests."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class AliasUtil:
    @staticmethod
    def to_data_record(record: SapioRecord) -> DataRecord:
        """
        Convert a single DataRecord, PyRecordModel, or WrappedRecordModel to just a DataRecord.

        :return: The DataRecord of the input SapioRecord.
        """
        return record if isinstance(record, DataRecord) else record.get_data_record()

    @staticmethod
    def to_data_records(records: Iterable[SapioRecord]) -> list[DataRecord]:
        """
        Convert a list of variables that could either be DataRecords, PyRecordModels,
        or WrappedRecordModels to just DataRecords.

        :return: A list of DataRecords for the input records.
        """
        return [(x if isinstance(x, DataRecord) else x.get_data_record()) for x in records]

    @staticmethod
    def to_record_ids(records: Iterable[RecordIdentifier]) -> list[int]:
        """
        Convert a list of variables that could either be integers, DataRecords, PyRecordModels,
        or WrappedRecordModels to just integers (taking the record ID from the records).

        :return: A list of record IDs for the input records.
        """
        return [(AliasUtil.to_record_id(x)) for x in records]

    @staticmethod
    def to_record_id(record: RecordIdentifier):
        """
        Convert a single variable that could be either an integer, DataRecord, PyRecordModel,
        or WrappedRecordModel to just an integer (taking the record ID from the record).

        :return: A record ID for the input record.
        """
        return record if isinstance(record, int) else record.record_id

    @staticmethod
    def to_data_type_name(value: DataTypeIdentifier, convert_eln_dts: bool = True) -> str:
        """
        Convert a given value to a data type name.

        :param value: A value which is a string, record, or record model type.
        :param convert_eln_dts: If true, convert ELN data types to their base data type name.
        :return: A string of the data type name of the input value.
        """
        if isinstance(value, SapioRecord):
            value = value.data_type_name
        elif not isinstance(value, str):
            value = value.get_wrapper_data_type_name()
        if convert_eln_dts and ElnBaseDataType.is_eln_type(value):
            return ElnBaseDataType.get_base_type(value).data_type_name
        return value

    @staticmethod
    def to_data_type_names(values: Iterable[DataTypeIdentifier], return_set: bool = False,
                           convert_eln_dts: bool = True) -> list[str] | set[str]:
        """
        Convert a given iterable of values to a list or set of data type names.

        :param values: An iterable of values which are strings, records, or record model types.
        :param return_set: If true, return a set instead of a list.
        :param convert_eln_dts: If true, convert ELN data types to their base data type name.
        :return: A list or set of strings of the data type name of the input value.
        """
        values = [AliasUtil.to_data_type_name(x, convert_eln_dts) for x in values]
        return set(values) if return_set else values

    @staticmethod
    def to_singular_data_type_name(values: Iterable[DataTypeIdentifier], convert_eln_dts: bool = True) -> str:
        """
        Convert a given iterable of values to a singular data type name that they share. Throws an exception if more
        than one data type name exists in the provided list of identifiers.

        :param values: An iterable of values which are strings, records, or record model types.
        :param convert_eln_dts: If true, convert ELN data types to their base data type name.
        :return: The single data type name that the input vales share. Returns an empty string if an empty iterable
            was provided.
        """
        if not values:
            return ""
        data_types: set[str] = AliasUtil.to_data_type_names(values, True, convert_eln_dts)
        if len(data_types) > 1:
            raise SapioException(f"Provided values contain multiple data types: {data_types}. "
                                 f"Only expecting a single data type.")
        return data_types.pop()

    @staticmethod
    def to_data_field_name(value: FieldIdentifier) -> str:
        """
        Convert a string or WrapperField to a data field name string.

        :param value: A string or WrapperField.
        :return: A string of the data field name of the input value.
        """
        if isinstance(value, tuple):
            return value[0]
        if isinstance(value, WrapperField):
            return value.field_name
        return value

    @staticmethod
    def to_data_field_names(values: Iterable[FieldIdentifier]) -> list[str]:
        """
        Convert an iterable of strings or WrapperFields to a list of data field name strings.

        :param values: An iterable of strings or WrapperFields.
        :return: A list of strings of the data field names of the input values.
        """
        return [AliasUtil.to_data_field_name(x) for x in values]

    @staticmethod
    def to_data_field_names_dict(values: dict[FieldIdentifierKey, Any]) -> dict[str, Any]:
        """
        Take a dictionary whose keys are field identifiers and convert them all to strings for the data field name.

        :param values: A dictionary of field identifiers to field values.
        :return: A dictionary of strings of the data field names to field values for the input values.
        """
        ret_dict: dict[str, FieldValue] = {}
        for field, value in values.items():
            ret_dict[AliasUtil.to_data_field_name(field)] = value
        return ret_dict

    @staticmethod
    def to_data_field_names_list_dict(values: list[dict[FieldIdentifierKey, Any]]) -> list[dict[str, Any]]:
        ret_list: list[dict[str, Any]] = []
        for field_map in values:
            ret_list.append(AliasUtil.to_data_field_names_dict(field_map))
        return ret_list

    @staticmethod
    def to_field_type(field: FieldIdentifier, data_type: HasFieldWrappers | None = None) -> FieldType:
        """
        Convert a given field identifier to the field type for that field.

        :param field: A string or WrapperField.
        :param data_type: If the field is provided as a string, then a record model wrapper or wrapped record model
            must be provided to determine the field type.
        :return: The field type of the given field.
        """
        if isinstance(field, tuple):
            return field[1]
        if isinstance(field, WrapperField):
            return field.field_type
        for var in dir(data_type):
            attr = getattr(data_type, var)
            if isinstance(attr, WrapperField) and attr.field_name == field:
                return attr.field_type
        raise SapioException(f"The wrapper of data type \"{data_type.get_wrapper_data_type_name()}\" doesn't have a "
                             f"field with the name \"{field}\",")

    @staticmethod
    def to_field_map_lists(records: Iterable[SapioRecord]) -> list[FieldMap]:
        """
        Convert a list of variables that could either be DataRecords, PyRecordModels,
        or WrappedRecordModels to a list of their field maps.

        :return: A list of field maps for the input records.
        """
        field_map_list: list[FieldMap] = []
        for record in records:
            if isinstance(record, DataRecord):
                # noinspection PyTypeChecker
                field_map_list.append(record.get_fields())
            else:
                field_map_list.append(record.fields.copy_to_dict())
        return field_map_list

    @staticmethod
    def to_notebook_id(experiment: ExperimentIdentifier) -> int:
        """
        Convert an object that identifies an ELN experiment to its notebook ID.

        :return: The notebook ID for the experiment identifier.
        """
        if isinstance(experiment, int):
            return experiment
        if isinstance(experiment, ElnExperiment):
            return experiment.notebook_experiment_id
        return experiment.get_id()

    @staticmethod
    def to_notebook_ids(experiments: list[ExperimentIdentifier]) -> list[int]:
        """
        Convert a list of objects that identify ELN experiments to their notebook IDs.

        :return: The list of notebook IDs for the experiment identifiers.
        """
        notebook_ids: list[int] = []
        for experiment in experiments:
            notebook_ids.append(AliasUtil.to_notebook_id(experiment))
        return notebook_ids

    @staticmethod
    def to_entry_id(entry: ExperimentEntryIdentifier) -> int:
        """
        Convert an object that identifies an experiment entry to its entry ID.

        :return: The entry ID for the entry identifier.
        """
        if isinstance(entry, int):
            return entry
        elif isinstance(entry, ExperimentEntry):
            return entry.entry_id
        elif isinstance(entry, ElnEntryStep):
            return entry.get_id()
        raise SapioException(f"Unrecognized entry identifier of type {type(entry)}")

    @staticmethod
    def to_entry_ids(entries: list[ExperimentEntryIdentifier]) -> list[int]:
        """
        Convert a list of objects that identify experiment entries to their entry IDs.

        :return: The list of entry IDs for the entry identifiers.
        """
        entry_ids: list[int] = []
        for entry in entries:
            entry_ids.append(AliasUtil.to_entry_id(entry))
        return entry_ids

    @staticmethod
    def to_sapio_user(context: UserIdentifier) -> SapioUser:
        """
        Convert an object that could be either a SapioUser or SapioWebhookContext to just a SapioUser.

        :return: A SapioUser object.
        """
        return context if isinstance(context, SapioUser) else context.user
