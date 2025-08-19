"""
Contains the python Dataclasses and the methods associated with them.
"""

import argparse
import asyncio
import json
import os
import sys
from pprint import pformat
from typing import Any, Dict, List, Optional, Union, Literal

import yaml  # type: ignore
from pydantic import BaseModel, Field

from crux_odin.dict_utils import (
    MergeDicts,
    YAMLFileClosures,
    denormalize_dict,
    normalize_dict,
    yaml_file_to_dict,
)
from crux_odin.types.deadlines import (
    DeadlineDayOfMonth,
    DeadlineDayOfWeek,
    DeadlineHour,
    DeadlineMinute,
    DeadlineMonth,
    DeadlineYear,
    FileFrequency,
    Timezone,
)
from crux_odin.validate_yaml import validate_dict


class AllObjects(BaseModel):
    """
    This class is a placeholder above ALL the objects in the tree.
    It is a convenient place to place dynamic binding methods and it also
    can be used as the supertype if you ever want to refer to ANY object.
    """

    def validator(self) -> None:
        """
        This method is used to validate the object. Each object should be
        able to validate itself so we can use assertions like
        assert obj.validator()
        Each class should override this method when the validation is written.
        """
        # If you wanted to validate using JSON Schema you could do something like:
        # validate_dict(self.model_dump(exclude_none=True, exclude_unset=True))
        # but Pydantic already does a good job of validating this kind of stuff.
        # This routine is more meant to validate things that Pydantic can't do.

    def dump_yaml(self) -> str:
        """
        Dumps the object into a YAML string.
        """
        return yaml.dump(self.dump_denormalized())

    def dump_json(self) -> str:
        """
        Dumps the object into a JSON string. We don't use the BaseModel.model_dump_json()
        method because our POPO has the crux_api_conf variable at the top level. That isn't
        where it is normally dumped. It resides under global:->global:. dump_denormalized()
        moves it there.
        """
        return json.dumps(self.dump_denormalized(), indent=4)

    def dump_denormalized(self) -> Dict[str, Any]:
        """
        Dumps into a dict that is denormalized. When we create the Workflow POPO, we normalize
        all the global sections. When we dump it again, you may wish to dump it using the
        normalized method. If you want to do that, you use the built in Pydantic
        model_dump(exclude_none=True, exclude_unset=True)
        function. If you want to dump it denormalized with the global sections recreated, use this
        method. We have  to move the crux_api_conf variable under global/global since it is special.
        crux_api_conf can't reside at the top most level in the YAML file.
        :return: Dict that is denormalized.
        """
        dump_dict = denormalize_dict(
            self.model_dump(exclude_none=True, exclude_unset=True)
        )
        return dump_dict


class DagObject(AllObjects):
    """
    The DAG object used in a Workflow.
    """

    # See this discussion on which fields are required:
    # https://cruxinformatics.slack.com/archives/C01C1C7MBMW/p1717060210775299?thread_ts=1716998694.571799&cid=C01C1C7MBMW
    # This document discusses these fields:
    # https://cruxinformatics.atlassian.net/wiki/spaces/TECH/pages/477954521/Onboarding+your+first+Airflow+Dag+on+Cloud+Composer
    max_active_runs: int
    owner: str
    schedule_interval: Optional[str] = None
    priority_weight: int
    dag_start_date: str
    dag_catchup: bool
    enable_delivery_cache: Optional[bool] = False  # deprecated and ignored
    queue: Optional[str] = None
    tags: Optional[List] = None
    dag_end_date: Optional[str] = None


class AvailabilityDeadline(AllObjects):
    """
    Object for a deadline notification
    """

    deadline_minute: DeadlineMinute
    deadline_hour: DeadlineHour
    deadline_day_of_month: DeadlineDayOfMonth
    deadline_month: DeadlineMonth
    deadline_day_of_week: DeadlineDayOfWeek
    deadline_year: DeadlineYear = "*"
    file_frequency: FileFrequency
    timezone: Timezone = "UTC"

    def __eq__(self, other):
        if not isinstance(other, AvailabilityDeadline):
            return NotImplemented
        return (
            self.deadline_minute == other.deadline_minute
            and self.deadline_hour == other.deadline_hour
            and self.deadline_day_of_month == other.deadline_day_of_month
            and self.deadline_month == other.deadline_month
            and self.deadline_day_of_week == other.deadline_day_of_week
            and self.deadline_year == other.deadline_year
            and self.file_frequency == other.file_frequency
            and self.timezone == other.timezone
        )

    def __lt__(self, other):
        if not isinstance(other, AvailabilityDeadline):
            return NotImplemented

        if self.timezone != other.timezone:
            raise ValueError("Cannot compare deadlines with different timezones")

        def convert_cron_value(value):
            try:
                return int(value)
            except ValueError:
                if value.startswith("*/"):
                    return 0
                return float("inf")

        self_values = (
            convert_cron_value(self.deadline_year),
            convert_cron_value(self.deadline_month),
            convert_cron_value(self.deadline_day_of_month),
            convert_cron_value(self.deadline_day_of_week),
            convert_cron_value(self.deadline_hour),
            convert_cron_value(self.deadline_minute),
        )
        other_values = (
            convert_cron_value(other.deadline_year),
            convert_cron_value(other.deadline_month),
            convert_cron_value(other.deadline_day_of_month),
            convert_cron_value(other.deadline_day_of_week),
            convert_cron_value(other.deadline_hour),
            convert_cron_value(other.deadline_minute),
        )
        return self_values < other_values

    def __str__(self):
        return (
            f"Cron: {self.cron()} "
            f"File Frequency: {self.file_frequency}, Timezone: {self.timezone}"
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"deadline_minute={self.deadline_minute!r}, "
            f"deadline_hour={self.deadline_hour!r}, "
            f"deadline_day_of_month={self.deadline_day_of_month!r}, "
            f"deadline_month={self.deadline_month!r}, "
            f"deadline_day_of_week={self.deadline_day_of_week!r}, "
            f"deadline_year={self.deadline_year!r}, "
            f"file_frequency={self.file_frequency!r}, "
            f"timezone={self.timezone!r})"
        )

    def cron(self) -> str:
        """
        Returns the cron representation of the deadline.
        :return: A string that represents the cron schedule.
        """
        return (
            f"{self.deadline_minute} {self.deadline_hour} "
            f"{self.deadline_day_of_month} {self.deadline_month} {self.deadline_day_of_week} "
            f"{self.deadline_year}"
        )


class DeclaredField(AllObjects):
    """
    Object for a declared field
    """

    name: str
    data_type: Optional[str] = "STRING"
    description: Optional[str] = ""
    page_number: Optional[int] = None
    column_number: Optional[int] = None
    is_primary_key: bool = False
    configured_data_type: Optional[str] = ""
    configured_name: Optional[str] = ""


class DeclaredSchemaDef(AllObjects):
    """
    Object for a declared schema
    """

    vendor_table_name: Optional[str] = ""
    vendor_table_description: Optional[str] = ""
    vendor_schedule: Optional[str] = ""
    version: Optional[str] = "1.0"
    date_format: Optional[str] = None
    fields: Optional[List[DeclaredField]] = []


class Step(AllObjects):
    """
    The step object in a Workflow.
    """

    # DO NOT validate with 'pattern=r"^[a-zA-Z_]([a-zA-Z0-9_]*[a-zA-Z0-9])?$"'
    # because it may be the case that a YAML fails validation (the "id:" starts with
    # a digit) but we still want to create the Workflow. See CXP-12250. Hydration
    # still creates the Workflow object and it has to succeed even if strict validation
    # fails.
    id: str = Field(...)
    action_class: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None
    chunk_size: Optional[int] = None
    conf: Optional[Dict[str, Any]] = None
    connection: Optional[Dict[str, Any]] = None
    connection_lib: Optional[str] = None
    delimiter: Optional[str] = None
    doc_type: Optional[str] = None
    doc_type_schema: Optional[List[str]] = None
    encoding: Optional[str] = None
    endpoint: Optional[str] = None
    error_bad_lines: Optional[bool] = None
    escapechar: Optional[str] = None
    extractor_concurrency: Optional[int] = None
    fetch_method: Optional[str] = None
    file_available_end_date: Optional[str] = None
    file_available_start_date: Optional[str] = None
    file_has_header: Optional[bool] = None
    file_header_row_index: Optional[int] = None
    file_optional: Optional[bool] = None
    header_patterns: Optional[List[str]] = None
    idtype: Optional[str] = None
    ignore_paths: Optional[List[str]] = None
    ignore_quotes: Optional[bool] = None
    interim_line_ending: Optional[str] = None
    is_empty_file_ok: Optional[bool] = None
    is_us_dataset: Optional[bool] = None
    is_value_list: Optional[str] = None
    latest_only: Optional[bool] = None
    local_file_name: Optional[str] = None
    melt_column_pattern: Optional[str] = None
    metadata_fields: Optional[Dict[str, Any]] = None
    min_date_filter: Optional[str] = None
    output_file_format: Optional[str] = None
    parquet_page_size: Optional[int] = None
    parquet_row_group_size: Optional[int] = None
    path_nesting_level: Optional[int] = None
    pipeline_row_schema: Optional[Any] = None
    process_max_heap: Optional[int] = None
    provenance_file_patterns: Optional[Dict[str, Any]] = None
    quotechar: Optional[str] = None
    raw_encoding: Optional[str] = None
    remote_file_name: Optional[Union[str, list]] = None
    remote_path: Optional[str] = None
    removal_strings: Optional[List[str]] = None
    remove_namespace: Optional[bool] = None
    rename_identifiers: Optional[bool] = None
    replacement_values: Optional[Dict[str, Any]] = None
    row_schema: Optional[Any] = None
    schema_def: Optional[Dict[str, Any]] = None
    declared_schema_def: Optional[DeclaredSchemaDef] = None
    observed_schema_def: Optional[Dict[str, Any]] = None
    sets_field: Optional[str] = None
    sheet_to_normalize: Optional[str] = None
    skip_footer: Optional[bool] = None
    skip_header: Optional[bool] = None
    skip_rows: Optional[List[int]] = None
    strip_trailing_delimiter: Optional[bool] = None
    supplier_implied_date_regex: Optional[Union[str, list]] = None
    supplier_implied_date_var: Optional[str] = None
    table_identifier: Optional[str] = None
    timedelta: Optional[Dict[str, Any]] = None
    unzip_patterns: Optional[List[str]] = None
    use_simple_preprocessing: Optional[bool] = None
    write_header: Optional[bool] = None
    writer_queue_chunk_size: Optional[int] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Config for pydantic"""

        # extra = "allow" # Turning this on allows extra fields we didn't declare to be
        # written out on write.
        arbitrary_types_allowed = True


class Pipeline(AllObjects):
    """
    The pipelines of a Workflow.
    """

    # DO NOT validate with 'pattern=r"^[a-zA-Z_]([a-zA-Z0-9_]*[a-zA-Z0-9])?$"'
    # because it may be the case that a YAML fails validation (the "id:" starts with
    # a digit) but we still want to create the Workflow. See CXP-12250. Hydration
    # still creates the Workflow object and it has to succeed even if strict validation
    # fails.
    id: str = Field(
        ...,
    )
    steps: Optional[List[Step]] = None
    vendor_doc: Optional[str] = None

    def get_step(self, step_id) -> Optional[Step]:
        """
        This method returns the step object in pipeline by step_id
        :param step_id: Step ID.
        """
        assert step_id and isinstance(step_id, str)

        for step in self.steps:  # pylint: disable=not-an-iterable
            if step.id == step_id:
                return step
        return None

    def get_schema_def(self, step_id: str = "process") -> Optional[Dict[str, Any]]:
        """
        This method returns the schema def for a step. As steps in a pipeline have same schema defs,
        get the schema from the first step.
        """
        if not self.steps:
            return None

        step = self.get_step(step_id)
        return step.schema_def

    def get_declared_schema_def(
        self, step_id: str = "process"
    ) -> Optional[DeclaredSchemaDef]:
        """
        This method returns the declared schema def for a step. As steps in a pipeline have same declared schema defs,
        get the schema from the first step.
        """
        if not self.steps:
            return None

        step = self.get_step(step_id)
        return step.declared_schema_def

    def get_observed_schema_def(
        self, step_id: str = "process"
    ) -> Optional[Dict[str, Any]]:
        """
        This method returns the observed schema def for a step. As steps in a pipeline have same observed schema defs,
        get the schema from the first step.
        """
        if not self.steps:
            return None

        step = self.get_step(step_id)
        return step.observed_schema_def

    def set_schema_def(
        self, schema_def: Dict[str, Any], step_id: str = "process"
    ) -> None:
        """
        This method sets the schema def for steps in a pipeline. As steps in a pipeline have same schema defs,
        set this for all the steps for a pipeline.

        :param declared_schema_def: a schema definition.
        """

        step = self.get_step(step_id)
        step.schema_def = schema_def

    def set_declared_schema_def(
        self, declared_schema_def: DeclaredSchemaDef, step_id: str = "process"
    ) -> None:
        """
        This method sets the declared schema def for a step in a pipeline. As steps in a pipeline have same
        declared schema defs, set this for all the steps for a pipeline.

        :param declared_schema_def: The declared schema definition.
        :return: None
        """
        step = self.get_step(step_id)
        step.declared_schema_def = declared_schema_def

    def set_observed_schema_def(
        self, observed_schema_def: Dict[str, Any], step_id: str = "process"
    ) -> None:
        """
        This method sets the observed schema def for a step in a pipeline

        :param observed_schema_def: The declared schema definition.
        :return: None
        """
        step = self.get_step(step_id)
        step.observed_schema_def = observed_schema_def

    class Config:  # pylint: disable=too-few-public-methods
        """Config for pydantic"""

        arbitrary_types_allowed = True


# Catalog and VendorDeclarations are not used in the Workflow object but they are used
# by other libraries.
class VendorDeclarations(AllObjects):
    """
    Vendor declarations in a Workflow.
    """

    vendor_doc: Optional[str] = None
    schema_def: Optional[Dict[str, Any]] = None
    table_metadata: Optional[Dict[str, Any]] = None


class Catalog(AllObjects):
    """
    Catalog metadata for a Workflow.
    """

    vendor_declarations: Optional[Dict[str, VendorDeclarations]] = None


class Destination(AllObjects):
    """
    Delivery destinations for a Workflow.
    """

    destination_id: str
    name: Optional[str] = None


class Annotations(BaseModel):
    """Adding annotations to the workflow"""

    ENV: Literal["PRODUCTION", "TEST"] = Field(
        default="PRODUCTION",
        description="Specifies the environment. Must be either PRODUCTION or TEST.",
    )


class Workflow(AllObjects):
    """
    Top level Workflow object that represents a whole workflow. This class is polymorphic
    and can hold workflows of any type. Any new workflows inherit from this class.
    This is the outer most object of a workflow and a workflow is a YAML file (they are
    one-to-one).

    When this object is instantiated, the "global" sections have already been normalized
    into the steps and the global sections are gone. Therefore, you won't see references
    to the global sections here. On write, we'll recreate these global sections.
    """

    # DO NOT validate with 'pattern=r"^[a-zA-Z_]([a-zA-Z0-9_]*[a-zA-Z0-9])?$"'
    # because it may be the case that a YAML fails validation (the "id:" starts with
    # a digit) but we still want to create the Workflow. See CXP-12250. Hydration
    # still creates the Workflow object and it has to succeed even if strict validation
    # fails.
    id: str = Field(...)
    pipelines: Optional[List[Pipeline]] = None
    parent: Optional[str] = None
    run_uber_step: Optional[bool] = None
    annotations: Optional[Annotations] = Annotations()
    version: Optional[str] = "1.0.0"
    crux_api_conf: Optional[object] = None

    # Two notes:
    # 1. You won't see global/global here because when the Workflow is created
    #    the global sections are normalized into the steps. See this line in
    #    create_workflow:
    #    workflow_dict = _elevate_crux_api_conf(normalize_dict(yaml_workflow_dict))
    #    You'll find the fields you are looking for IN EACH STEP if you want them
    #    in the Workflow object.
    # 2. "global" is a reserved word in Python so if you DID want to suck in
    #    the global section you'd have to do something like
    #    globals: Optional[Dict[str, Any]] = Field(None, alias="global")

    def get_pipeline(self, pipeline_id) -> Optional[Pipeline]:
        """
        This method returns the step objects of a pipeline_id and step_id in a workflow.
        :param pipeline_id: Pipeline ID.
        """
        if not pipeline_id:
            return None

        for pipeline in self.pipelines:  # pylint: disable=not-an-iterable
            if pipeline.id == pipeline_id:
                return pipeline
        return None

    def get_all_pipeline_schema_defs(self) -> List[Dict[str, Any]]:
        """
        This method returns schema defs for every pipeline in a workflow.
        """
        schema_defs = []
        for pipeline in self.pipelines:  # pylint: disable=not-an-iterable
            schema_def = pipeline.get_schema_def()
            schema_defs.append(schema_def)
        return schema_defs

    def set_all_pipeline_schema_defs(self, schema_defs: List[Dict[str, Any]]) -> None:
        """
        This method sets schema defs for every pipeline in a workflow.
        :param schema_defs
        """
        if len(schema_defs) != len(self.pipelines):
            raise ValueError(
                "Number of schema defs doesn't match with number of pipelines"
            )

        for i, pipeline in enumerate(self.pipelines):
            pipeline.set_schema_def(schema_defs[i])

    def get_all_pipeline_declared_schema_defs(self) -> List[DeclaredSchemaDef]:
        """
        This method returns declared schema defs for every pipeline in a workflow.
        """
        declared_schema_defs = []
        for pipeline in self.pipelines:  # pylint: disable=not-an-iterable
            schema_def = pipeline.get_declared_schema_def()
            declared_schema_defs.append(schema_def)
        return declared_schema_defs

    def set_all_pipeline_declared_schema_defs(
        self, declared_schema_defs: List[DeclaredSchemaDef]
    ) -> None:
        """
        This method sets declared schema defs for every pipeline in a workflow.
        :param delcared_schema_defs
        """
        if len(declared_schema_defs) != len(self.pipelines):
            raise ValueError(
                "Number of schema defs doesn't match with number of pipelines"
            )

        for i, pipeline in enumerate(self.pipelines):
            pipeline.set_declared_schema_def(declared_schema_defs[i])


class Workflow_1_1(Workflow):  # pylint: disable=invalid-name
    """
    Workflow for version 1.1.0 of the crux-odin library.
    """

    dag: Optional[DagObject] = None
    kubernetes: Optional[Dict] = None


class Workflow_1_2(Workflow_1_1):  # pylint: disable=invalid-name
    """
    Workflow for version 1.2.0 of the crux-odin library.
    """

    # This must contain dataset_id, data_product_id, and org_id
    metadata: Optional[Dict[str, Any]] = None


class Workflow_1_4(Workflow_1_2):  # pylint: disable=invalid-name
    """
    Workflow for version 1.4.0 of the crux-odin library.
    """

    availability_deadlines: List[AvailabilityDeadline]


class Workflow_1_5(Workflow_1_4):  # pylint: disable=invalid-name
    """
    Workflow for version 1.5.0 of the crux-odin library.
    """

    destinations: Optional[List[Destination]] = None


def _elevate_crux_api_conf(workflow_dict: Dict) -> Dict:
    """
    This method elevates the crux_api_conf from the steps level to the workflow level.
    This is done because the crux_api_conf is a global setting and should be available
    at the workflow level. We select the last crux_api_conf seen but it shouldn't make a
    difference if there are multiple ones (there shouldn't be).
    """
    assert workflow_dict and isinstance(workflow_dict, dict)
    assert "pipelines" in workflow_dict and isinstance(workflow_dict["pipelines"], list)

    for pipeline in workflow_dict["pipelines"]:
        assert "steps" in pipeline and isinstance(pipeline["steps"], list)
        for step in pipeline["steps"]:
            if "conf" in step and "crux_api_conf" in step["conf"]:
                # The "if" statement prevents overwriting an existing global crux_api_conf.
                if "crux_api_conf" not in workflow_dict:
                    workflow_dict["crux_api_conf"] = step["conf"]["crux_api_conf"]
                del step["conf"]["crux_api_conf"]
            if "crux_api_conf" in step:
                if "crux_api_conf" not in workflow_dict:
                    workflow_dict["crux_api_conf"] = step["crux_api_conf"]
                del step["crux_api_conf"]

    return workflow_dict


def create_workflow(yaml_workflow_dict: Dict, do_validation: bool = True) -> Workflow:
    """
    This is the main factory that creates a new Workflow object. The
    version is taken from the YAML file itself.
    :param yaml_workflow_dict: Dict that contains the Workflow.
    """
    assert yaml_workflow_dict and isinstance(yaml_workflow_dict, dict)
    assert isinstance(do_validation, bool)

    if do_validation:
        validate_dict(yaml_workflow_dict)
    workflow_dict = _elevate_crux_api_conf(normalize_dict(yaml_workflow_dict))

    version = yaml_workflow_dict.get("version", "1.0.0")
    assert isinstance(version, str)
    if version.startswith("1.0"):
        workflow = Workflow.model_validate(workflow_dict)
    elif version.startswith("1.1"):
        workflow = Workflow_1_1.model_validate(workflow_dict)
    elif version.startswith(("1.2", "1.3")):
        # 1.3.0 fields are contained in the global:/global: and we can't declare them in POPO.
        workflow = Workflow_1_2.model_validate(workflow_dict)
    elif version.startswith("1.4"):
        workflow = Workflow_1_4.model_validate(workflow_dict)
    elif version.startswith("1.5"):
        workflow = Workflow_1_5.model_validate(workflow_dict)
    else:
        raise ValueError(f"Version {version} not supported.")
    return workflow


def _create_workflow_for_yamls_and_check_export(
    yaml_files: List[str], verbose: bool = False
) -> None:
    """
    This method creates a workflow for a set of YAML files.
    :param yaml_files: List of YAML files.
    :param verbose: Whether to be chatty.
    """
    assert yaml_files and isinstance(yaml_files, list)
    assert all(isinstance(yaml_file, str) for yaml_file in yaml_files)

    dicts_to_coalesce = [yaml_file_to_dict(p) for p in yaml_files]
    dict_with_merged_yamls = MergeDicts(*dicts_to_coalesce)
    try:
        if verbose:
            print(f"Creating workflow for {yaml_files}")
        workflow = create_workflow(dict_with_merged_yamls)
    except Exception as ex:  # pylint: disable=broad-except
        print(f"Create workflow error in {yaml_files}: {ex}", file=sys.stderr)
        return
    if verbose:
        print(f"Original workflow to workflow dump comparison for {yaml_files}")
    # Remove crux_api_conf as we don't want to compare it.
    normalized_original = _elevate_crux_api_conf(normalize_dict(dict_with_merged_yamls))
    if "crux_api_conf" in normalized_original:
        del normalized_original["crux_api_conf"]
    # Dump should be normalized.
    dumped_workflow = _elevate_crux_api_conf(
        workflow.model_dump(exclude_none=True, exclude_unset=True)
    )
    if "crux_api_conf" in dumped_workflow:
        del dumped_workflow["crux_api_conf"]
    diffs = workflow_dicts_different(normalized_original, dumped_workflow)
    if diffs:
        print(f"Workflow dump comparison failed for {yaml_files}", file=sys.stderr)
        print(diffs, file=sys.stderr)


def _create_workflows_from_directory(
    yaml_directory: str,
    verbose: bool = False,
) -> None:
    """
    This method creates workflows from all the YAML files in a directory.
    :param yaml_directory: Directory that contains the YAML files.
    :param verbose: Whether to be chatty.
    """
    assert yaml_directory and isinstance(yaml_directory, str)
    assert os.path.isdir(yaml_directory)

    yaml_paths: List[str] = []
    for root, _, files in os.walk(yaml_directory):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                yaml_paths.append(file_path)
    # Handle parent/child relationships
    directory_closure = YAMLFileClosures(*yaml_paths, src_dir=yaml_directory)
    yamls_to_group_as_paths: List[list] = asyncio.run(directory_closure.get_lists())
    for yaml_group in yamls_to_group_as_paths:
        _create_workflow_for_yamls_and_check_export(yaml_group, verbose=verbose)


def _dictionaries_are_different(
    dict1: Dict, dict2: Dict, message_prefix: str = ""
) -> str:
    """
    Compares two dictionaries to see if the keys and values are the same. If they aren't,
    then a string describing the differences is returned.
    :param dict1: First dictionary.
    :param dict2: Second dictionary.
    :param message_prefix: Prefix to add to the message.
    :return str: String describing the differences or an empty string if they are the same.
    """
    assert dict1 and isinstance(dict1, dict)
    assert dict2 and isinstance(dict2, dict)

    if dict1 == dict2:
        return ""
    problems = ""
    for key, value in dict1.items():
        if key not in dict2:
            problems += f"{message_prefix}Key {key} not in workflow 2.\n"
        elif dict2[key] != value:
            problems += (
                f"{message_prefix}Key {key} in workflow 1 is different from workflow 2.\n"
                + f"workflow 1: {pformat(value)}\nworkflow 2: {pformat(dict2[key])}\n"
            )
    for key, value in dict2.items():
        if key not in dict1:
            problems += f"{message_prefix}Key {key} not in workflow 1.\n"
    return problems


def workflow_dicts_different(wf1: Dict, wf2: Dict) -> str:
    """
    This method compares two workflow dictionaries and returns a string noting their differences
    if they are different. If they are the same, an empty string is returned. This DOES NOT
    take into account normalization or denormalization. If you compare a normalized dict
    with a denormalized dict they probably will fail the comparison. Therefore, make sure that
    both dicts are normalized or denormalized.
    :param wf1: Dict containing a workflow dictionary.
    :param wf2: Dict containing a workflow dictionary.
    """
    assert wf1 and isinstance(wf1, dict)
    assert wf2 and isinstance(wf2, dict)
    assert "id" in wf1 and "id" in wf2
    assert "pipelines" in wf1 and "pipelines" in wf2
    assert isinstance(wf1["pipelines"], list) and isinstance(wf2["pipelines"], list)

    # For the algorithm, since most of the YAML are dictionaries we should just be able to compare
    # the dictionary values. However, for pipelines, they can be in any order so we need to compare them
    # unordered.
    if wf1 == wf2:
        return ""
    wf1_no_pipelines = wf1.copy()
    del wf1_no_pipelines["pipelines"]
    wf2_no_pipelines = wf2.copy()
    del wf2_no_pipelines["pipelines"]
    problems = _dictionaries_are_different(wf1_no_pipelines, wf2_no_pipelines)
    pipeline1_dict = {}
    pipeline2_dict = {}
    for pipeline in wf1["pipelines"]:
        pipeline1_dict[pipeline["id"]] = pipeline
    for pipeline in wf2["pipelines"]:
        pipeline2_dict[pipeline["id"]] = pipeline
    problems += _dictionaries_are_different(
        pipeline1_dict, pipeline2_dict, message_prefix="Pipeline "
    )
    return problems


if __name__ == "__main__":
    # Tests creating Workflows for a set of YAML files.
    parser = argparse.ArgumentParser(
        prog="dataclass",
        description="Creates workflows for all the YAMLs in a directory hierarchy.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "directory",
        help="Directory that contains YAML files.",
    )

    VERBOSE = False
    args = parser.parse_args()
    if args.verbose:
        VERBOSE = True
    directory = args.directory
    _create_workflows_from_directory(directory, verbose=VERBOSE)
