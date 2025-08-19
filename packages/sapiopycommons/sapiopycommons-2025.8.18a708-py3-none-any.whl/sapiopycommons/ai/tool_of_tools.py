import base64
import io
import math
from typing import Final, Mapping, Any

import requests
from pandas import DataFrame
from requests import Response
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.Sort import SortDirection
from sapiopylib.rest.pojo.chartdata.DashboardDefinition import GaugeChartDefinition, DashboardDefinition
from sapiopylib.rest.pojo.chartdata.DashboardEnums import ChartGroupingType, ChartOperationType, DashboardScope
from sapiopylib.rest.pojo.chartdata.DashboardSeries import GaugeChartSeries
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout, TableLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldType, \
    VeloxStringFieldDefinition
from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, ElnFormEntryUpdateCriteria, \
    ElnDashboardEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ElnBaseDataType, ExperimentEntryStatus
from sapiopylib.rest.pojo.eln.eln_headings import ElnExperimentTabAddCriteria, ElnExperimentTab
from sapiopylib.rest.pojo.eln.field_set import ElnFieldSetInfo
from sapiopylib.rest.utils.ProtocolUtils import ELNStepFactory
from sapiopylib.rest.utils.Protocols import ElnEntryStep, ElnExperimentProtocol

from sapiopycommons.callbacks.field_builder import FieldBuilder
from sapiopycommons.general.aliases import AliasUtil, SapioRecord
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.general.html_formatter import HtmlFormatter
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.multimodal.multimodal import MultiModalManager
from sapiopycommons.multimodal.multimodal_data import ImageDataRequestPojo

CREDENTIALS_HEADER: Final[str] = "SAPIO_APP_API_KEY"
API_URL_HEADER: Final[str] = "SAPIO_APP_API_URL"
EXP_ID_HEADER: Final[str] = "EXPERIMENT_ID"
TAB_PREFIX_HEADER: Final[str] = "TAB_PREFIX"


# FR-47422: Create utility classes and methods to assist the tool of tools.
def create_tot_headers(url: str, username: str, password: str, experiment_id: int, tab_prefix: str) \
        -> dict[str, str]:
    """
    Create the headers to be passed to a tool of tools endpoint.

    :param url: The webservice URL of the system to make the changes in.
    :param username: The username of the user making the changes.
    :param password: The password of the user making the changes.
    :param experiment_id: The ID of the experiment to make the changes in.
    :param tab_prefix: The prefix to use for the tab name that will be created by the tool.
    :return: The headers to be passed to the endpoint.
    """
    # Combine the credentials into the format "username:password"
    credentials: str = f"{username}:{password}"
    # Encode the credentials to bytes, then encode them using base64,
    # and finally convert the result back into a string.
    encoded_credentials: str = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    # Remove the trailing slash from the URL if it exists.
    if url.endswith("/"):
        url.rstrip("/")
    headers: dict[str, str] = {
        CREDENTIALS_HEADER: f"Basic {encoded_credentials}",
        API_URL_HEADER: url,
        EXP_ID_HEADER: str(experiment_id),
        TAB_PREFIX_HEADER: tab_prefix
    }
    return headers


def create_user_from_tot_headers(headers: Mapping[str, str]) -> SapioUser:
    """
    Create a SapioUser object from the headers passed to a tool of tools endpoint.

    :param headers: The headers that were passed to the endpoint.
    :return: A SapioUser object created from the headers that can be used to communicate with the Sapio server.
    """
    headers: dict[str, str] = format_tot_headers(headers)
    credentials = (base64.b64decode(headers[CREDENTIALS_HEADER.lower()].removeprefix("Basic "))
                   .decode("utf-8").split(":", 1))
    url: str = headers[API_URL_HEADER.lower()]
    if url.endswith("/"):
        url.rstrip("/")
    return SapioUser(url, username=credentials[0], password=credentials[1])


def format_tot_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """
    Format the headers passed to a tool of tools endpoint to guarantee that the keys are lowercase.

    :param headers: The headers that were passed to the endpoint.
    :return: The headers with all keys converted to lowercase. (Conflicting keys will cause one to overwrite the other,
        but there should not be any conflicting keys in the headers passed to a tool of tools endpoint.)
    """
    return {k.lower(): v for k, v in headers.items()}


class AiHelper:
    """
    A class with helper methods for the AI to make use of when creating/updating experiment tabs and entries.
    """
    # Contextual info.
    user: SapioUser
    exp_id: int
    timeout: int

    # Managers.
    dr_man: DataRecordManager
    eln_man: ElnManager
    dt_man: DataTypeManager

    def __init__(self, user: SapioUser, exp_id: int, timeout: int = 120):
        """
        :param user: The user to send the requests from.
        :param exp_id: The ID of the experiment to create the entries in.
        :param timeout: The timeout in seconds to use for requests.
        """
        self.user = user
        self.exp_id = exp_id
        self.timeout = timeout

        self.dr_man = DataRecordManager(self.user)
        self.eln_man = ElnManager(self.user)
        self.dt_man = DataTypeManager(self.user)

    def call_post_endpoint(self, url: str, payload: Any, tab_prefix: str = "") -> Response:
        """
        Call a tool endpoint. Constructs the tool headers and checks the response for errors for the caller.

        :param url: The URL of the endpoint to call.
        :param payload: The payload to send to the endpoint.
        :param tab_prefix: The prefix to use for the tab name that will be created by the tool.
        :return: The Response object returned by the endpoint.
        """
        headers = create_tot_headers(self.user.url, self.user.username, self.user.password, self.exp_id, tab_prefix)
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response

    def call_get_endpoint(self, url: str, params: Any, tab_prefix: str = "") -> Response:
        """
        Call a tool endpoint. Constructs the tool headers and checks the response for errors for the caller.

        :param url: The URL of the endpoint to call.
        :param params: The query parameters to send to the endpoint.
        :param tab_prefix: The prefix to use for the tab name that will be created by the tool.
        :return: The Response object returned by the endpoint.
        """
        headers = create_tot_headers(self.user.url, self.user.username, self.user.password, self.exp_id, tab_prefix)
        response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response

    @property
    def protocol(self) -> ElnExperimentProtocol:
        """
        :return: An experiment protocol object for this helper's experiment. (Recreating a new protocol object every
            time this is called since the protocol's cache could be invalidated by things that the AI is doing.)
        """
        # The experiment name and record ID aren't necessary to know for our purposes.
        return ElnExperimentProtocol(ElnExperiment(self.exp_id, "", 0), self.user)

    def create_tab(self, name: str) -> ElnExperimentTab:
        """
        Create a new tab in the experiment.

        :param name: The name of the tab to create.
        :return: The newly created tab.
        """
        tab_crit = ElnExperimentTabAddCriteria(name, [])
        return self.eln_man.add_tab_for_experiment(self.exp_id, tab_crit)

    def tab_next_entry_order(self, tab: ElnExperimentTab) -> int:
        """
        :param tab: A tab in this helper's experiment.
        :return: The order that the next entry that gets created in the tab should have.
        """
        max_order: int = 0
        for step in self.protocol.get_sorted_step_list():
            if step.eln_entry.notebook_experiment_tab_id == tab.tab_id and step.eln_entry.order > max_order:
                max_order = step.eln_entry.order
        return max_order + 1

    def create_experiment_details_from_data_frame(self,
                                                  tab: ElnExperimentTab,
                                                  entry_name: str,
                                                  df: DataFrame,
                                                  sort_field: str | None = None,
                                                  sort_direction: SortDirection = SortDirection.DESCENDING,
                                                  smiles_column: str | None = None) -> ExperimentEntry | None:
        """
        Create an experiment detail entry from a DataFrame.

        :param tab: The tab that the entry should be added to.
        :param entry_name: The name of the entry.
        :param df: The DataFrame to create the entry from.
        :param sort_field: The field to sort the resulting entry rows by, if any.
        :param sort_direction: The direction to sort the resulting entry rows in, if a sort_field is provided.
        :param smiles_column: The column name in the provided DataFrame that corresponds to the SMILES strings of the
            compounds tracked in the DataFrame, if any. If this is provided, then the entry will be created with
            images of the compounds corresponding to the SMILES strings in each row of the table.
        :return: The newly created experiment detail entry.
        """
        json_list: list[dict[str, Any]] = []
        smiles: list[str] = []
        for _, row in df.iterrows():
            row_dict: dict[str, Any] = row.to_dict()
            if smiles_column is not None:
                smiles.append(row_dict.get(smiles_column))
            json_list.append(row_dict)
        images: list[bytes] | None = None
        if smiles:
            images = self.smiles_to_svg(smiles)
        return self.create_experiment_details_from_json(tab, entry_name, json_list, sort_field, sort_direction, images)

    def create_experiment_details_from_json(self,
                                            tab: ElnExperimentTab,
                                            entry_name: str,
                                            json_list: list[dict[str, Any]],
                                            sort_field: str | None = None,
                                            sort_direction: SortDirection = SortDirection.DESCENDING,
                                            images: list[bytes] | None = None) -> ExperimentEntry | None:
        """
        Create an experiment detail entry from a list of JSON dictionaries.

        :param tab: The tab that the entry should be added to.
        :param entry_name: The name of the entry.
        :param json_list: The list of JSON dictionaries to create the entry from. Each dictionary is expected to have the
            same keys.
        :param sort_field: The field to sort the resulting entry rows by, if any.
        :param sort_direction: The direction to sort the resulting entry rows in, if a sort_field is provided.
        :param images: The images to include in the entry, if any. The images will be added to the rows that they
            correspond to based on the order of the images in the images list and the order of the rows in the
            json list.
        :return: The newly created experiment detail entry.
        """
        if not json_list:
            return None

        def update_string_field(f: AbstractVeloxFieldDefinition, v: Any) -> None:
            """
            Update the max length of the string field and whether it is a link-out field depending on the length and
            form of the given value.

            :param f: The definition of the string field.
            :param v: A field value that will be present for this field.
            """
            if not isinstance(f, VeloxStringFieldDefinition) or v is None:
                return
            sv = str(v)
            f.max_length = max(f.max_length, len(sv))
            if not f.link_out and sv.startswith("http://") or sv.startswith("https://"):
                link_out, link_out_url = FieldBuilder._convert_link_out({"Link": "[[LINK_OUT]]"})
                f.link_out = link_out
                f.link_out_url = link_out_url

        # Determine which fields in the JSON can be used to create field definitions.
        fb = FieldBuilder()
        json_key_to_field_def: dict[str, AbstractVeloxFieldDefinition] = {}
        numeric_string_fields: set[str] = set()
        for values in json_list:
            for key, value in values.items():
                # Skip null values, since we can't know what type they're meant to represent.
                if value is None:
                    continue

                # The field name is the JSON key name, but with spaces and dashes replaced by underscores and with a
                # leading underscore added if the field name starts with a number.
                field_name: str = key.strip()
                if " " in field_name:
                    field_name = field_name.replace(" ", "_")
                if "-" in field_name:
                    field_name = field_name.replace("-", "_")
                if field_name[0].isnumeric():
                    field_name = "_" + field_name

                # If this is the first time this key is being encountered, create a field for it.
                if key not in json_key_to_field_def:
                    if isinstance(value, str):
                        json_key_to_field_def[key] = fb.string_field(field_name, display_name=key)
                        update_string_field(json_key_to_field_def[key], value)
                    elif isinstance(value, bool):
                        json_key_to_field_def[key] = fb.boolean_field(field_name, display_name=key)
                    elif isinstance(value, (int, float)):
                        json_key_to_field_def[key] = fb.double_field(field_name, display_name=key, precision=3)
                    # All other values in the JSON get skipped.
                    continue

                # The field definition already exists, but it may not be a valid field type for this value.
                field_type: FieldType = json_key_to_field_def[key].data_field_type
                # Strings can be anything, so we don't need to check the value type.
                if field_type == FieldType.STRING:
                    # We still need to make sure the lengths are fine.
                    update_string_field(json_key_to_field_def[key], value)
                    continue
                # Boolean values can only be booleans.
                if field_type == FieldType.BOOLEAN and isinstance(value, bool):
                    continue
                # Integers and floats both fit in DOUBLE fields, but floats can't be NaN or infinity.
                if field_type == FieldType.DOUBLE:
                    # Booleans count as ints for isinstance, so make sure that true integers continue but bools don't.
                    if isinstance(value, int) and not isinstance(value, bool):
                        continue
                    if isinstance(value, float) and not math.isnan(value) and not math.isinf(value):
                        continue
                    numeric_string_fields.add(key)
                json_key_to_field_def[key] = fb.string_field(field_name, display_name=key)
                update_string_field(json_key_to_field_def[key], value)

        # Sort the JSON list if requested.
        if sort_field and sort_direction != SortDirection.NONE:
            if images:
                old_order: list[str] = [x[sort_field] for x in json_list]
            json_list.sort(key=lambda x: x.get(sort_field), reverse=sort_direction == SortDirection.DESCENDING)
            # We'll need to resort the images as well.
            if images:
                new_order: list[str] = [x[sort_field] for x in json_list]
                new_images: list[bytes] = []
                for val in new_order:
                    # noinspection PyUnboundLocalVariable
                    new_images.append(images[old_order.index(val)])
                images = new_images

        # Extract the valid field values from the JSON.
        field_maps: list[dict[str, Any]] = []
        for json_dict in json_list:
            field_map: dict[str, Any] = {}
            for key, field in json_key_to_field_def.items():
                val: Any = json_dict.get(key)
                if key in numeric_string_fields and val is not None and isinstance(val, (int, float)):
                    val: str = f"{val:.3f}"
                field_map[field.data_field_name] = val
            field_maps.append(field_map)

        # Create the experiment detail entry.
        detail_entry = ElnEntryCriteria(ElnEntryType.Table, entry_name,
                                        ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name,
                                        self.tab_next_entry_order(tab),
                                        notebook_experiment_tab_id=tab.tab_id,
                                        field_definition_list=[y for x, y in json_key_to_field_def.items()])
        entry = self.eln_man.add_experiment_entry(self.exp_id, detail_entry)
        records: list[DataRecord] = self.dr_man.add_data_records_with_data(entry.data_type_name, field_maps)

        # If images are provided, update the data type definition of the experiment detail data type to allow
        # record images and add the images to the records.
        if images:
            dt: DataTypeDefinition = self.dt_man.get_data_type_definition(entry.data_type_name)
            dt.is_record_image_assignable = True
            self.eln_man.update_eln_data_type_definition(self.exp_id, entry.entry_id, dt)

            layout: DataTypeLayout = self.dt_man.get_default_layout(entry.data_type_name)
            layout.table_layout = TableLayout(cell_size=128, record_image_width=128)
            self.eln_man.update_eln_data_type_layout(self.exp_id, entry.entry_id, layout)

            self.update_record_images(records, images)

        return entry

    def create_text_entry(self, tab: ElnExperimentTab, timestamp: str, description: str, auto_format: bool = True) \
            -> ExperimentEntry:
        """
        Create a new text entry in the experiment.

        :param tab: The tab to create the text entry in.
        :param timestamp: The timestamp to display at the top of the text entry.
        :param description: The description to display in the text entry.
        :param auto_format: Whether to automatically format the text to be added.
        :return: The newly created text entry.
        """
        if auto_format:
            description: str = f"<p>{HtmlFormatter.timestamp(timestamp)}<br>{HtmlFormatter.body(description)}</p>"
        else:
            description: str = f"<p>{timestamp}<br>{description}</p>"
        position = ElnEntryPosition(tab.tab_id, self.tab_next_entry_order(tab))
        text_entry: ElnEntryStep = ELNStepFactory.create_text_entry(self.protocol, description, position)
        return text_entry.eln_entry

    def set_text_entry(self, text_entry: ExperimentEntry, timestamp: str, description: str,
                       auto_format: bool = True) -> None:
        """
        Set the text of a text entry.

        :param text_entry: The text entry to set the text of.
        :param timestamp: The timestamp to display at the top of the text entry.
        :param description: The description to display in the text entry.
        :param auto_format: Whether to automatically format the text to be added.
        """
        if auto_format:
            timestamp = HtmlFormatter.timestamp(timestamp)
            description = HtmlFormatter.body(description)
        description: str = f"<p>{timestamp}<br>{description}</p>"
        step = ElnEntryStep(self.protocol, text_entry)
        text_record: DataRecord = step.get_records()[0]
        text_record.set_field_value(ElnBaseDataType.get_text_entry_data_field_name(), description)
        self.dr_man.commit_data_records([text_record])

    def add_to_text_entry(self, text_entry: ExperimentEntry, description: str, auto_format: bool = True) -> None:
        """
        Add to the text of a text entry.

        :param text_entry: The text entry to add the text to.
        :param description: The text to add to the text entry.
        :param auto_format: Whether to automatically format the text to be added.
        """
        step = ElnEntryStep(self.protocol, text_entry)
        text_record: DataRecord = step.get_records()[0]
        update: str = text_record.get_field_value(ElnBaseDataType.get_text_entry_data_field_name())
        if auto_format:
            description = HtmlFormatter.body(description)
        update += f"<p style=\"padding-top: 10px;\">{description}</p>"
        text_record.set_field_value(ElnBaseDataType.get_text_entry_data_field_name(), update)
        self.dr_man.commit_data_records([text_record])

    def create_attachment_entry(self, tab: ElnExperimentTab, entry_name: str, file_name: str, file_data: str | bytes) \
            -> ExperimentEntry:
        """
        Add a new attachment entry to the experiment with the provided attachment data.

        :param tab: The tab where the attachment entry will be added.
        :param entry_name: Name of the attachment entry to create in the experiment.
        :param file_name: The name of the attachment.
        :param file_data: The data of the attachment. This can be a string or bytes.
        :return: The newly created attachment entry.
        """
        tab_id: int = tab.tab_id

        # Encode the file contents in base64.
        if isinstance(file_data, str):
            file_data: bytes = file_data.encode("utf-8")
        base64_encoded: str = base64.b64encode(file_data).decode("utf-8")

        # Crete an attachment entry with the provided data.
        attachment_entry = self.eln_man.add_experiment_entry(
            self.exp_id,
            ElnEntryCriteria(ElnEntryType.Attachment, entry_name, "Attachment", order=2,
                             notebook_experiment_tab_id=tab_id, attachment_file_name=file_name,
                             attachment_data_base64=base64_encoded)
        )

        # Return the entry object for further use.
        return attachment_entry

    def create_attachment_entry_from_file(self, tab: ElnExperimentTab, entry_name: str, file_path: str) \
            -> ExperimentEntry:
        """
        Add a new attachment entry to the experiment with the provided file path to a file in the file system.

        :param tab: The tab where the attachment entry will be added.
        :param entry_name: Name of the attachment entry to create in the experiment.
        :param file_path: The path to a file in the system to attach to the experiment.
        :return: The newly created attachment entry.
        """
        with open(file_path, 'rb') as f:
            file_contents: bytes = f.read()
            return self.create_attachment_entry(tab, entry_name, file_path, file_contents)

    def smiles_to_svg(self, smiles: list[str]) -> list[bytes]:
        """
        Given a list of SMILES strings, return a list of the corresponding images in SVG format.

        :param smiles: The SMILES strings to retrieve images for.
        :return: The images in SVG format. The indices of the returned list correspond to the indices of the input
            SMILES.
        """
        if not smiles:
            return []
        reg_man = MultiModalManager(self.user)
        image_list: list[str] = reg_man.load_image_data(ImageDataRequestPojo(smiles, False))
        return [x.encode() for x in image_list]

    def update_record_images(self, records: list[SapioRecord], images: list[bytes]) -> None:
        """
        Update the images of the given records with the given images.

        :param records: The records to update the images of.
        :param images: The images to update the records with. Records will be match with the image in the matching
            index of this list.
        """
        for record, image in zip(AliasUtil.to_data_records(records), images):
            with io.BytesIO(image) as bytes_io:
                self.dr_man.set_record_image(record, bytes_io)

    def create_bar_chart(self, entry_name: str, tab: ElnExperimentTab, source_entry: ExperimentEntry,
                         x_axis: str, y_axis: str) -> ExperimentEntry:
        """
        Create a bar chart in the experiment based on the contents of the given source entry.

        :param entry_name: The name of the bar chart.
        :param tab: The tab to create the bar chart in.
        :param source_entry: The source entry to base the bar chart on.
        :param x_axis: The field to use for the x-axis.
        :param y_axis: The field to use for the y-axis.
        :return: The newly created bar chart entry.
        """
        protocol = self.protocol
        source_step = ElnEntryStep(protocol, source_entry)
        position = ElnEntryPosition(tab.tab_id, self.tab_next_entry_order(tab))
        return ELNStepFactory.create_bar_chart_step(protocol, source_step, entry_name,
                                                    x_axis, y_axis, position=position)[0].eln_entry


class ToolOfToolsHelper:
    """
    A class with helper methods utilized by the Tool of Tools for the creation and updating of experiment tabs that
    track a tool's progress and results.
    """
    # Contextual info.
    user: SapioUser
    tab_prefix: str
    exp_id: int
    helper: AiHelper

    # Tool info.
    name: str
    description: str
    results_data_type: str | None

    # Managers.
    dr_man: DataRecordManager
    eln_man: ElnManager

    # Stuff created by this helper.
    _initialized: bool
    """Whether a tab for this tool has been initialized."""
    _new_tab: bool
    """Whether a new tab was created for this tool."""
    tab: ElnExperimentTab
    """The tab that contains the tool's entries."""
    description_entry: ElnEntryStep | None
    """The text entry that displays the description of the tool."""
    description_record: DataRecord | None
    """The record that stores the description of the tool."""
    progress_entry: ElnEntryStep | None
    """A hidden entry for tracking the progress of the tool."""
    progress_record: DataRecord | None
    """The record that stores the progress of the tool."""
    progress_gauge_entry: ElnEntryStep | None
    """A chart entry that displays the progress of the tool using the hidden progress entry."""
    results_entry: ElnEntryStep | None
    """An entry for displaying the results of the tool. If None, the tool does not produce result records."""

    def __init__(self, headers: Mapping[str, str], name: str, description: str,
                 results_data_type: str | None = None):
        """
        :param headers: The headers that were passed to the endpoint.
        :param name: The name of the tool.
        :param description: A description of the tool.
        :param results_data_type: The data type name for the results of the tool. If None, the tool does not produce
            result records.
        """
        headers: dict[str, str] = format_tot_headers(headers)
        self.user = create_user_from_tot_headers(headers)
        self.exp_id = int(headers[EXP_ID_HEADER.lower()])
        self.tab_prefix = headers[TAB_PREFIX_HEADER.lower()]
        self.helper = AiHelper(self.user, self.exp_id)

        self.name = name
        self.description = description
        self.results_data_type = results_data_type

        self.dr_man = DataRecordManager(self.user)
        self.eln_man = ElnManager(self.user)

        self._initialized = False
        self._new_tab = False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_new_tab(self) -> bool:
        return self._new_tab

    def initialize_tab(self) -> ElnExperimentTab:
        if self._initialized:
            return self.tab
        self._initialized = True

        # Determine if a previous call to this endpoint already created a tab for these results. If so, grab the entries
        # from that tab.
        tab_name: str = f"{self.tab_prefix.strip()} {self.name.strip()}"
        tabs: list[ElnExperimentTab] = self.eln_man.get_tabs_for_experiment(self.exp_id)
        for tab in tabs:
            if tab.tab_name != tab_name:
                continue

            for entry in self.helper.protocol.get_sorted_step_list():
                if entry.eln_entry.notebook_experiment_tab_id != tab.tab_id:
                    continue

                dt: str = entry.get_data_type_names()[0] if entry.get_data_type_names() else None
                if (entry.eln_entry.entry_type == ElnEntryType.Form
                        and ElnBaseDataType.get_base_type(dt) == ElnBaseDataType.EXPERIMENT_DETAIL
                        and not hasattr(self, "progress_entry")):
                    self.progress_entry = entry
                    self.progress_record = entry.get_records()[0]
                elif (entry.eln_entry.entry_type == ElnEntryType.Dashboard
                      and not hasattr(self, "progress_gauge_entry")):
                    self.progress_gauge_entry = entry
                elif (entry.eln_entry.entry_type == ElnEntryType.Text
                      and not hasattr(self, "description_entry")):
                    self.description_entry = entry
                    self.description_record = entry.get_records()[0]
                elif (entry.eln_entry.entry_type == ElnEntryType.Table
                      and dt == self.results_data_type
                      and not hasattr(self, "results_entry")):
                    self.results_entry = entry

            if not hasattr(self, "progress_entry"):
                self.progress_entry = None
                self.progress_record = None
            if not hasattr(self, "progress_gauge_entry"):
                self.progress_gauge_entry = None
            if not hasattr(self, "description_entry"):
                self.description_entry = None
                self.description_record = None
            if not hasattr(self, "results_entry"):
                self.results_entry = None

            self.tab = tab
            return tab

        # Otherwise, create the tab for the tool progress and results.
        self.tab = self.helper.create_tab(tab_name)
        self._new_tab = True

        # Create a hidden entry for tracking the progress of the tool.
        field_sets: list[ElnFieldSetInfo] = self.eln_man.get_field_set_info_list()
        progress_field_set: list[ElnFieldSetInfo] = [x for x in field_sets if
                                                     x.field_set_name == "Tool of Tools Progress"]
        if not progress_field_set:
            raise SapioException("Unable to locate the field set for the Tool of Tools progress.")
        progress_entry_crit = _ElnEntryCriteria(ElnEntryType.Form, f"{tab_name} Progress",
                                                ElnBaseDataType.EXPERIMENT_DETAIL.data_type_name, 1,
                                                notebook_experiment_tab_id=self.tab.tab_id,
                                                enb_field_set_id=progress_field_set[0].field_set_id,
                                                is_hidden=True)
        progress_entry = ElnEntryStep(self.helper.protocol,
                                      self.eln_man.add_experiment_entry(self.exp_id, progress_entry_crit))
        self.progress_entry = progress_entry
        self.progress_record = progress_entry.get_records()[0]

        # Hide the progress entry.
        # TODO: Remove once we get this working on entry creation.
        form_update_crit = ElnFormEntryUpdateCriteria()
        form_update_crit.is_hidden = True
        self.eln_man.update_experiment_entry(self.exp_id, self.progress_entry.get_id(), form_update_crit)

        # Create the text entry that displays the description of the tool. Include the timestamp of when the
        # tool started and format the description so that the text isn't too small to read.
        # TODO: Get the UTC offset in seconds from the header once that's being sent.
        now: str = TimeUtil.now_in_format("%Y-%m-%d %H:%M:%S UTC", "UTC")
        description: str = f"<p>{HtmlFormatter.timestamp(now)}<br>{HtmlFormatter.body(self.description)}</p>"
        text_entry: ElnEntryStep = _ELNStepFactory.create_text_entry(self.helper.protocol, description,
                                                                     column_order=0, column_span=2)
        self.description_entry = text_entry
        self.description_record = text_entry.get_records()[0]

        # Create a gauge entry to display the progress.
        gauge_entry: ElnEntryStep = _ELNStepFactory._create_gauge_chart(self.helper.protocol, progress_entry,
                                                                        f"{self.name} Progress", "Progress", "StatusMsg",
                                                                        column_order=2, column_span=2, entry_height=250)
        self.progress_gauge_entry = gauge_entry

        # Make sure the gauge entry isn't too big and stick it to the right of the text entry.
        # TODO: Remove once we get this working on entry creation.
        dash_update_crit = ElnDashboardEntryUpdateCriteria()
        dash_update_crit.entry_height = 250
        self.eln_man.update_experiment_entry(self.exp_id, self.progress_gauge_entry.get_id(), dash_update_crit)

        # Create a results entry if this tool produces result records.
        if self.results_data_type:
            results_entry = ELNStepFactory.create_table_step(self.helper.protocol, f"{self.name} Results",
                                                             self.results_data_type)
            self.results_entry = results_entry
        else:
            self.results_entry = None

        return self.tab

    def add_to_description(self, description: str, auto_format: bool = True) -> None:
        """
        Add to the description entry of the tool.

        :param description: The text to add to the description.
        :param auto_format: Whether to automatically format the text to be added.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")
        field: str = ElnBaseDataType.get_text_entry_data_field_name()
        update: str = self.description_record.get_field_value(field)
        if auto_format:
            description = HtmlFormatter.body(description)
        update += f"<p style=\"padding-top: 10px;\">{description}</p>"
        self.description_record.set_field_value(field, update)
        self.dr_man.commit_data_records([self.description_record])

    def update_progress(self, progress: float, status_msg: str | None = None) -> None:
        """
        Updates the progress of the tool.

        :param progress: A value between 0 and 100 representing the progress of the tool.
        :param status_msg: A status message to display to the user alongside the progress gauge.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")
        self.progress_record.set_field_value("Progress", progress)
        self.progress_record.set_field_value("StatusMsg", status_msg)
        self.dr_man.commit_data_records([self.progress_record])

    def add_results(self, results: list[SapioRecord]) -> None:
        """
        Add the results of the tool to the results entry.

        :param results: The result records to add to the results entry.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")
        self.results_entry.add_records(AliasUtil.to_data_records(results))

    def add_results_bar_chart(self, x_axis: str, y_axis: str) -> ExperimentEntry:
        """
        Create a bar chart entry for the results of the tool.

        :param x_axis: The data field to use for the x-axis of the chart.
        :param y_axis: The data field to use for the y-axis of the chart.
        :return: The newly created chart entry.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")
        if not self.results_entry:
            raise SapioException("This tool does not produce result records.")
        return ELNStepFactory.create_bar_chart_step(self.helper.protocol, self.results_entry,
                                                    f"{self.name} Results Chart", x_axis, y_axis)[0].eln_entry

    def add_attachment_entry(self, entry_name: str, file_name: str, file_data: str | bytes) -> ExperimentEntry:
        """
        Add a new attachment entry to the experiment with the provided attachment data.

        :param entry_name: Name of the attachment entry to create in the experiment.
        :param file_name: The name of the attachment.
        :param file_data: The data of the attachment. This can be a string or bytes.
        :return: The newly created attachment entry.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")

        return self.helper.create_attachment_entry(self.tab, entry_name, file_name, file_data)

    def add_attachment_entry_from_file(self, entry_name: str, file_path: str) -> ExperimentEntry:
        """
        Add a new attachment entry to the experiment with the provided file path to a file in the file system.

        :param entry_name: Name of the attachment entry to create in the experiment.
        :param file_path: The path to a file in the system to attach to the experiment.
        :return: The newly created attachment entry.
        """
        if not self._initialized:
            raise SapioException("The tab for this tool has not been initialized.")

        return self.helper.create_attachment_entry_from_file(self.tab, entry_name, file_path)


class _ELNStepFactory:
    """
    Factory that provides simple functions to create a new ELN step under an ELN protocol.
    """
    @staticmethod
    def create_text_entry(protocol: ElnExperimentProtocol, text_data: str,
                          position: ElnEntryPosition | None = None, **kwargs) -> ElnEntryStep:
        """
        Create a text entry at the end of the protocol, with a initial text specified in the text entry.
        :param protocol: The protocol to create a new step for.
        :param text_data: Must be non-blank. This is what will be displayed. Some HTML format tags can be inserted.
        :param position: The position of the new step. If not specified, the new step will be added at the end.
        :return: The new text entry step.
        """
        eln_manager, new_entry = _ELNStepFactory._get_entry_creation_criteria(ElnBaseDataType.TEXT_ENTRY_DETAIL.data_type_name,
                                                                              protocol, 'Text Entry', ElnEntryType.Text,
                                                                              position, **kwargs)
        record = eln_manager.get_data_records_for_entry(protocol.eln_experiment.notebook_experiment_id,
                                                        new_entry.entry_id).result_list[0]
        record.set_field_value(ElnBaseDataType.get_text_entry_data_field_name(), text_data)
        DataMgmtServer.get_data_record_manager(protocol.user).commit_data_records([record])
        ret = ElnEntryStep(protocol, new_entry)
        protocol.invalidate()
        return ret

    # TODO: Remove this once pylib's gauge chart definition is up to date.
    @staticmethod
    def _create_gauge_chart(protocol: ElnExperimentProtocol, data_source_step: ElnEntryStep, step_name: str,
                            field_name: str, status_field: str, group_by_field_name: str = "DataRecordName",
                            **kwargs) \
            -> ElnEntryStep:
        """
        Create a gauge chart step in the experiment protocol.
        """
        if not data_source_step.get_data_type_names():
            raise ValueError("The data source step did not declare a data type name.")
        data_type_name: str = data_source_step.get_data_type_names()[0]
        series = GaugeChartSeries(data_type_name, field_name)
        series.operation_type = ChartOperationType.VALUE
        chart = _GaugeChartDefinition()
        chart.main_data_type_name = data_type_name
        chart.status_field = status_field
        chart.minimum_value = 0.
        chart.maximum_value = 100.
        chart.series_list = [series]
        chart.grouping_type = ChartGroupingType.GROUP_BY_FIELD
        chart.grouping_type_data_type_name = data_type_name
        chart.grouping_type_data_field_name = group_by_field_name
        dashboard, step = _ELNStepFactory._create_dashboard_step_from_chart(chart, data_source_step, protocol, step_name,
                                                                            None, **kwargs)
        protocol.invalidate()
        return step

    @staticmethod
    def _create_dashboard_step_from_chart(chart: GaugeChartDefinition, data_source_step: ElnEntryStep,
                                          protocol: ElnExperimentProtocol, step_name: str,
                                          position: ElnEntryPosition | None = None, **kwargs) -> \
            tuple[DashboardDefinition, ElnEntryStep]:
        dashboard: DashboardDefinition = DashboardDefinition()
        dashboard.chart_definition_list = [chart]
        dashboard.dashboard_scope = DashboardScope.PRIVATE_ELN
        dashboard = DataMgmtServer.get_dashboard_manager(protocol.user).store_dashboard_definition(dashboard)
        eln_manager, new_entry = _ELNStepFactory._get_entry_creation_criteria("", protocol, step_name,
                                                                              ElnEntryType.Dashboard, position,
                                                                              **kwargs)
        # noinspection PyTypeChecker
        update_criteria = ElnDashboardEntryUpdateCriteria()
        update_criteria.dashboard_guid = dashboard.dashboard_guid
        update_criteria.data_source_entry_id = data_source_step.get_id()
        update_criteria.entry_height = 500
        eln_manager.update_experiment_entry(protocol.eln_experiment.notebook_experiment_id, new_entry.entry_id,
                                            update_criteria)
        step = ElnEntryStep(protocol, new_entry)
        return dashboard, step

    @staticmethod
    def _get_entry_creation_criteria(data_type_name: str | None, protocol: ElnExperimentProtocol,
                                     step_name: str, entry_type: ElnEntryType, position: ElnEntryPosition | None = None,
                                     **kwargs):
        tab_id: int | None = None
        order: int | None = None
        if position:
            tab_id = position.tab_id
            order = position.order
        # noinspection PyTypeChecker
        last_step: ElnEntryStep = protocol.get_sorted_step_list()[-1]
        if tab_id is None:
            tab_id = last_step.eln_entry.notebook_experiment_tab_id
        if order is None:
            order = last_step.eln_entry.order + 1
        eln_manager = DataMgmtServer.get_eln_manager(protocol.user)
        entry_criteria = _ElnEntryCriteria(entry_type, step_name, data_type_name, order,
                                           notebook_experiment_tab_id=tab_id, **kwargs)
        new_entry: ExperimentEntry = eln_manager.add_experiment_entry(protocol.eln_experiment.notebook_experiment_id,
                                                                      entry_criteria)
        return eln_manager, new_entry


# TODO: Using this to set the new status field setting.
class _GaugeChartDefinition(GaugeChartDefinition):
    status_field: str

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["statusValueField"] = {
            "dataTypeName": self.main_data_type_name,
            "dataFieldName": self.status_field
        }
        return result


class _ElnEntryCriteria(ElnEntryCriteria):
    is_hidden: bool | None
    entry_height: int | None
    description: str | None
    is_initialization_required: bool | None
    collapse_entry: bool | None
    entry_status: ExperimentEntryStatus | None
    template_item_fulfilled_timestamp: int | None

    def __init__(self, entry_type: ElnEntryType, entry_name: str | None, data_type_name: str | None, order: int,
                 is_hidden: bool | None = None, entry_height: int | None = None, description: str | None = None,
                 is_initialization_required: bool | None = None, collapse_entry: bool | None = None,
                 entry_status: ExperimentEntryStatus | None = None, template_item_fulfilled_timestamp: int | None = None,
                 **kwargs):
        super().__init__(entry_type, entry_name, data_type_name, order, **kwargs)
        self.is_hidden = is_hidden
        self.entry_height = entry_height
        self.description = description
        self.is_initialization_required = is_initialization_required
        self.collapse_entry = collapse_entry
        self.entry_status = entry_status
        self.template_item_fulfilled_timestamp = template_item_fulfilled_timestamp

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = super().to_json()
        ret.update({
            "hidden": self.is_hidden,
            "entryHeight": self.entry_height,
            "description": self.description,
            "initializationRequired": self.is_initialization_required,
            "collapsed": self.collapse_entry,
            "entryStatus": self.entry_status,
            "templateItemFulfilledTimestamp": self.template_item_fulfilled_timestamp
        })
        return ret
