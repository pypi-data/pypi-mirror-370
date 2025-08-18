from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.aliases import FieldMap, AliasUtil, DataTypeIdentifier
from sapiopycommons.general.exceptions import SapioException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class ElnRuleHandler:
    """
    A class which helps with the parsing and navigation of the ELN rule result map of a webhook context.
    """
    __context: SapioWebhookContext
    """The context that this handler is working from."""

    __inst_man: RecordModelInstanceManager
    """The record model instance manager, used for wrapping the data records as record models."""

    # Reformatted and cached version of the Velox ELN rule result map for easier handling.
    __records: dict[str, set[DataRecord]]
    """A mapping of data type to the set of data records from the context that match that data type."""
    __entry_to_records: dict[str, dict[str, set[DataRecord]]]
    """A mapping of entry name to the sets of data records for that entry, each set of records being mapped by its
    data type."""
    __field_maps: dict[str, dict[int, FieldMap]]
    """A mapping of data type to the field maps from the context that match that data type. In order to prevent
    duplicate field maps, each field map is in a dict keyed by the RecordId field in the field map, since field maps
    are just dictionaries and dictionaries aren't hashable and therefore can't go in a set."""
    __entry_to_field_maps: dict[str, dict[str, dict[int, FieldMap]]]
    """A mapping of entry name to the lists of field maps for that entry, each grouping of field maps being mapped by
    its data type."""

    __instances: WeakValueDictionary[SapioUser, ElnRuleHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: SapioWebhookContext):
        if context.velox_eln_rule_result_map is None:
            raise SapioException("No Velox ELN rule result map in context for ElnRuleHandler to parse.")
        user = context if isinstance(context, SapioUser) else context.user
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, context: SapioWebhookContext):
        if self.__initialized:
            return
        self.__initialized = True

        if context.velox_eln_rule_result_map is None:
            raise SapioException("No Velox ELN rule result map in context for ElnRuleHandler to parse.")
        self.__context = context
        self.__inst_man = RecordModelManager(context.user).instance_manager
        self.__cache_records()

    def __cache_records(self) -> None:
        """
        Cache the records from the context into dictionaries. Two caches are created. One cache maps the data type of
        each record to a set of all records of that data type. The other cache maps the entry that the records come
        from to another dict that maps the data types to the records of that type.
        Doesn't cache any relationship info from the VeloxRuleType of the rule results.
        """
        self.__records = {}
        self.__entry_to_records = {}
        # Each entry in the context has a list of results for that entry.
        for entry, entry_results in self.__context.velox_eln_rule_result_map.items():
            # Keep track of the records for this specific entry.
            entry_dict: dict[str, set[DataRecord]] = {}
            # Entry results consist of a record ID of the record in the entry and a list of results tied to that record.
            for record_result in entry_results:
                # The list of results for a record consist of a list of data records and a VeloxType that specifies
                # how the records in the list relate to the main record.
                for result in record_result.rule_result_list:
                    # For the purposes of caching, we don't care about the VeloxType.
                    for record in result.data_records:
                        # Get the data type of this record. If this is an ELN type, ignore the digits.
                        data_type: str = record.data_type_name
                        # PR-46331: Ensure that all ELN types are converted to their base data type name.
                        if ElnBaseDataType.is_eln_type(data_type):
                            data_type = ElnBaseDataType.get_base_type(data_type).data_type_name
                        # Update the list of records of this type that exist so far globally.
                        self.__records.setdefault(data_type, set()).add(record)
                        # Do the same for the list of records of this type for this specific entry.
                        entry_dict.setdefault(data_type, set()).add(record)
            # Update the records for this entry.
            self.__entry_to_records.update({entry: entry_dict})

        self.__field_maps = {}
        self.__entry_to_field_maps = {}
        # Repeat the same thing for the field map results.
        for entry, entry_results in self.__context.velox_eln_rule_field_map_result_map.items():
            entry_dict: dict[str, dict[int, FieldMap]] = {}
            for record_result in entry_results:
                for result in record_result.velox_type_rule_field_map_result_list:
                    data_type: str = result.velox_type_pojo.data_type_name
                    if ElnBaseDataType.is_eln_type(data_type):
                        data_type = ElnBaseDataType.get_base_type(data_type).data_type_name
                    for field_map in result.field_map_list:
                        rec_id: int = field_map.get("RecordId")
                        self.__field_maps.setdefault(data_type, {}).update({rec_id: field_map})
                        entry_dict.setdefault(data_type, {}).update({rec_id: field_map})
            self.__entry_to_field_maps.update({entry: entry_dict})

    def get_entry_names(self) -> list[str]:
        """
        :return: A list of the entry names that may be used with the get_records and get_models functions. These are the
            entries from the experiment that the records in the rule context originate from.
        """
        return list(self.__entry_to_records.keys())

    def get_field_maps_entry_names(self) -> list[str]:
        """
        :return: A list of the entry names that may be used with the get_field_maps function. These are the
            entries from the experiment that the field maps in the rule context originate from.
        """
        return list(self.__entry_to_field_maps.keys())

    def get_records(self, data_type: DataTypeIdentifier, entry: str | None = None) -> list[DataRecord]:
        """
        Get records from the cached context with the given data type. Capable of being filtered to searching within
        the context of an entry name. If the given data type or entry does not exist in the context,
        returns an empty list.

        :param data_type: The data type of the records to return.
        :param entry: The name of the entry to grab the records from. If None, returns the records that match the data
            type from every entry. If an entry is provided, but it does not exist in the context, returns an empty list.
        :return: The records from the context that match the input parameters.
        """
        data_type: str = AliasUtil.to_data_type_name(data_type)
        records: dict[str, set[DataRecord]] = self.__entry_to_records.get(entry, {}) if entry else self.__records
        return list(records.get(data_type, []))

    # FR-46701: Add functions to the rule handlers for accessing the field maps of inaccessible records in the context.
    def get_field_maps(self, data_type: DataTypeIdentifier, entry: str | None = None) -> list[FieldMap]:
        """
        Get field maps from the cached context with the given data type. Capable of being filtered to searching within
        the context of an entry name. If the given data type or entry does not exist in the context,
        returns an empty list.

        Field maps will only exist in the context if the data record that the fields are from is no longer accessible
        to the user. This can occur because the data record was deleted, or because the user does not have access to the
        record due to ACL.

        :param data_type: The data type of the field maps to return.
        :param entry: The name of the entry to grab the field maps from. If None, returns the field maps that match the
            data type from every entry. If an entry is provided, but it does not exist in the context, returns an empty
            list.
        :return: The field maps from the context that match the input parameters.
        """
        data_type: str = AliasUtil.to_data_type_name(data_type)
        field_maps: dict[str, dict[int, FieldMap]] = self.__entry_to_field_maps.get(entry, {}) if entry else self.__field_maps
        return list(field_maps.get(data_type, {}).values())

    def get_models(self, wrapper_type: type[WrappedType], entry: str | None = None) -> list[WrappedType]:
        """
        Get record models from the cached context with the given data type. Capable of being filtered to searching
        within the context of an entry name. If the given data type or entry does not exist in the context,
        returns an empty list.

        :param wrapper_type: The record model wrapper to use.
        :param entry: The name of the entry to grab the records from. If None, returns the records that match the data
            type from every entry. If an entry is provided, but it does not exist in the context, returns an empty list.
        :return: The record models from the context that match the input parameters.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        return self.__inst_man.add_existing_records_of_type(self.get_records(dt, entry), wrapper_type)
