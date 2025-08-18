from sapiopylib.rest.utils.Protocols import ElnEntryStep
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.eln.experiment_handler import ExperimentHandler
from sapiopycommons.general.aliases import SapioRecord, RecordIdentifier, AliasUtil
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler

PLATE_IDS_TAG: str = "MultiLayerPlating_Plate_RecordIdList"


class PlateDesignerEntry:
    """
    A wrapper for 3D plate designer entries in experiments, providing functions for common actions when dealing with
    such entries.
    """
    step: ElnEntryStep
    __exp_handler: ExperimentHandler
    __rec_handler: RecordHandler
    __plates: list[SapioRecord] | None
    __aliquots: list[SapioRecord] | None
    __sources: list[SapioRecord] | None
    __designer_elements: list[SapioRecord] | None
    __plate_ids: list[int] | None

    def __init__(self, step: ElnEntryStep, exp_handler: ExperimentHandler):
        """
        :param step: The ElnEntryStep that is the 3D plate designer entry.
        :param exp_handler: An ExperimentHandler for the experiment that this entry comes from.
        """
        self.step = step
        self.__exp_handler = exp_handler
        self.__rec_handler = RecordHandler(exp_handler.context)
        self.__plates = None
        self.__aliquots = None
        self.__sources = None
        self.__designer_elements = None
        self.__plate_ids = None

    def get_plates(self, wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Get the plates that are in the designer entry.

        Makes a webservice query to get the plates from the entry and caches the result for future calls. This cache
        will be invalidated if a set_plates or add_plates call is made, requiring a new webservice call the next time
        this function is called.

        :param wrapper_type: The record model wrapper to use.
        :return: A list of the plates in the designer entry.
        """
        if self.__plates is not None:
            return self.__plates
        self.__plates = self.__rec_handler.query_models_by_id(wrapper_type, self.__get_plate_ids())
        return self.__plates

    def set_plates(self, plates: list[RecordIdentifier]) -> None:
        """
        Set the plates that are in the plate designer entry. This removes any existing plates that are in the entry
        but not in the given list.

        Makes a webservice call to update the plate designer entry's entry options.

        :param plates: The plates to set the plate designer entry with.
        """
        record_ids: list[int] = AliasUtil.to_record_ids(plates)
        self.__set_plate_ids(record_ids)

    def add_plates(self, plates: list[RecordIdentifier]) -> None:
        """
        Add the given plates to the plate designer entry. This preserves any existing plates that are in the entry.

        Makes a webservice call to update the plate designer entry's entry options.

        :param plates: The plates to add to the plate designer entry.
        """
        record_ids: list[int] = AliasUtil.to_record_ids(plates)
        self.__set_plate_ids(self.__get_plate_ids() + record_ids)

    def get_sources(self, wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Get the source records that were used to populate the plate designer entry's sample table. This looks for the
        entries that the plate designer entry is dependent upon and gets their records if they match the data type name
        of the given wrapper.

        Makes a webservice call to retrieve the dependent entries if the experiment handler had not already cached it.
        Makes another webservice call to get the records from the dependent entry and caches them for future calls.

        :param wrapper_type: The record model wrapper to use.
        :return: A list of the source records that populate the plate designer entry's sample table.
        """
        if self.__sources is not None:
            return self.__sources

        records: list[WrappedType] = []
        dependent_ids: list[int] = self.step.eln_entry.dependency_set
        for step in self.__exp_handler.get_all_steps(wrapper_type):
            if step.get_id() in dependent_ids:
                records.extend(self.__exp_handler.get_step_models(step, wrapper_type))

        self.__sources = records
        return self.__sources

    def get_aliquots(self, wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Get the aliquots that were created from this plate designer entry upon its submission.

        Makes a webservice call to retrieve the aliquots from the plate designer entry and caches them for future calls.

        :param wrapper_type: The record model wrapper to use.
        :return: A list of the aliquots created by the plate designer entry.
        """
        if not self.__exp_handler.step_is_submitted(self.step):
            raise SapioException("The plate designer entry must be submitted before its aliquots can be retrieved.")
        if self.__aliquots is not None:
            return self.__aliquots
        self.__aliquots = self.__exp_handler.get_step_models(self.step, wrapper_type)
        return self.__aliquots

    def get_plate_designer_well_elements(self, wrapper_type: type[WrappedType]) -> list[WrappedType]:
        """
        Get the plate designer well elements for the plates in the plate designer entry. These are the records in the
        system that determine how wells are displayed on each plate in the entry.

        Makes a webservice call to get the plate designer well elements of the entry and caches them for future calls.
        This cache will be invalidated if a set_plates or add_plates call is made, requiring a new webservice call the
        next time this function is called.

        :param wrapper_type: The record model wrapper to use.
        :return: A list of the plate designer well elements in the designer entry.
        """
        if self.__designer_elements is not None:
            return self.__designer_elements
        self.__designer_elements = self.__rec_handler.query_models(wrapper_type, "PlateRecordId",
                                                                   self.__get_plate_ids())
        return self.__designer_elements

    def __get_plate_ids(self) -> list[int]:
        if self.__plate_ids is not None:
            return self.__plate_ids
        id_tag: str = self.__exp_handler.get_step_option(self.step, PLATE_IDS_TAG)
        if not id_tag:
            raise SapioException("No plates in the plate designer entry")
        self.__plate_ids = [int(x) for x in id_tag.split(",")]
        return self.__plate_ids

    def __set_plate_ids(self, record_ids: list[int]) -> None:
        record_ids.sort()
        self.__exp_handler.add_step_options(self.step, {PLATE_IDS_TAG: ",".join([str(x) for x in record_ids])})
        self.__plate_ids = record_ids
        # The plates and designer elements caches have been invalidated.
        self.__plates = None
        self.__designer_elements = None
