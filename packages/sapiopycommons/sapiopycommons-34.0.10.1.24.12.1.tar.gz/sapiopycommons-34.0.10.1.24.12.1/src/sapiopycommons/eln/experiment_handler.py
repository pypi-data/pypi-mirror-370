from __future__ import annotations

import time
from collections.abc import Mapping, Iterable
from weakref import WeakValueDictionary

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment, TemplateExperimentQueryPojo, ElnTemplate, \
    InitializeNotebookExperimentPojo, ElnExperimentUpdateCriteria
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import AbstractElnEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ExperimentEntryStatus, ElnExperimentStatus, ElnEntryType, \
    ElnBaseDataType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookDirective import ElnExperimentDirective
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.Protocols import ElnEntryStep, ElnExperimentProtocol
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager, RecordModelManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType
from sapiopylib.rest.utils.recordmodel.properties import Child

from sapiopycommons.eln.experiment_report_util import ExperimentReportUtil
from sapiopycommons.general.aliases import AliasUtil, SapioRecord, ExperimentIdentifier, UserIdentifier, \
    DataTypeIdentifier, RecordModel
from sapiopycommons.general.exceptions import SapioException

Step = str | ElnEntryStep
"""An object representing an identifier to an ElnEntryStep. May be either the name of the step or the ElnEntryStep
itself."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class ExperimentHandler:
    user: SapioUser
    context: SapioWebhookContext | None
    """The context that this handler is working from."""

    # Basic experiment info from the context.
    __eln_exp: ElnExperiment
    """The ELN experiment from the context."""
    __protocol: ElnExperimentProtocol
    """The ELN experiment as a protocol."""
    __exp_id: int
    """The ID of this experiment's notebook. Used for making update webservice calls."""

    # Managers.
    __eln_man: ElnManager
    """The ELN manager. Used for updating the experiment and its steps."""
    __inst_man: RecordModelInstanceManager
    """The record model instance manager. Used for wrapping the data records of a step as record models."""

    # Only a fraction of the information about the current experiment exists in the context. Much information requires
    # additional queries to obtain, but may also be repeatedly accessed. In such cases, cache the information after it
    # has been requested so that the user doesn't need to worry about caching it themselves.
    # CR-46341: Replace class variables with instance variables.
    __exp_record: DataRecord | None
    """The data record for this experiment. Only cached when first accessed."""
    __exp_template: ElnTemplate | None
    """The template for this experiment. Only cached when first accessed."""
    __exp_options: dict[str, str]
    """Experiment options for this experiment. Only cached when first accessed."""

    __queried_all_steps: bool
    """Whether this ExperimentHandler has queried the system for all steps in the experiment."""
    __steps: dict[str, ElnEntryStep]
    """Steps from this experiment. All steps are cached the first time any individual step is accessed."""
    __step_options: dict[int, dict[str, str]]
    """Entry options for each step in this experiment. All entry options are cached the first time any individual step's
    options are queried. The cache is updated whenever the entry options for a step are changed by this handler."""

    # Constants
    __ENTRY_COMPLETE_STATUSES = [ExperimentEntryStatus.Completed, ExperimentEntryStatus.CompletedApproved]
    """The set of statuses that an ELN entry could have and be considered completed/submitted."""
    __ENTRY_LOCKED_STATUSES = [ExperimentEntryStatus.Completed, ExperimentEntryStatus.CompletedApproved,
                               ExperimentEntryStatus.Disabled, ExperimentEntryStatus.LockedAwaitingApproval,
                               ExperimentEntryStatus.LockedRejected]
    """The set of statuses that an ELN entry could have and be considered locked."""
    __EXPERIMENT_COMPLETE_STATUSES = [ElnExperimentStatus.Completed, ElnExperimentStatus.CompletedApproved]
    """The set of statuses that an ELN experiment could have and be considered completed."""
    __EXPERIMENT_LOCKED_STATUSES = [ElnExperimentStatus.Completed, ElnExperimentStatus.CompletedApproved,
                                    ElnExperimentStatus.LockedRejected, ElnExperimentStatus.LockedAwaitingApproval,
                                    ElnExperimentStatus.Canceled]
    """The set of statuses that an ELN experiment could have and be considered locked."""

    __instances: WeakValueDictionary[str, ExperimentHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None):
        """
        :param context: The current webhook context or a user object to send requests from.
        :param experiment: If an experiment is provided that is separate from the experiment that is in the context,
            that experiment will be used by this ExperimentHandler instead. An experiment can be provided in various
            forms, including an ElnExperiment, ElnExperimentProtocol, an experiment record, or a notebook experiment ID.
        """
        param_results = cls.__parse_params(context, experiment)
        user = param_results[0]
        experiment = param_results[2]
        key = f"{user.__hash__()}:{experiment.notebook_experiment_id}"
        obj = cls.__instances.get(key)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[key] = obj
        return obj

    def __init__(self, context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None):
        """
        Initialization will throw an exception if there is no ELN Experiment in the provided context and no experiment
        is provided.

        :param context: The current webhook context or a user object to send requests from.
        :param experiment: If an experiment is provided that is separate from the experiment that is in the context,
            that experiment will be used by this ExperimentHandler instead. An experiment can be provided in various
            forms, including an ElnExperiment, ElnExperimentProtocol, an experiment record, or a notebook experiment ID.
        """
        param_results = self.__parse_params(context, experiment)
        self.user = param_results[0]
        self.context = param_results[1]
        experiment = param_results[2]

        # Get the basic information about this experiment that already exists in the context and is often used.
        self.__eln_exp = experiment
        self.__protocol = ElnExperimentProtocol(experiment, self.user)
        self.__exp_id = self.__protocol.get_id()

        # Grab various managers that may be used.
        self.__eln_man = DataMgmtServer.get_eln_manager(self.user)
        self.__inst_man = RecordModelManager(self.user).instance_manager

        # Create empty caches to fill when necessary.
        self.__steps = {}
        self.__step_options = {}
        # CR-46330: Cache any experiment entry information that might already exist in the context.
        self.__queried_all_steps = False
        # We can only trust the entries in the context if the experiment that this handler is for is the same as the
        # one from the context.
        if self.context is not None and self.context.eln_experiment == experiment:
            if self.context.experiment_entry is not None:
                self.__steps.update({self.context.active_step.get_name(): self.context.active_step})
            if self.context.experiment_entry_list is not None:
                for entry in self.context.experiment_entry_list:
                    self.__steps.update({entry.entry_name: ElnEntryStep(self.__protocol, entry)})

    @staticmethod
    def __parse_params(context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None) \
            -> tuple[SapioUser, SapioWebhookContext | None, ElnExperiment]:
        if isinstance(context, SapioWebhookContext):
            user = context.user
            context = context
        else:
            user = context
            context = None
        if context is not None and context.eln_experiment is not None and experiment is None:
            experiment = context.eln_experiment
        # FR-46495 - Allow the init function of ExperimentHandler to take in an ElnExperiment that is separate from the
        # context.
        # CR-37038 - Allow other experiment object types to be provided. Convert them all down to ElnExperiment.
        if (context is None or context.eln_experiment is None) and experiment is not None:
            eln_manager = DataMgmtServer.get_eln_manager(user)
            # If this object is already an ElnExperiment, do nothing.
            if isinstance(experiment, ElnExperiment):
                pass
            # If this object is an ElnExperimentProtocol, then we can get the ElnExperiment from the object.
            elif isinstance(experiment, ElnExperimentProtocol):
                experiment: ElnExperiment = experiment.eln_experiment
            # If this object is an integer, assume it is a notebook ID that we can query the system with.
            elif isinstance(experiment, int):
                notebook_id: int = experiment
                experiment: ElnExperiment = eln_manager.get_eln_experiment_by_id(notebook_id)
                if not experiment:
                    raise SapioException(f"No experiment with notebook ID {notebook_id} located in the system.")
            # If this object is a record, assume it is an experiment record that we can query the system with.
            else:
                record_id: int = AliasUtil.to_record_ids([experiment])[0]
                experiment: ElnExperiment = eln_manager.get_eln_experiment_by_record_id(record_id)
                if not experiment:
                    raise SapioException(f"No experiment with record ID {record_id} located in the system.")
        if experiment is None:
            raise SapioException("Cannot initialize ExperimentHandler. No ELN Experiment found in the provided parameters.")

        return user, context, experiment

    # FR-46495: Split the creation of the experiment in launch_experiment into a create_experiment function.
    @staticmethod
    def create_experiment(context: SapioWebhookContext,
                          template_name: str,
                          experiment_name: str | None = None,
                          parent_record: SapioRecord | None = None, *,
                          template_version: int | None = None, active_templates_only: bool = True) -> ElnExperiment:
        """
        Create an ElnExperiment from the given template name.

        Makes a webservice request to query for all the templates matching the provided criteria. Note that if multiple
        templates match the same criteria, the first template that is encountered in the query is used. Throws an
        exception if no template is found. Also makes a webservice request to create the experiment.

        :param context: The current webhook context.
        :param template_name: The name of the template to create the experiment from.
        :param experiment_name: The name to give to the experiment after it is created. If not provided, defaults to the
            display name of the template.
        :param parent_record: The parent record to attach this experiment under. This record must be an eligible
            parent type to ELNExperiment. If not provided, the experiment is stored in the aether.
        :param template_version: The version number of the template to use. If not provided, the latest version of the
            template is used. NOTICE: Template version numbers aren't necessarily the same between environments, so
            be careful with using the same webhook across multiple environments if you are searching for a specific
            version number.
        :param active_templates_only: Whether only active templates should be queried for.
        :return: The newly created experiment.
        """
        template_query = TemplateExperimentQueryPojo(latest_version_only=(template_version is None),
                                                     active_templates_only=active_templates_only)
        templates: list[ElnTemplate] = context.eln_manager.get_template_experiment_list(template_query)
        launch_template: ElnTemplate | None = None
        for template in templates:
            if template.template_name != template_name:
                continue
            if template_version is not None and template.template_version != template_version:
                continue
            launch_template = template
            break
        if launch_template is None:
            raise SapioException(f"No template with the name \"{template_name}\"" +
                                 ("" if template_version is None else f" and the version {template_version}") +
                                 f" found.")

        if experiment_name is None:
            experiment_name: str = launch_template.display_name
        if parent_record is not None:
            parent_record: DataRecord = AliasUtil.to_data_record(parent_record)
        notebook_init = InitializeNotebookExperimentPojo(experiment_name, launch_template.template_id, parent_record)
        return context.eln_manager.create_notebook_experiment(notebook_init)

    @staticmethod
    def launch_experiment(context: SapioWebhookContext,
                          template_name: str,
                          experiment_name: str | None = None,
                          parent_record: SapioRecord | None = None, *,
                          template_version: int | None = None, active_templates_only: bool = True) -> SapioWebhookResult:
        """
        Create a SapioWebhookResult that, when returned by a webhook handler, sends the user to a new experiment of the
        input template name.

        Makes a webservice request to query for all the templates matching the provided criteria. Note that if multiple
        templates match the same criteria, the first template that is encountered in the query is used. Throws an
        exception if no template is found. Also makes a webservice request to create the experiment.

        :param context: The current webhook context.
        :param template_name: The name of the template to create the experiment from.
        :param experiment_name: The name to give to the experiment after it is created. If not provided, defaults to the
            display name of the template.
        :param parent_record: The parent record to attach this experiment under. This record must be an eligible
            parent type to ELNExperiment. If not provided, the experiment is stored in the aether.
        :param template_version: The version number of the template to use. If not provided, the latest version of the
            template is used. NOTICE: Template version numbers aren't necessarily the same between environments, so
            be careful with using the same webhook across multiple environments if you are searching for a specific
            version number.
        :param active_templates_only: Whether only active templates should be queried for.
        :return: A SapioWebhookResult that directs the user to the newly created experiment.
        """
        experiment = ExperimentHandler.create_experiment(context, template_name, experiment_name, parent_record,
                                                         template_version=template_version,
                                                         active_templates_only=active_templates_only)
        return SapioWebhookResult(True, directive=ElnExperimentDirective(experiment.notebook_experiment_id))

    def get_experiment_template(self, exception_on_none: bool = True) -> ElnTemplate | None:
        """
        Query for the experiment template for the current experiment. The returned template is cached by the
        ExperimentHandler.

        :param exception_on_none: If false, returns None if there is no experiment template. If true, raises an exception
            when the experiment template doesn't exist.
        :return: This experiment's template. None if it has no template.
        """
        template_id: int | None = self.__eln_exp.template_id
        if template_id is None:
            self.__exp_template = None
            if exception_on_none:
                raise SapioException(f"Experiment with ID {self.__exp_id} has no template ID.")
            return None

        if not hasattr(self, "_ExperimentHandler__exp_template"):
            # PR-46504: Allow inactive and non-latest version templates to be queried.
            query = TemplateExperimentQueryPojo(template_id_white_list=[template_id],
                                                active_templates_only=False,
                                                latest_version_only=False)
            templates: list[ElnTemplate] = self.__eln_man.get_template_experiment_list(query)
            # PR-46504: Set the exp_template to None if there are no results.
            self.__exp_template = templates[0] if templates else None
        if self.__exp_template is None and exception_on_none:
            raise SapioException(f"Experiment template not found for experiment with ID {self.__exp_id}.")
        return self.__exp_template

    # CR-46104: Change get_template_name to behave like NotebookProtocolImpl.getTemplateName (i.e. first see if the
    # experiment template exists, and if not, see if the experiment record exists, instead of only checking the
    # template).
    def get_template_name(self, exception_on_none: bool = True) -> str | None:
        """
        Get the template name for the current experiment.

        The template name is determined by either the experiment template or the experiment record, whichever is
        already cached. If neither are cached, queries for the experiment template. If no experiment template exists,
        queries for the experiment record.

        :param exception_on_none: If false, returns None if there is no template name. If true, raises an exception
            when the template name doesn't exist.
        :return: The template name of the current experiment. None if it has no template name.
        """
        if not hasattr(self, "_ExperimentHandler__exp_template"):
            self.get_experiment_template(False)
        if self.__exp_template is None and not hasattr(self, "_ExperimentHandler__exp_record"):
            self.get_experiment_record(False)

        name: str | None = None
        if self.__exp_template is not None:
            name = self.__exp_template.template_name
        elif self.__exp_record is not None:
            name = self.__exp_record.get_field_value("TemplateExperimentName")
        if name is None and exception_on_none:
            raise SapioException(f"Template name not found for experiment with ID {self.__exp_id}.")
        return name

    def get_experiment_record(self, exception_on_none: bool = True) -> DataRecord | None:
        """
        Query for the data record of this experiment. The returned record is cached by the ExperimentHandler.

        :param exception_on_none: If false, returns None if there is no experiment record. If true, raises an exception
            when the experiment record doesn't exist.
        :return: The data record for this experiment. None if it has no record.
        """
        if not hasattr(self, "_ExperimentHandler__exp_record"):
            self.__exp_record = self.__protocol.get_record()
        if self.__exp_record is None and exception_on_none:
            raise SapioException(f"Experiment record not found for experiment with ID {self.__exp_id}.")
        return self.__exp_record

    def get_experiment_model(self, wrapper_type: type[WrappedType]) -> WrappedType:
        """
        Query for the data record of this experiment and wrap it as a record model with the given wrapper.
        The returned record is cached by the ExperimentHandler.

        :param wrapper_type: The record model wrapper to use.
        :return: The record model for this experiment.
        """
        return self.__inst_man.add_existing_record_of_type(self.get_experiment_record(), wrapper_type)

    def update_experiment(self,
                          experiment_name: str | None = None,
                          experiment_status: ElnExperimentStatus | None = None,
                          experiment_option_map: dict[str, str] | None = None) -> None:
        """
        Make a webservice call to update the experiment for this ExperimentHandler.  If any parameter is not provided,
        then no change is made to it.

        :param experiment_name: The new name of the experiment.
        :param experiment_status: The new status of this experiment.
        :param experiment_option_map:
            The new map of options for this experiment. Completely overwrites the existing options map.
            Any changes to the experiment options will update this ExperimentHandler's cache of the experiment options.
            If you wish to add options to the existing map of options that an experiment has, use the
            add_experiment_options method.
        """
        criteria = ElnExperimentUpdateCriteria()
        criteria.new_experiment_name = experiment_name
        criteria.new_experiment_status = experiment_status
        criteria.experiment_option_map = experiment_option_map
        self.__eln_man.update_notebook_experiment(self.__exp_id, criteria)

        if experiment_name is not None:
            self.__eln_exp.notebook_experiment_name = experiment_name
        if experiment_status is not None:
            self.__eln_exp.notebook_experiment_status = experiment_status
        if experiment_option_map is not None:
            self.__exp_options = experiment_option_map

    def get_experiment_option(self, option: str) -> str:
        """
        Get the value of a specific experiment option.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param option: The experiment option to search for.
        :return: The value of the input experiment options.
        """
        return self.get_experiment_options().get(option)

    def get_experiment_options(self) -> dict[str, str]:
        """
        Get the entire map of options for this experiment.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :return: The map of options for this experiment.
        """
        return self.__get_experiment_options()

    def add_experiment_options(self, mapping: Mapping[str, str]) -> None:
        """
        Add to the existing map of options for this experiment. Makes a webservice call to update the experiment. Also
        updates the cache of the experiment options.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param mapping: The new options and values to add to the existing experiment options, provided as some Mapping
            (e.g. a Dict). If an option key already exists and is provided in the mapping, overwrites the existing value
            for that key.
        """
        options: dict[str, str] = self.get_experiment_options()
        options.update(mapping)
        self.update_experiment(experiment_option_map=options)

    def experiment_is_complete(self) -> bool:
        """
        Determine if the experiment has been completed.

        :return: True if the experiment's status is Completed or CompletedApproved. False otherwise.
        """
        return self.__eln_exp.notebook_experiment_status in self.__EXPERIMENT_COMPLETE_STATUSES

    def experiment_is_canceled(self) -> bool:
        """
        Determine if the experiment has been canceled.

        :return: True if the experiment's status is Canceled. False otherwise.
        """
        return self.__eln_exp.notebook_experiment_status == ElnExperimentStatus.Canceled

    def experiment_is_locked(self) -> bool:
        """
        Determine if the experiment has been locked in any way.

        :return: True if the experiment's status is Completed, CompletedApproved, Canceled, LockedAwaitingApproval,
            or LockedRejected. False otherwise.
        """
        return self.__eln_exp.notebook_experiment_status in self.__EXPERIMENT_LOCKED_STATUSES

    def complete_experiment(self) -> None:
        """
        Set the experiment's status to Completed. Makes a webservice call to update the experiment. Checks if the
        experiment is already completed, and does nothing if so.
        """
        if not self.experiment_is_complete():
            self.__protocol.complete_protocol()
            self.__eln_exp.notebook_experiment_status = ElnExperimentStatus.Completed

    def cancel_experiment(self) -> None:
        """
        Set the experiment's status to Canceled. Makes a webservice call to update the experiment. Checks if the
        experiment is already canceled, and does nothing if so.

        NOTE: This will not run the usual logic around canceling an experiment that you'd see if canceling the
        experiment using the "Cancel Experiment" toolbar button, such as moving in process samples back to the queue,
        as those changes are tied to the button instead of being on the experiment status change.
        """
        if not self.experiment_is_canceled():
            self.__protocol.cancel_protocol()
            self.__eln_exp.notebook_experiment_status = ElnExperimentStatus.Canceled

    def step_exists(self, step_name: str) -> bool:
        """
        Determine if a step by the given name exists in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_name: The name of the step to search for.
        :return: True if the step exists, false otherwise.
        """
        return self.get_step(step_name, False) is not None

    def steps_exist(self, step_names: Iterable[str]) -> bool:
        """
        Determine if all the steps by the given names exist in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_names: The names of the steps to search for.
        :return: True if every step exists, false if at least one does not exist.
        """
        return all([x is not None for x in self.get_steps(step_names, False)])

    def get_step(self, step_name: str, exception_on_none: bool = True) -> ElnEntryStep | None:
        """
        Get the step of the given name from the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_name: The name for the step to return.
        :param exception_on_none: If false, returns None if the entry can't be found. If true, raises an exception
            when the named entry doesn't exist in the experiment.
        :return: An ElnEntrySteps matching the provided name. If there is no match and no exception is to be thrown,
            returns None.
        """
        return self.get_steps([step_name], exception_on_none)[0]

    def get_steps(self, step_names: Iterable[str], exception_on_none: bool = True) -> list[ElnEntryStep | None]:
        """
        Get a list of steps of the given names from the experiment, sorted in the same order as the names are provided.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_names: A list of names for the entries to return and the order to return them in.
        :param exception_on_none: If false, returns None for entries that can't be found. If true, raises an exception
            when the named entry doesn't exist in the experiment.
        :return: A list of ElnEntrySteps matching the provided names in the order they were provided in. If there is no
            match for a given step and no exception is to be thrown, returns None for that step.
        """
        ret_list: list[ElnEntryStep | None] = []
        for name in step_names:
            # If we haven't queried the system for all steps in the experiment yet, then the reason that a step is
            # missing may be because it wasn't in the webhook context. Therefore, query all steps and then check
            # if the step name is still missing from the experiment before potentially throwing an exception.
            if self.__queried_all_steps is False and name not in self.__steps:
                self.__queried_all_steps = True
                self.__steps.update({step.get_name(): step for step in self.__protocol.get_sorted_step_list()})

            step: ElnEntryStep = self.__steps.get(name)
            if step is None and exception_on_none is True:
                raise SapioException(f"ElnEntryStep of name \"{name}\" not found in experiment with ID {self.__exp_id}.")
            ret_list.append(step)
        return ret_list

    def get_all_steps(self, data_type: DataTypeIdentifier | None = None) -> list[ElnEntryStep]:
        """
        Get a list of every entry in the experiment. Optionally filter the returned entries by a data type.

        Makes a webservice call to retrieve every entry in the experiment if they were not already previously cached.

        :param data_type: A data type used to filter the returned entries. If None is given, returns all entries. If
            a data type name or wrapper is given, only returns entries that match that data type name or wrapper.
        :return: Every entry in the experiment in order of appearance that match the provided data type, if any.
        """
        if self.__queried_all_steps is False:
            self.__queried_all_steps = True
            self.__steps.update({step.get_name(): step for step in self.__protocol.get_sorted_step_list()})
        all_steps: list[ElnEntryStep] = self.__protocol.get_sorted_step_list()
        if data_type is None:
            return all_steps
        data_type: str = AliasUtil.to_data_type_name(data_type)
        return [x for x in all_steps if data_type in x.get_data_type_names()]

    def get_step_by_option(self, key: str, value: str | None = None) -> ElnEntryStep:
        """
        Retrieve the step in this experiment that contains an entry option with the provided key and value.
        Throws an exception if no entries or multiple entries in the experiment match.

        :param key: The key of the entry option to match on.
        :param value: The value of the entry option to match on. If not provided, then only matches on key.
        :return: The entry in this experiment that matches the provided entry option key and value.
        """
        steps: list[ElnEntryStep] = self.get_steps_by_option(key, value)
        count: int = len(steps)
        if count != 1:
            option = key + ("::" + value if value is not None else "")
            raise SapioException(f"{('No' if count == 0 else 'Multiple')} entries in this experiment match the "
                                 f"provided option: {option}")
        return steps[0]

    def get_steps_by_option(self, key: str, value: str | None = None) -> list[ElnEntryStep]:
        """
        Retrieve every step in this experiment that contains an entry option with the provided key and value.

        :param key: The key of the entry option to match on.
        :param value: The value of the entry option to match on. If not provided, then only matches on key.
        :return: The entries in this experiment that match the provided entry option key and value.
        """
        ret_list: list[ElnEntryStep] = []
        for step in self.get_all_steps():
            options: dict[str, str] = self.get_step_options(step)
            if key in options:
                if value is None or options[key] == value:
                    ret_list.append(step)
        return ret_list

    def get_step_records(self, step: Step) -> list[DataRecord]:
        """
        Query for the data records for the given step. The returned records are not cached by the ExperimentHandler.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to get the data records for.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The data records for the given step.
        """
        return self.__to_eln_step(step).get_records()

    def get_step_models(self, step: Step, wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Query for the data records for the given step and wrap them as record models with the given type. The returned
        records are not cached by the ExperimentHandler.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to get the data records for.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param wrapper_type: The record model wrapper to use.
        :return: The record models for the given step.
        """
        return self.__inst_man.add_existing_records_of_type(self.get_step_records(step), wrapper_type)

    def add_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Make a webservice call to add a list of records to a step. Only functions for global data type table entries.
        For adding to an ELN data type table entry, see add_eln_rows.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to add the records to.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to add to the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step = self.__to_eln_step(step)
        if not records:
            return
        dt: str = AliasUtil.to_singular_data_type_name(records)
        if ElnBaseDataType.is_base_data_type(dt):
            raise SapioException(f"{dt} is an ELN data type. This function call has no effect on ELN data types. "
                                 f"Use add_eln_rows or add_sample_details instead.")
        if dt != step.get_data_type_names()[0]:
            raise SapioException(f"Cannot add {dt} records to entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        step.add_records(AliasUtil.to_data_records(records))

    def remove_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Make a webservice call to remove a list of records from a step. Only functions for global data type table
        entries. For removing from an ELN data type table entry, see remove_eln_rows.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to remove from the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step = self.__to_eln_step(step)
        if not records:
            return
        dt: str = AliasUtil.to_singular_data_type_name(records)
        if ElnBaseDataType.is_base_data_type(dt):
            raise SapioException(f"{dt} is an ELN data type. This function call has no effect on ELN data types. "
                                 f"Use remove_eln_rows or remove_sample_details instead.")
        if dt != step.get_data_type_names()[0]:
            raise SapioException(f"Cannot remove {dt} records from entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        step.remove_records(AliasUtil.to_data_records(records))

    def set_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Sets the records in the given step to be equal to the input list of records. If a record is already on the step,
        it remains. If a record is missing from the step, it gets added. If a record is on the step but not in the
        provided record list, it gets removed. Makes one webservice call to get what is currently on the step and
        one additional webservice call for each of either adding or removing, if necessary.

        Functions for table, form, and attachment entries. For form and attachment entries, only a single record should
        be provided.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to set for the given step,
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step = self.__to_eln_step(step)
        if records:
            dt: str = AliasUtil.to_singular_data_type_name(records)
            if ElnBaseDataType.is_base_data_type(dt):
                raise SapioException(f"{dt} is an ELN data type. This function call has no effect on ELN data types. "
                                     f"Use add_eln_rows or add_sample_details instead.")
            if dt != step.get_data_type_names()[0]:
                raise SapioException(f"Cannot set {dt} records for entry {step.get_name()} of type "
                                     f"{step.get_data_type_names()[0]}.")
        step.set_records(AliasUtil.to_data_records(records))

    # FR-46496 - Provide alias of set_step_records for use with form entries.
    def set_form_record(self, step: Step, record: SapioRecord) -> None:
        """
        Sets the record for a form entry.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param record:
            A record to set for the given step,
            The record may be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel.
        """
        self.set_step_records(step, [record])

    # FR-46496 - Provide functions for adding and removing rows from an ELN data type entry.
    def add_eln_rows(self, step: Step, count: int, wrapper_type: type[WrappedType] | None = None) \
            -> list[PyRecordModel | WrappedType]:
        """
        Add rows to an ELNExperimentDetail or ELNSampleDetail table entry. The rows will not appear in the system
        until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param count: The number of new rows to add to the entry.
        :param wrapper_type: Optionally wrap the ELN data type in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: A list of the newly created rows.
        """
        step = self.__to_eln_step(step)
        if step.eln_entry.entry_type != ElnEntryType.Table:
            raise SapioException("The provided step is not a table entry.")
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt):
            raise SapioException("The provided step is not an ELN data type entry.")
        records: list[PyRecordModel] = self.__inst_man.add_new_records(dt, count)
        if wrapper_type:
            return self.__inst_man.wrap_list(records, wrapper_type)
        return records

    def add_eln_row(self, step: Step, wrapper_type: type[WrappedType] | None = None) -> PyRecordModel | WrappedType:
        """
        Add a row to an ELNExperimentDetail or ELNSampleDetail table entry. The row will not appear in the system
        until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param wrapper_type: Optionally wrap the ELN data type in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: The newly created row.
        """
        return self.add_eln_rows(step, 1, wrapper_type)[0]

    def remove_eln_rows(self, step: Step, records: list[SapioRecord]) -> None:
        """
        Remove rows from an ELNExperimentDetail or ELNSampleDetail table entry. ELN data type table entries display all
        records in the system that match the entry's data type. This means that removing rows from an ELN data type
        table entry is equivalent to deleting the records for the rows.

        The rows will not be deleted in the system until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to remove from the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step = self.__to_eln_step(step)
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt):
            raise SapioException("The provided step is not an ELN data type entry.")
        if not records:
            return
        record_dt: str = AliasUtil.to_singular_data_type_name(records, False)
        if record_dt != dt:
            raise SapioException(f"Cannot remove {dt} records from entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        # If any rows were provided as data records, turn them into record models before deleting them, as otherwise
        # this function would need to make a webservice call to do the deletion.
        data_records: list[DataRecord] = []
        for record in records:
            if isinstance(record, DataRecord):
                data_records.append(record)
            else:
                record.delete()
        if data_records:
            record_models: list[PyRecordModel] = self.__inst_man.add_existing_records(data_records)
            for record in record_models:
                record.delete()

    def remove_eln_row(self, step: Step, record: SapioRecord) -> None:
        """
        Remove a row from an ELNExperimentDetail or ELNSampleDetail table entry. ELN data type table entries display all
        records in the system that match the entry's data type. This means that removing rows from an ELN data type
        table entry is equivalent to deleting the records for the rows.

        The row will not be deleted in the system until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param record:
            The record to remove from the given step.
            The record may be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel.
        """
        self.remove_eln_rows(step, [record])

    def add_sample_details(self, step: Step, samples: list[RecordModel], wrapper_type: type[WrappedType]) \
            -> list[PyRecordModel | WrappedType]:
        """
        Add sample details to a sample details entry while relating them to the input sample records.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param samples: The sample records to add the sample details to.
        :param wrapper_type: Optionally wrap the sample details in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: The newly created sample details. The indices of the samples in the input list match the index of the
            sample details in this list that they are related to.
        """
        step = self.__to_eln_step(step)
        if step.eln_entry.entry_type != ElnEntryType.Table:
            raise SapioException("The provided step is not a table entry.")
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt) or ElnBaseDataType.get_base_type(dt) != ElnBaseDataType.SAMPLE_DETAIL:
            raise SapioException("The provided step is not an ELNSampleDetail entry.")
        records: list[PyRecordModel] = []
        for sample in samples:
            if sample.data_type_name != "Sample":
                raise SapioException(f"Received a {sample.data_type_name} record when Sample records were expected.")
            detail: PyRecordModel = sample.add(Child.create_by_name(dt))
            detail.set_field_values({
                "SampleId": sample.get_field_value("SampleId"),
                "OtherSampleId": sample.get_field_value("OtherSampleId")
            })
            records.append(detail)
        if wrapper_type:
            return self.__inst_man.wrap_list(records, wrapper_type)
        return records

    def update_step(self, step: Step,
                    entry_name: str | None = None,
                    related_entry_set: Iterable[int] | None = None,
                    dependency_set: Iterable[int] | None = None,
                    entry_status: ExperimentEntryStatus | None = None,
                    order: int | None = None,
                    description: str | None = None,
                    requires_grabber_plugin: bool | None = None,
                    is_initialization_required: bool | None = None,
                    notebook_experiment_tab_id: int | None = None,
                    entry_height: int | None = None,
                    column_order: int | None = None,
                    column_span: int | None = None,
                    is_removable: bool | None = None,
                    is_renamable: bool | None = None,
                    source_entry_id: int | None = None,
                    clear_source_entry_id: bool | None = None,
                    is_hidden: bool | None = None,
                    is_static_View: bool | None = None,
                    is_shown_in_template: bool | None = None,
                    template_item_fulfilled_timestamp: int | None = None,
                    clear_template_item_fulfilled_timestamp: bool | None = None,
                    entry_options_map: dict[str, str] | None = None) -> None:
        """
        Make a webservice call to update an abstract step. If any parameter is not provided, then no change is made
        to it. All changes will be reflected by the ExperimentEntry of the Step that is being updated.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The entry step to update.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param entry_name: The new name of this entry.
        :param related_entry_set: The new set of entry IDs for the entries that are related (implicitly dependent) to
            this entry. Completely overwrites the existing related entries.
        :param dependency_set: The new set of entry IDs for the entries that are dependent (explicitly dependent) on
            this entry. Completely overwrites the existing dependent entries.
        :param entry_status: The new status of this entry.
        :param order: The row order of this entry in its tab.
        :param description: The new description of this entry.
        :param requires_grabber_plugin: Whether this entry's initialization is handled by a grabber plugin. If true,
            then is_initialization_required is forced to true by the server.
        :param is_initialization_required: Whether the user is required to manually initialize this entry.
        :param notebook_experiment_tab_id: The ID of the tab that this entry should appear on.
        :param entry_height: The height of this entry.
        :param column_order: The column order of this entry.
        :param column_span: How many columns this entry spans.
        :param is_removable: Whether this entry can be removed by the user.
        :param is_renamable: Whether this entry can be renamed by the user.
        :param source_entry_id: The ID of this entry from its template.
        :param clear_source_entry_id: True if the source entry ID should be cleared.
        :param is_hidden: Whether this entry is hidden from the user.
        :param is_static_View: Whether this entry is static. Static entries are uneditable and shared across all
            experiments of the same template.
        :param is_shown_in_template: Whether this entry is saved to and shown in the experiment's template.
        :param template_item_fulfilled_timestamp: A timestamp in milliseconds for when this entry was initialized.
        :param clear_template_item_fulfilled_timestamp: True if the template item fulfilled timestamp should be cleared,
            uninitializing the entry.
        :param entry_options_map:
            The new map of options for this entry. Completely overwrites the existing options map.
            Any changes to the entry options will update this ExperimentHandler's cache of entry options.
            If you wish to add options to the existing map of options that an entry has, use the
            add_step_options method.
        """
        step: ElnEntryStep = self.__to_eln_step(step)
        criteria = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)

        # These two variables could be iterables that aren't lists. Convert them to plain
        # lists, since that's what the update criteria is expecting.
        if related_entry_set is not None:
            related_entry_set = list(related_entry_set)
        if dependency_set is not None:
            dependency_set = list(dependency_set)

        criteria.entry_name = entry_name
        criteria.related_entry_set = related_entry_set
        criteria.dependency_set = dependency_set
        criteria.entry_status = entry_status
        criteria.order = order
        criteria.description = description
        criteria.requires_grabber_plugin = requires_grabber_plugin
        criteria.is_initialization_required = is_initialization_required
        criteria.notebook_experiment_tab_id = notebook_experiment_tab_id
        criteria.entry_height = entry_height
        criteria.column_order = column_order
        criteria.column_span = column_span
        criteria.is_removable = is_removable
        criteria.is_renamable = is_renamable
        criteria.source_entry_id = source_entry_id
        criteria.clear_source_entry_id = clear_source_entry_id
        criteria.is_hidden = is_hidden
        criteria.is_static_View = is_static_View
        criteria.is_shown_in_template = is_shown_in_template
        criteria.template_item_fulfilled_timestamp = template_item_fulfilled_timestamp
        criteria.clear_template_item_fulfilled_timestamp = clear_template_item_fulfilled_timestamp
        criteria.entry_options_map = entry_options_map

        self.__eln_man.update_experiment_entry(self.__exp_id, step.get_id(), criteria)

        # Update the cached information for this entry in case it's needed by the caller after updating.
        entry: ExperimentEntry = step.eln_entry
        if entry_name is not None:
            # PR-46477 - Ensure that the previous name of the updated entry already existed in the cache.
            if entry.entry_name in self.__steps:
                self.__steps.pop(entry.entry_name)
            entry.entry_name = entry_name
            self.__steps.update({entry_name: step})
        if related_entry_set is not None:
            entry.related_entry_id_set = related_entry_set
        if dependency_set is not None:
            entry.dependency_set = dependency_set
        if entry_status is not None:
            entry.entry_status = entry_status
        if order is not None:
            entry.order = order
        if description is not None:
            entry.description = description
        if requires_grabber_plugin is not None:
            entry.requires_grabber_plugin = requires_grabber_plugin
        if is_initialization_required is not None:
            entry.is_initialization_required = is_initialization_required
        if notebook_experiment_tab_id is not None:
            entry.notebook_experiment_tab_id = notebook_experiment_tab_id
        if entry_height is not None:
            entry.entry_height = entry_height
        if column_order is not None:
            entry.column_order = column_order
        if column_span is not None:
            entry.column_span = column_span
        if is_removable is not None:
            entry.is_removable = is_removable
        if is_renamable is not None:
            entry.is_renamable = is_renamable
        if source_entry_id is not None:
            entry.source_entry_id = source_entry_id
        if clear_source_entry_id is True:
            entry.source_entry_id = None
        if is_hidden is not None:
            entry.is_hidden = is_hidden
        if is_static_View is not None:
            entry.is_static_View = is_static_View
        if is_shown_in_template is not None:
            entry.is_shown_in_template = is_shown_in_template
        if template_item_fulfilled_timestamp is not None:
            entry.template_item_fulfilled_timestamp = template_item_fulfilled_timestamp
        if clear_template_item_fulfilled_timestamp is True:
            entry.template_item_fulfilled_timestamp = None
        if entry_options_map is not None:
            self.__step_options.update({step.get_id(): entry_options_map})

    def get_step_option(self, step: Step, option: str) -> str:
        """
        Get the value of a specific entry option for the given step.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for a specific step. The step options are cached so that subsequent calls of this
        method for that step don't make a webservice call.

        :param step:
            The step to check the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param option: The entry option to search for.
        :return: The value of the input entry option for the input step.
        """
        return self.get_step_options(step).get(option)

    def get_step_options(self, step: Step) -> dict[str, str]:
        """
        Get the entire map of options for the input step.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for any step in this experiment. The step options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param step:
            The step to get the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The map of options for the input step.
        """
        step = self.__to_eln_step(step)
        if step not in self.__step_options:
            self.__step_options.update(ExperimentReportUtil.get_experiment_entry_options(self.user, self.get_all_steps()))
        return self.__step_options[step.get_id()]

    def add_step_options(self, step: Step, mapping: Mapping[str, str]):
        """
        Add to the existing map of options for the input step. Makes a webservice call to update the step. Also
        updates the cache of the step's options.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for a specific step. The step options are cached so that subsequent calls of this
        method for that step don't make a webservice call.

        :param step:
            The step to update the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param mapping: The new options and values to add to the existing step options, provided as some Mapping
            (e.g. a Dict). If an option key already exists and is provided in the mapping, overwrites the existing value
            for that key.
        """
        options: dict[str, str] = self.get_step_options(step)
        options.update(mapping)
        self.update_step(step, entry_options_map=options)

    def initialize_step(self, step: Step) -> None:
        """
        Initialize the input step by setting its template item fulfilled timestamp to now. Makes a webservice call to
        update the step. Checks if the step already has a timestamp, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to initialize.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        # Avoid unnecessary calls if the step is already initialized.
        step: ElnEntryStep = self.__to_eln_step(step)
        if step.eln_entry.template_item_fulfilled_timestamp is None:
            self.update_step(step, template_item_fulfilled_timestamp=round(time.time() * 1000))

    def uninitialize_step(self, step: Step) -> None:
        """
        Uninitialize the input step by clearing its template item fulfilled timestamp to now. Makes a webservice call to
        update the step. Checks if the step already doesn't have a timestamp, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to uninitialize.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        # Avoid unnecessary calls if the step is already uninitialized.
        step: ElnEntryStep = self.__to_eln_step(step)
        if step.eln_entry.template_item_fulfilled_timestamp is not None:
            self.update_step(step, clear_template_item_fulfilled_timestamp=True)

    def complete_step(self, step: Step) -> None:
        """
        Submit the input step. Makes a webservice call to update the step. Checks if the step is already completed, and
        does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to complete.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step = self.__to_eln_step(step)
        if step.eln_entry.entry_status not in self.__ENTRY_COMPLETE_STATUSES:
            step.complete_step()
            step.eln_entry.entry_status = ExperimentEntryStatus.Completed

    def unlock_step(self, step: Step) -> None:
        """
        Set the status of the input step to UnlockedChangesRequired. Makes a webservice call to update the step. Checks
        if the step is already unlocked, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to unlock.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step = self.__to_eln_step(step)
        if step.eln_entry.entry_status in self.__ENTRY_LOCKED_STATUSES:
            step.unlock_step()
            step.eln_entry.entry_status = ExperimentEntryStatus.UnlockedChangesRequired

    def disable_step(self, step: Step) -> None:
        """
        Set the status of the input step to Disabled. This is the state that entries are in when they are waiting for
        entries that they are dependent upon to be submitted before they can be enabled. If you have unsubmitted an
        entry and want its dependent entries to be locked again, then you would use this to set their status to
        disabled.

        Makes a webservice call to update the step. Checks if the step is already unlocked, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to disable.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step = self.__to_eln_step(step)
        if step.eln_entry.entry_status in self.__ENTRY_LOCKED_STATUSES:
            self.update_step(step, entry_status=ExperimentEntryStatus.Disabled)

    def step_is_submitted(self, step: Step) -> bool:
        """
        Determine if the input step has already been submitted.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to check.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: True if the step's status is Completed or CompletedApproved. False otherwise.
        """
        return self.__to_eln_step(step).eln_entry.entry_status in self.__ENTRY_COMPLETE_STATUSES

    def step_is_locked(self, step: Step) -> bool:
        """
        Determine if the input step has been locked in any way.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to check.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: True if the step's status is Completed, CompletedApproved, Disabled, LockedAwaitingApproval,
            or LockedRejected. False otherwise.
        """
        return self.__to_eln_step(step).eln_entry.entry_status in self.__ENTRY_LOCKED_STATUSES

    def __to_eln_step(self, step: Step) -> ElnEntryStep:
        """
        Convert a variable that could be either a string or an ElnEntryStep to just an ElnEntryStep.
        This will query and cache the steps for the experiment if the input step is a name and the steps have not been
        cached before.

        :return: The input step as an ElnEntryStep.
        """
        return self.get_step(step) if isinstance(step, str) else step

    def __get_experiment_options(self) -> dict[str, str]:
        """
        Cache the experiment options if they haven't been cached yet.

        :return: The options for this experiment.
        """
        if hasattr(self, "_ExperimentHandler__exp_options"):
            return self.__exp_options
        self.__exp_options = self.__eln_man.get_notebook_experiment_options(self.__exp_id)
        return self.__exp_options
