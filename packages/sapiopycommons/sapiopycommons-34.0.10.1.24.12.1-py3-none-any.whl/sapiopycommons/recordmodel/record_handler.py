from __future__ import annotations

from collections.abc import Iterable
from weakref import WeakValueDictionary

from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, RawReportTerm, ReportColumn
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.DataRecordPaging import DataRecordPojoPageCriteria
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.utils.autopaging import QueryDataRecordsAutoPager, QueryDataRecordByIdListAutoPager, \
    QueryAllRecordsOfTypeAutoPager
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType, WrappedRecordModel
from sapiopylib.rest.utils.recordmodel.RelationshipPath import RelationshipPath, RelationshipNode, \
    RelationshipNodeType
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager

from sapiopycommons.general.aliases import RecordModel, SapioRecord, FieldMap, FieldIdentifier, AliasUtil, \
    FieldIdentifierMap, FieldValue, UserIdentifier, FieldIdentifierKey
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.general.exceptions import SapioException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class RecordHandler:
    """
    A collection of shorthand methods for dealing with the various record managers.
    """
    user: SapioUser
    dr_man: DataRecordManager
    rec_man: RecordModelManager
    inst_man: RecordModelInstanceManager
    rel_man: RecordModelRelationshipManager
    an_man: RecordModelAncestorManager

    __instances: WeakValueDictionary[SapioUser, RecordHandler] = WeakValueDictionary()
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
        self.user = AliasUtil.to_sapio_user(context)
        if self.__initialized:
            return
        self.__initialized = True

        self.user = context if isinstance(context, SapioUser) else context.user
        self.dr_man = DataRecordManager(self.user)
        self.rec_man = RecordModelManager(self.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = RecordModelAncestorManager(self.rec_man)

    def wrap_model(self, record: DataRecord, wrapper_type: type[WrappedType]) -> WrappedType:
        """
        Shorthand for adding a single data record as a record model.

        :param record: The data record to wrap.
        :param wrapper_type: The record model wrapper to use.
        :return: The record model for the input.
        """
        self.__verify_data_type([record], wrapper_type)
        return self.inst_man.add_existing_record_of_type(record, wrapper_type)

    def wrap_models(self, records: Iterable[DataRecord], wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Shorthand for adding a list of data records as record models.

        :param records: The data records to wrap.
        :param wrapper_type: The record model wrapper to use.
        :return: The record models for the input.
        """
        self.__verify_data_type(records, wrapper_type)
        return self.inst_man.add_existing_records_of_type(list(records), wrapper_type)

    def query_models(self, wrapper_type: type[WrappedType], field: FieldIdentifier, value_list: Iterable[FieldValue],
                     page_limit: int | None = None, page_size: int | None = None) -> list[WrappedType]:
        """
        Shorthand for using the data record manager to query for a list of data records by field value
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param field: The field to query on.
        :param value_list: The values of the field to query on.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_models_with_criteria(wrapper_type, field, value_list, criteria, page_limit)[0]

    def query_and_map_models(self, wrapper_type: type[WrappedType], field: FieldIdentifier,
                             value_list: Iterable[FieldValue], page_limit: int | None = None,
                             page_size: int | None = None, *, mapping_field: FieldIdentifier | None = None) \
            -> dict[FieldValue, list[WrappedType]]:
        """
        Shorthand for using query_models to search for records given values on a specific field and then using
        map_by_field to turn the returned list into a dictionary mapping field values to records.

        :param wrapper_type: The record model wrapper to use.
        :param field: The field to query and map on.
        :param value_list: The values of the field to query on.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :param mapping_field: If provided, use this field to map against instead of the field that was queried on.
        :return: The record models for the queried records mapped by field values to the records with that value.
        """
        if mapping_field is None:
            mapping_field = field
        return self.map_by_field(self.query_models(wrapper_type, field, value_list, page_limit, page_size),
                                 mapping_field)

    def query_and_unique_map_models(self, wrapper_type: type[WrappedType], field: FieldIdentifier,
                                    value_list: Iterable[FieldValue], page_limit: int | None = None,
                                    page_size: int | None = None, *, mapping_field: FieldIdentifier | None = None) \
            -> dict[FieldValue, WrappedType]:
        """
        Shorthand for using query_models to search for records given values on a specific field and then using
        map_by_unique_field to turn the returned list into a dictionary mapping field values to records.
        If any two records share the same field value, throws an exception.

        :param wrapper_type: The record model wrapper to use.
        :param field: The field to query and map on.
        :param value_list: The values of the field to query on.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :param mapping_field: If provided, use this field to map against instead of the field that was queried on.
        :return: The record models for the queried records mapped by field values to the record with that value.
        """
        if mapping_field is None:
            mapping_field = field
        return self.map_by_unique_field(self.query_models(wrapper_type, field, value_list, page_limit, page_size),
                                        mapping_field)

    def query_models_with_criteria(self, wrapper_type: type[WrappedType], field: FieldIdentifier,
                                   value_list: Iterable[FieldValue],
                                   paging_criteria: DataRecordPojoPageCriteria | None = None,
                                   page_limit: int | None = None) \
            -> tuple[list[WrappedType], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for a list of data records by field value
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param field: The field to query on.
        :param value_list: The values of the field to query on.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        field: str = AliasUtil.to_data_field_name(field)
        pager = QueryDataRecordsAutoPager(dt, field, list(value_list), self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_id(self, wrapper_type: type[WrappedType], ids: Iterable[int],
                           page_limit: int | None = None, page_size: int | None = None) -> list[WrappedType]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param ids: The list of record IDs to query.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_models_by_id_with_criteria(wrapper_type, ids, criteria, page_limit)[0]

    def query_models_by_id_with_criteria(self, wrapper_type: type[WrappedType], ids: Iterable[int],
                                         paging_criteria: DataRecordPojoPageCriteria | None = None,
                                         page_limit: int | None = None) \
            -> tuple[list[WrappedType], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param ids: The list of record IDs to query.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        pager = QueryDataRecordByIdListAutoPager(dt, list(ids), self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_id_and_map(self, wrapper_type: type[WrappedType], ids: Iterable[int],
                                   page_limit: int | None = None, page_size: int | None = None) \
            -> dict[int, WrappedType]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a dictionary of record ID to the record model for that ID.

        :param wrapper_type: The record model wrapper to use.
        :param ids: The list of record IDs to query.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records mapped in a dictionary by their record ID.
        """
        return {x.record_id: x for x in self.query_models_by_id(wrapper_type, ids, page_limit, page_size)}

    def query_all_models(self, wrapper_type: type[WrappedType], page_limit: int | None = None,
                         page_size: int | None = None) -> list[WrappedType]:
        """
        Shorthand for using the data record manager to query for all data records of a given type
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_all_models_with_criteria(wrapper_type, criteria, page_limit)[0]

    def query_all_models_with_criteria(self, wrapper_type: type[WrappedType],
                                       paging_criteria: DataRecordPojoPageCriteria | None = None,
                                       page_limit: int | None = None) \
            -> tuple[list[WrappedType], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for all data records of a given type
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        pager = QueryAllRecordsOfTypeAutoPager(dt, self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_report(self, wrapper_type: type[WrappedType],
                               report_name: str | RawReportTerm | CustomReportCriteria,
                               filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None = None,
                               page_limit: int | None = None,
                               page_size: int | None = None,
                               page_number: int | None = None) -> list[WrappedType]:
        """
        Run a report and use the results of that report to query for and return the records in the report results.
        First runs the report, then runs a data record manager query on the results of the custom report.

        Will throw an exception if given the name of a system report that does not have a RecordId column.
        Quick and custom reports are guaranteed to have a record ID column.

        Any given custom report criteria should only have columns from a single data type.

        :param wrapper_type: The record model wrapper to use.
        :param report_name: The name of a system report, or a raw report term for a quick report, or custom report
            criteria for a custom report.
        :param filters: If provided, filter the results of the report using the given mapping of headers to values to
            filter on. This filtering is done before the records are queried.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages.
        :param page_size: The size of each page of results in the search. If None, the page size is set by the server.
            If the input report is a custom report criteria, uses the value from the criteria, unless this value is
            not None, in which case it overwrites the given report's value.
        :param page_number: The page number to start the search from, If None, starts on the first page.
            If the input report is a custom report criteria, uses the value from the criteria, unless this value is
            not None, in which case it overwrites the given report's value. Note that the number of the first page is 0.
        :return: The record models for the queried records that matched the given report.
        """
        if isinstance(report_name, str):
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_system_report(self.user, report_name, filters,
                                                                                      page_limit, page_size, page_number)
        elif isinstance(report_name, RawReportTerm):
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_quick_report(self.user, report_name, filters,
                                                                                     page_limit, page_size, page_number)
        elif isinstance(report_name, CustomReportCriteria):
            dt: str = wrapper_type.get_wrapper_data_type_name()
            # Ensure that the root data type is the one we're looking for.
            report_name.root_data_type = dt
            # Raise an exception if any column in the report doesn't match the given data type.
            if any([x.data_type_name != dt for x in report_name.column_list]):
                raise SapioException("You may only query records from a report containing columns from that data type.")
            # Enforce that the given custom report has a record ID column.
            if not any([x.data_type_name == dt and x.data_field_name == "RecordId" for x in report_name.column_list]):
                report_name.column_list.append(ReportColumn(dt, "RecordId", FieldType.LONG))
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_custom_report(self.user, report_name, filters,
                                                                                      page_limit, page_size, page_number)
        else:
            raise SapioException("Unrecognized report object.")

        # Using the bracket accessor because we want to throw an exception if RecordId doesn't exist in the report.
        # This should only possibly be the case with system reports, as quick reports will include the record ID and
        # we forced any given custom report to have a record ID column.
        ids: list[int] = [row["RecordId"] for row in results]
        return self.query_models_by_id(wrapper_type, ids)

    def add_model(self, wrapper_type: type[WrappedType]) -> WrappedType:
        """
        Shorthand for using the instance manager to add a new record model of the given type.

        :param wrapper_type: The record model wrapper to use.
        :return: The newly added record model.
        """
        return self.inst_man.add_new_record_of_type(wrapper_type)

    def add_models(self, wrapper_type: type[WrappedType], num: int) -> list[WrappedType]:
        """
        Shorthand for using the instance manager to add new record models of the given type.

        :param wrapper_type: The record model wrapper to use.
        :param num: The number of models to create.
        :return: The newly added record models.
        """
        return self.inst_man.add_new_records_of_type(num, wrapper_type)

    def add_models_with_data(self, wrapper_type: type[WrappedType], fields: list[FieldIdentifierMap]) \
            -> list[WrappedType]:
        """
        Shorthand for using the instance manager to add new models of the given type, and then initializing all those
        models with the given fields.

        :param wrapper_type: The record model wrapper to use.
        :param fields: A list of field maps to initialize the record models with.
        :return: The newly added record models with the provided fields set. The records will be in the same order as
            the fields in the fields list.
        """
        fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(fields)
        models: list[WrappedType] = self.add_models(wrapper_type, len(fields))
        for model, field_list in zip(models, fields):
            model.set_field_values(field_list)
        return models

    def find_or_add_model(self, wrapper_type: type[WrappedType], primary_identifier: FieldIdentifier,
                          id_value: FieldValue, secondary_identifiers: FieldIdentifierMap | None = None) -> WrappedType:
        """
        Find a unique record that matches the given field values. If no such records exist, add a record model to the
        cache with the identifying fields set to the desired values. This record will be created in the system when
        you store and commit changes. If more than one record with the identifying values exists, throws an exception.

        The record is searched for using the primary identifier field name and value. If multiple records are returned
        by the query on this primary identifier, then the secondary identifiers are used to filter the results.

        Makes a webservice call to query for the existing record.

        :param wrapper_type: The record model wrapper to use.
        :param primary_identifier: The data field name of the field to search on.
        :param id_value: The value of the identifying field to search for.
        :param secondary_identifiers: Optional fields used to filter the records that are returned after searching on
            the primary identifier.
        :return: The record model with the identifying field value, either pulled from the system or newly created.
        """
        # PR-46335: Initialize the secondary identifiers parameter if None is provided to avoid an exception.
        # If no secondary identifiers were provided, use an empty dictionary.
        if secondary_identifiers is None:
            secondary_identifiers = {}

        primary_identifier: str = AliasUtil.to_data_field_name(primary_identifier)
        secondary_identifiers: FieldMap = AliasUtil.to_data_field_names_dict(secondary_identifiers)
        unique_record: WrappedType | None = self.__find_model(wrapper_type, primary_identifier, id_value,
                                                              secondary_identifiers)
        # If a unique record matched the identifiers, return it.
        if unique_record is not None:
            return unique_record

        # If none of the results matched the identifiers, create a new record with all identifiers set.
        # Put the primary identifier and value into the secondary identifiers list and use that as the fields map
        # for this new record.
        secondary_identifiers.update({primary_identifier: id_value})
        return self.add_models_with_data(wrapper_type, [secondary_identifiers])[0]

    def create_models(self, wrapper_type: type[WrappedType], num: int) -> list[WrappedType]:
        """
        Shorthand for creating new records via the data record manager and then returning them as wrapped
        record models. Useful in cases where your record model needs to have a valid record ID.

        Makes a webservice call to create the data records.

        :param wrapper_type: The record model wrapper to use.
        :param num: The number of new records to create.
        :return: The newly created record models.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        return self.wrap_models(self.dr_man.add_data_records(dt, num), wrapper_type)

    def create_models_with_data(self, wrapper_type: type[WrappedType], fields: list[FieldIdentifierMap]) \
            -> list[WrappedType]:
        """
        Shorthand for creating new records via the data record manager with field data to initialize the records with
        and then returning them as wrapped record models. Useful in cases where your record model needs to have a valid
        record ID.

        Makes a webservice call to create the data records.

        :param wrapper_type: The record model wrapper to use.
        :param fields: The field map list to initialize the new data records with.
        :return: The newly created record models.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(fields)
        return self.wrap_models(self.dr_man.add_data_records_with_data(dt, fields), wrapper_type)

    def find_or_create_model(self, wrapper_type: type[WrappedType], primary_identifier: FieldIdentifier,
                             id_value: FieldValue, secondary_identifiers: FieldIdentifierMap | None = None) \
            -> WrappedType:
        """
        Find a unique record that matches the given field values. If no such records exist, create one with the
        identifying fields set to the desired values. If more than one record with the identifying values exists,
        throws an exception.

        The record is searched for using the primary identifier field name and value. If multiple records are returned
        by the query on this primary identifier, then the secondary identifiers are used to filter the results.

        Makes a webservice call to query for the existing record. Makes an additional webservice call if the record
        needs to be created.

        :param wrapper_type: The record model wrapper to use.
        :param primary_identifier: The data field name of the field to search on.
        :param id_value: The value of the identifying field to search for.
        :param secondary_identifiers: Optional fields used to filter the records that are returned after searching on
            the primary identifier.
        :return: The record model with the identifying field value, either pulled from the system or newly created.
        """
        # PR-46335: Initialize the secondary identifiers parameter if None is provided to avoid an exception.
        # If no secondary identifiers were provided, use an empty dictionary.
        if secondary_identifiers is None:
            secondary_identifiers = {}

        primary_identifier: str = AliasUtil.to_data_field_name(primary_identifier)
        secondary_identifiers: FieldMap = AliasUtil.to_data_field_names_dict(secondary_identifiers)
        unique_record: WrappedType | None = self.__find_model(wrapper_type, primary_identifier, id_value,
                                                              secondary_identifiers)
        # If a unique record matched the identifiers, return it.
        if unique_record is not None:
            return unique_record

        # If none of the results matched the identifiers, create a new record with all identifiers set.
        # Put the primary identifier and value into the secondary identifiers list and use that as the fields map
        # for this new record.
        secondary_identifiers.update({primary_identifier: id_value})
        return self.create_models_with_data(wrapper_type, [secondary_identifiers])[0]

    @staticmethod
    def map_to_parent(models: Iterable[RecordModel], parent_type: type[WrappedType]) -> dict[RecordModel, WrappedType]:
        """
        Map a list of record models to a single parent of a given type. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper of the parent.
        :return: A dict[ModelType, ParentType]. If an input model doesn't have a parent of the given parent type, then
            it will map to None.
        """
        return_dict: dict[RecordModel, WrappedType] = {}
        for model in models:
            return_dict[model] = model.get_parent_of_type(parent_type)
        return return_dict

    @staticmethod
    def map_to_parents(models: Iterable[RecordModel], parent_type: type[WrappedType]) \
            -> dict[RecordModel, list[WrappedType]]:
        """
        Map a list of record models to a list parents of a given type. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper of the parents.
        :return: A dict[ModelType, list[ParentType]]. If an input model doesn't have a parent of the given parent type,
            then it will map to an empty list.
        """
        return_dict: dict[RecordModel, list[WrappedType]] = {}
        for model in models:
            return_dict[model] = model.get_parents_of_type(parent_type)
        return return_dict

    @staticmethod
    def map_by_parent(models: Iterable[RecordModel], parent_type: type[WrappedType]) \
            -> dict[WrappedType, RecordModel]:
        """
        Take a list of record models and map them by their parent. Essentially an inversion of map_to_parent.
        If two records share the same parent, an exception will be thrown. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper of the parents.
        :return: A dict[ParentType, ModelType]. If an input model doesn't have a parent of the given parent type,
            then it will not be in the resulting dictionary.
        """
        to_parent: dict[RecordModel, WrappedType] = RecordHandler.map_to_parent(models, parent_type)
        by_parent: dict[WrappedType, RecordModel] = {}
        for record, parent in to_parent.items():
            if parent is None:
                continue
            if parent in by_parent:
                raise SapioException(f"Parent {parent.data_type_name} {parent.record_id} encountered more than once "
                                     f"in models list.")
            by_parent[parent] = record
        return by_parent

    @staticmethod
    def map_by_parents(models: Iterable[RecordModel], parent_type: type[WrappedType]) \
            -> dict[WrappedType, list[RecordModel]]:
        """
        Take a list of record models and map them by their parents. Essentially an inversion of map_to_parents. Input
        models that share a parent will end up in the same list. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper of the parents.
        :return: A dict[ParentType, list[ModelType]]. If an input model doesn't have a parent of the given parent type,
            then it will not be in the resulting dictionary.
        """
        to_parents: dict[RecordModel, list[WrappedType]] = RecordHandler.map_to_parents(models, parent_type)
        by_parents: dict[WrappedType, list[RecordModel]] = {}
        for record, parents in to_parents.items():
            for parent in parents:
                by_parents.setdefault(parent, []).append(record)
        return by_parents

    @staticmethod
    def map_to_child(models: Iterable[RecordModel], child_type: type[WrappedType]) -> dict[RecordModel, WrappedType]:
        """
        Map a list of record models to a single child of a given type. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper of the child.
        :return: A dict[ModelType, ChildType]. If an input model doesn't have a child of the given child type, then
            it will map to None.
        """
        return_dict: dict[RecordModel, WrappedType] = {}
        for model in models:
            return_dict[model] = model.get_child_of_type(child_type)
        return return_dict

    @staticmethod
    def map_to_children(models: Iterable[RecordModel], child_type: type[WrappedType]) \
            -> dict[RecordModel, list[WrappedType]]:
        """
        Map a list of record models to a list children of a given type. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper of the children.
        :return: A dict[ModelType, list[ChildType]]. If an input model doesn't have children of the given child type,
            then it will map to an empty list.
        """
        return_dict: dict[RecordModel, list[WrappedType]] = {}
        for model in models:
            return_dict[model] = model.get_children_of_type(child_type)
        return return_dict

    @staticmethod
    def map_by_child(models: Iterable[RecordModel], child_type: type[WrappedType]) \
            -> dict[WrappedType, RecordModel]:
        """
        Take a list of record models and map them by their children. Essentially an inversion of map_to_child.
        If two records share the same child, an exception will be thrown. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper of the children.
        :return: A dict[ChildType, ModelType]. If an input model doesn't have a child of the given child type,
            then it will not be in the resulting dictionary.
        """
        to_child: dict[RecordModel, WrappedType] = RecordHandler.map_to_child(models, child_type)
        by_child: dict[WrappedType, RecordModel] = {}
        for record, child in to_child.items():
            if child is None:
                continue
            if child in by_child:
                raise SapioException(f"Child {child.data_type_name} {child.record_id} encountered more than once "
                                     f"in models list.")
            by_child[child] = record
        return by_child

    @staticmethod
    def map_by_children(models: Iterable[RecordModel], child_type: type[WrappedType]) \
            -> dict[WrappedType, list[RecordModel]]:
        """
        Take a list of record models and map them by their children. Essentially an inversion of map_to_children. Input
        models that share a child will end up in the same list. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper of the children.
        :return: A dict[ChildType, list[ModelType]]. If an input model doesn't have children of the given child type,
            then it will not be in the resulting dictionary.
        """
        to_children: dict[RecordModel, list[WrappedType]] = RecordHandler.map_to_children(models, child_type)
        by_children: dict[WrappedType, list[RecordModel]] = {}
        for record, children in to_children.items():
            for child in children:
                by_children.setdefault(child, []).append(record)
        return by_children

    @staticmethod
    def map_to_forward_side_link(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType]) -> dict[WrappedRecordModel, WrappedType]:
        """
        Map a list of record models to their forward side link. The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side link.
        :return: A dict[ModelType, SlideLink]. If an input model doesn't have a forward side link of the given type,
            then it will map to None.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[WrappedRecordModel, WrappedType] = {}
        for model in models:
            return_dict[model] = model.get_forward_side_link(field_name, side_link_type)
        return return_dict

    @staticmethod
    def map_by_forward_side_links(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType]) -> dict[WrappedType, list[WrappedRecordModel]]:
        """
        Take a list of record models and map them by their forward side link. Essentially an inversion of
        map_to_forward_side_link. Input models that share a forward side link will end up in the same list.
        The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side links.
        :return: A dict[SideLink, list[ModelType]]. If an input model doesn't have a forward side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[WrappedRecordModel, WrappedType] = RecordHandler\
            .map_to_forward_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType, list[WrappedRecordModel]] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            by_side_link.setdefault(side_link, []).append(record)
        return by_side_link

    @staticmethod
    def map_by_forward_side_link(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType]) -> dict[WrappedType, WrappedRecordModel]:
        """
        Take a list of record models and map them by their forward side link. Essentially an inversion of
        map_to_forward_side_link, but if two records share the same forward link, an exception is thrown.
        The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side links.
        :return: A dict[SideLink, ModelType]. If an input model doesn't have a forward side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[WrappedRecordModel, WrappedType] = RecordHandler\
            .map_to_forward_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType, WrappedRecordModel] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            if side_link in by_side_link:
                raise SapioException(f"Side link {side_link.data_type_name} {side_link.record_id} encountered more "
                                     f"than once in models list.")
            by_side_link[side_link] = record
        return by_side_link

    @staticmethod
    def map_to_reverse_side_links(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType]) -> dict[WrappedRecordModel, list[WrappedType]]:
        """
        Map a list of record models to a list reverse side links of a given type. The reverse side links must already
        be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper of the reverse side links.
        :return: A dict[ModelType, list[SideLink]]. If an input model doesn't have reverse side links of the given type,
            then it will map to an empty list.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[WrappedRecordModel, list[WrappedType]] = {}
        for model in models:
            return_dict[model] = model.get_reverse_side_link(field_name, side_link_type)
        return return_dict

    @staticmethod
    def map_to_reverse_side_link(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType]) -> dict[WrappedRecordModel, WrappedType]:
        """
        Map a list of record models to the reverse side link of a given type. If a given record has more than one
        reverse side link of this type, an exception is thrown. The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper of the reverse side links.
        :return: A dict[ModelType, SideLink]. If an input model doesn't have reverse side links of the given type,
            then it will map to None.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[WrappedRecordModel, WrappedType] = {}
        for model in models:
            links: list[WrappedType] = model.get_reverse_side_link(field_name, side_link_type)
            if len(links) > 1:
                raise SapioException(f"Model {model.data_type_name} {model.record_id} has more than one reverse link "
                                     f"of type {side_link_type.get_wrapper_data_type_name()}.")
            return_dict[model] = links[0] if links else None
        return return_dict

    @staticmethod
    def map_by_reverse_side_links(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType]) -> dict[WrappedType, list[WrappedRecordModel]]:
        """
        Take a list of record models and map them by their reverse side links. Essentially an inversion of
        map_to_reverse_side_links. Input models that share a reverse side link will end up in the same list.
        The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper of the reverse side links.
        :return: A dict[SideLink, list[ModelType]]. If an input model doesn't have reverse side links of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_links: dict[WrappedRecordModel, list[WrappedType]] = RecordHandler\
            .map_to_reverse_side_links(models, field_name, side_link_type)
        by_side_links: dict[WrappedType, list[WrappedRecordModel]] = {}
        for record, side_links in to_side_links.items():
            for side_link in side_links:
                by_side_links.setdefault(side_link, []).append(record)
        return by_side_links

    @staticmethod
    def map_by_reverse_side_link(models: Iterable[WrappedRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType]) -> dict[WrappedType, WrappedRecordModel]:
        """
        Take a list of record models and map them by their reverse side link. Essentially an inversion of
        map_to_reverse_side_link. If two records share the same reverse side link, an exception is thrown.
        The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper of the reverse side links.
        :return: A dict[SideLink, ModelType]. If an input model doesn't have a reverse side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[WrappedRecordModel, WrappedType] = RecordHandler\
            .map_to_reverse_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType, WrappedRecordModel] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            if side_link in by_side_link:
                raise SapioException(f"Side link {side_link.data_type_name} {side_link.record_id} encountered more "
                                     f"than once in models list.")
            by_side_link[side_link] = record
        return by_side_link

    @staticmethod
    def map_by_id(models: Iterable[SapioRecord]) -> dict[int, SapioRecord]:
        """
        Map the given records their record IDs.

        :param models: The records to map.
        :return: A dict mapping the record ID to each record.
        """
        ret_dict: dict[int, SapioRecord] = {}
        for model in models:
            ret_dict.update({model.record_id: model})
        return ret_dict

    @staticmethod
    def map_by_field(models: Iterable[SapioRecord], field_name: FieldIdentifier) \
            -> dict[FieldValue, list[SapioRecord]]:
        """
        Map the given records by one of their fields. If any two records share the same field value, they'll appear in
        the same value list.

        :param models: The records to map.
        :param field_name: The field name to map against.
        :return: A dict mapping field values to the records with that value.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        ret_dict: dict[FieldValue, list[SapioRecord]] = {}
        for model in models:
            val: FieldValue = model.get_field_value(field_name)
            ret_dict.setdefault(val, []).append(model)
        return ret_dict

    @staticmethod
    def map_by_unique_field(models: Iterable[SapioRecord], field_name: FieldIdentifier) \
            -> dict[FieldValue, SapioRecord]:
        """
        Uniquely map the given records by one of their fields. If any two records share the same field value, throws
        an exception.

        :param models: The records to map.
        :param field_name: The field name to map against.
        :return: A dict mapping field values to the record with that value.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        ret_dict: dict[FieldValue, SapioRecord] = {}
        for model in models:
            val: FieldValue = model.get_field_value(field_name)
            if val in ret_dict:
                raise SapioException(f"Value {val} encountered more than once in models list.")
            ret_dict.update({val: model})
        return ret_dict

    @staticmethod
    def sum_of_field(models: Iterable[SapioRecord], field_name: FieldIdentifier) -> float:
        """
        Sum up the numeric value of a given field across all input models. Excepts that all given models have a value.
        If the field is an integer field, the value will be converted to a float.

        :param models: The models to calculate the sum of.
        :param field_name: The name of the numeric field to sum.
        :return: The sum of the field values for the collection of models.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        field_sum: float = 0
        for model in models:
            field_sum += float(model.get_field_value(field_name))
        return field_sum

    @staticmethod
    def mean_of_field(models: Iterable[SapioRecord], field_name: FieldIdentifier) -> float:
        """
        Calculate the mean of the numeric value of a given field across all input models. Excepts that all given models
        have a value. If the field is an integer field, the value will be converted to a float.

        :param models: The models to calculate the mean of.
        :param field_name: The name of the numeric field to mean.
        :return: The mean of the field values for the collection of models.
        """
        return RecordHandler.sum_of_field(models, field_name) / len(list(models))

    @staticmethod
    def get_newest_record(records: Iterable[SapioRecord]) -> SapioRecord:
        """
        Get the newest record from a list of records.

        :param records: The list of records.
        :return: The input record with the highest record ID. None if the input list is empty.
        """
        newest: SapioRecord | None = None
        for record in records:
            if newest is None or record.record_id > newest.record_id:
                newest = record
        return newest

    # FR-46696: Add a function for getting the oldest record in a list, just like we have one for the newest record.
    @staticmethod
    def get_oldest_record(records: Iterable[SapioRecord]) -> SapioRecord:
        """
        Get the oldest record from a list of records.

        :param records: The list of records.
        :return: The input record with the lowest record ID. None if the input list is empty.
        """
        oldest: SapioRecord | None = None
        for record in records:
            if oldest is None or record.record_id < oldest.record_id:
                oldest = record
        return oldest

    @staticmethod
    def values_to_field_maps(field_name: FieldIdentifier, values: Iterable[FieldValue],
                             existing_fields: list[FieldIdentifier] | None = None) -> list[FieldMap]:
        """
        Add a list of values for a specific field to a list of dictionaries pairing each value to that field name.

        :param field_name: The name of the field that the values are from.
        :param values: A list of field values.
        :param existing_fields: An optional existing fields map list to add the new values to. Values are added in the
          list in the same order that they appear. If no existing fields are provided, returns a new fields map list.
        :return: A fields map list that contains the given values mapped by the given field name.
        """
        # Update the existing fields map list if one is given.
        field_name: str = AliasUtil.to_data_field_name(field_name)
        existing_fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(existing_fields)
        if existing_fields:
            values = list(values)
            # The number of new values must match the length of the existing fields list.
            if len(values) != len(existing_fields):
                raise SapioException(f"Length of \"{field_name}\" values does not match the existing fields length.")
            for field, value in zip(existing_fields, values):
                field.update({field_name: value})
            return existing_fields
        # Otherwise, create a new fields map list.
        return [{field_name: value} for value in values]

    # FR-46155: Update relationship path traversing functions to be non-static and take in a wrapper type so that the
    # output can be wrapped instead of requiring the user to wrap the output.
    def get_linear_path(self, models: Iterable[RecordModel], path: RelationshipPath, wrapper_type: type[WrappedType]) \
            -> dict[RecordModel, WrappedType | None]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy must be linear (1:1 relationship between data types at every step) and the
        relationship path must already be loaded.

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use.
        :return: Each record model mapped to the record at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to None.
        """
        ret_dict: dict[RecordModel, WrappedType | None] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current: PyRecordModel | None = model if isinstance(model, PyRecordModel) else model.backing_model
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if current is None:
                    break
                if direction == RelationshipNodeType.CHILD:
                    current = current.get_child_of_type(data_type)
                elif direction == RelationshipNodeType.PARENT:
                    current = current.get_parent_of_type(data_type)
                elif direction == RelationshipNodeType.ANCESTOR:
                    ancestors: list[PyRecordModel] = list(self.an_man.get_ancestors_of_type(current, data_type))
                    if not ancestors:
                        current = None
                    elif len(ancestors) > 1:
                        raise SapioException(f"Hierarchy contains multiple ancestors of type {data_type}.")
                    else:
                        current = ancestors[0]
                elif direction == RelationshipNodeType.DESCENDANT:
                    descendants: list[PyRecordModel] = list(self.an_man.get_descendant_of_type(current, data_type))
                    if not descendants:
                        current = None
                    elif len(descendants) > 1:
                        raise SapioException(f"Hierarchy contains multiple descendants of type {data_type}.")
                    else:
                        current = descendants[0]
                elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                    current = current.get_forward_side_link(node.data_field_name)
                elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                    field_name: str = node.data_field_name
                    reverse_links: list[PyRecordModel] = current.get_reverse_side_link(data_type, field_name)
                    if not reverse_links:
                        current = None
                    elif len(reverse_links) > 1:
                        raise SapioException(f"Hierarchy contains multiple reverse links of type {data_type} on field "
                                             f"{field_name}.")
                    else:
                        current = reverse_links[0]
                else:
                    raise SapioException("Unsupported path direction.")
            ret_dict.update({model: self.inst_man.wrap(current, wrapper_type) if current else None})
        return ret_dict

    def get_branching_path(self, models: Iterable[RecordModel], path: RelationshipPath,
                           wrapper_type: type[WrappedType]) -> dict[RecordModel, list[WrappedType]]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy may be non-linear (1:Many relationships between data types are allowed) and the
        relationship path must already be loaded.

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use.
        :return: Each record model mapped to the records at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to an empty list.
        """
        ret_dict: dict[RecordModel, list[WrappedType]] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current_search: set[PyRecordModel] = {model if isinstance(model, PyRecordModel) else model.backing_model}
            next_search: set[PyRecordModel] = set()
            # Exhaust the records at each step in the path, then use those records for the next step.
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if len(current_search) == 0:
                    break
                for search in current_search:
                    if direction == RelationshipNodeType.CHILD:
                        next_search.update(search.get_children_of_type(data_type))
                    elif direction == RelationshipNodeType.PARENT:
                        next_search.update(search.get_parents_of_type(data_type))
                    elif direction == RelationshipNodeType.ANCESTOR:
                        next_search.update(self.an_man.get_ancestors_of_type(search, data_type))
                    elif direction == RelationshipNodeType.DESCENDANT:
                        next_search.update(self.an_man.get_descendant_of_type(search, data_type))
                    elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                        next_search.add(search.get_forward_side_link(node.data_field_name))
                    elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                        next_search.update(search.get_reverse_side_link(data_type, node.data_field_name))
                    else:
                        raise SapioException("Unsupported path direction.")
                current_search = next_search
                next_search = set()
            ret_dict.update({model: self.inst_man.wrap_list(list(current_search), wrapper_type)})
        return ret_dict

    # FR-46155: Create a relationship traversing function that returns a single function at the end of the path like
    # get_linear_path but can handle branching paths in the middle of the search like get_branching_path.
    def get_flat_path(self, models: Iterable[RecordModel], path: RelationshipPath, wrapper_type: type[WrappedType]) \
            -> dict[RecordModel, WrappedType | None]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy may be non-linear (1:Many relationships between data types are allowed) and the
        relationship path must already be loaded.

        The path is "flattened" by only following the first record at each step. Useful for traversing 1-to-Many-to-1
        relationships (e.g. a sample which is aliquoted to a number of samples, then those aliquots are pooled back
        together into a single sample).

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use.
        :return: Each record model mapped to the record at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to None.
        """
        ret_dict: dict[RecordModel, WrappedType | None] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current: list[PyRecordModel] = [model if isinstance(model, PyRecordModel) else model.backing_model]
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if len(current) == 0:
                    break
                if direction == RelationshipNodeType.CHILD:
                    current = current[0].get_children_of_type(data_type)
                elif direction == RelationshipNodeType.PARENT:
                    current = current[0].get_parents_of_type(data_type)
                elif direction == RelationshipNodeType.ANCESTOR:
                    current = list(self.an_man.get_ancestors_of_type(current[0], data_type))
                elif direction == RelationshipNodeType.DESCENDANT:
                    current = list(self.an_man.get_descendant_of_type(current[0], data_type))
                elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                    current = [current[0].get_forward_side_link(node.data_field_name)]
                elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                    current = current[0].get_reverse_side_link(data_type, node.data_field_name)
                else:
                    raise SapioException("Unsupported path direction.")
            ret_dict.update({model: self.inst_man.wrap(current[0], wrapper_type) if current else None})
        return ret_dict

    def __find_model(self, wrapper_type: type[WrappedType], primary_identifier: str, id_value: FieldValue,
                     secondary_identifiers: FieldIdentifierMap | None = None) -> WrappedType | None:
        """
        Find a record from the system that matches the given field values. The primary identifier and value is used
        to query for the record, then the secondary identifiers may be optionally provided to further filter the
        returned results. If no record is found with these filters, returns None.
        """
        # Query for all records that match the primary identifier.
        results: list[WrappedType] = self.query_models(wrapper_type, primary_identifier, [id_value])

        # Find the one record, if any, that matches the secondary identifiers.
        unique_record: WrappedType | None = None
        for result in results:
            matches_all: bool = True
            for field, value in secondary_identifiers.items():
                if result.get_field_value(field) != value:
                    matches_all = False
                    break
            if matches_all:
                # If a previous record in the results already matched all identifiers, then throw an exception.
                if unique_record is not None:
                    raise SapioException(f"More than one record of type {wrapper_type.get_wrapper_data_type_name()} "
                                         f"encountered in system that matches all provided identifiers.")
                unique_record = result
        return unique_record

    @staticmethod
    def __verify_data_type(records: Iterable[DataRecord], wrapper_type: type[WrappedType]) -> None:
        """
        Throw an exception if the data type of the given records and wrapper don't match.
        """
        model_type: str = wrapper_type.get_wrapper_data_type_name()
        for record in records:
            record_type: str = record.data_type_name
            # Account for ELN data type records.
            if ElnBaseDataType.is_eln_type(record_type):
                record_type = ElnBaseDataType.get_base_type(record_type).data_type_name
            if record_type != model_type:
                raise SapioException(f"Data record of type {record_type} cannot be wrapped by the record model wrapper "
                                     f"of type {model_type}")
