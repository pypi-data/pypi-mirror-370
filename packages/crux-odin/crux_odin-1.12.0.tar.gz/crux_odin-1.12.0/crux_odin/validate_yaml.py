"""
Collection of routines related to YAML validation.
"""

import argparse
import importlib.resources
import json
import logging
import os
import re
import sys
from typing import Dict, Iterable, List, Tuple

import jsonschema
import yaml  # type: ignore
from croniter import croniter
from ruamel.yaml import YAML

import crux_odin

log = logging.getLogger()

try:
    with importlib.resources.as_file(  # type: ignore
        importlib.resources.files(crux_odin) / "workflow_crd.yaml"  # type: ignore
    ) as p:
        CRUX_WORKFLOW_CRD = str(p)
except AttributeError:
    # supported method for Python 3.8
    with importlib.resources.path(  # pylint: disable=deprecated-method
        crux_odin, "workflow_crd.yaml"
    ) as p:
        CRUX_WORKFLOW_CRD = str(p)


def get_json_schema(version: str) -> Dict:
    """
    Contains the JSON schema that we use for syntactic validation.
    See https://json-schema.org. The schemas for the different versions of the YAMLs
    are stored in the Kubernetes CRD schema file for workflows.
    It is recommended you cache the return value of this function if you are calling it
    over and over again since reading the schema isn't cheap. Also, you can set the
    WORKFLOW_CRD environment variable to the path to the Kubernetes CRD schema file.

    :version str: The version of the schema to get. This may or may be preceded by a 'v'
    (it is optional).
    :return: The dictionary containing the schema rules as a Python Dict.
    """
    assert version and isinstance(version, str)
    assert re.compile(r"^[Vv]?\d+\.\d+\.\d+$").match(version)

    version_desired = version.lower().lstrip("v")  # Remove the 'v' if it is there.
    workflow_crd_file = os.environ.get("WORKFLOW_CRD", CRUX_WORKFLOW_CRD)
    with open(workflow_crd_file, "r", encoding="utf-8") as yaml_fd:
        validate_config = yaml.safe_load(yaml_fd)
    log.debug("Using workflow_crd.yaml file %s", workflow_crd_file)
    if not validate_config.get("spec", {}).get("versions", None):
        raise Exception(
            f"{workflow_crd_file} doesn't contain a ['spec']['versions'] key."
        )  # pylint: disable=broad-exception-raised
    for version_obj in validate_config["spec"]["versions"]:
        if not version_obj.get("name", None):
            raise Exception(
                f"{workflow_crd_file} ['spec']['versions'] object doesn't contain a ['name'] key."
            )  # pylint: disable=broad-exception-raised
        if version_obj["name"] == "v" + version_desired:
            if not version_obj.get("schema", {}).get("openAPIV3Schema", None):
                raise Exception(
                    f"{workflow_crd_file} ['spec']['versions'][name = 'v{version_desired}']"
                    + " doesn't contain a ['schema']['openAPIV3Schema'] key."
                )  # pylint: disable=broad-exception-raised
            return version_obj["schema"]["openAPIV3Schema"]

    raise Exception(
        f"Couldn't find the schema for the version {version} in {workflow_crd_file}"
    )  # pylint: disable=broad-exception-raised


def validate_dict(workflow_dict: Dict) -> None:
    """
    Validates the dictionary against JSON Schema.
    :param Dict workflow_dict: The dictionary to validate.
    """
    # Get the version from the YAML dict.
    version = workflow_dict.get("version")
    if not version:
        version = "1.0.0"  # This version doesn't have a version: field.
    json_schema = get_json_schema(version)

    jsonschema.validate(workflow_dict, json_schema)

    validator = CustomValidations(workflow_dict)
    validator.validate_all()


def validate_yaml(file_name: str) -> None:
    """
    Validates the file according to the schema. The version of the schema is read from
    the YAML file.

    :param str file_name: The name of the file to validate.
    Throws an exception if it doesn't validate correctly.
    """
    assert file_name and isinstance(file_name, str)

    with open(file_name, "r", encoding="utf-8") as fh:
        yaml_obj = YAML(typ="safe")
        # This prevents the conversion of dates into something like datetime.date(2017, 8, 19)
        # I got this code from here:
        # https://stackoverflow.com/questions/50900727/skip-converting-entities-while-loading-a-yaml-string-using-pyyaml
        yaml_obj.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
            yaml_obj.constructor.yaml_constructors["tag:yaml.org,2002:str"]
        )
        yaml_data = yaml_obj.load(fh)

        validate_dict(yaml_data)


class CustomValidations:
    """
    Contains the routines that do custom validations (replaces CDW). All of the custom
    validations are put here to keep the custom validations organized. To use the custom
    validations, simply give a YAML dict to the constructor and run each custom validation
    routine as you wish (or run the validate_all() routine to run all of them).

    The usual scenario is to run all the custom validations over each workflow that we see.
    Therefore, you'll need to create a new CustomValidations object for each workflow that
    you want to process and the constructor of this class takes the YAML dict as an argument.

    This custom validation class DOES NOT run the regular JSON Schema YAML validations before
    running its custom code. It assumes this is run separately.

    Custom validations are actually split into two parts: those that are generic and are run
    for every company using the crux-odin YAML workflows and those that are specific to a
    certain company. For example, saying "two pipelines can't have the same ID" is generic
    and will apply to everyone. But saying that the "action_class" of a step must have the
    value "pipeline.crux_pdk.actions.process.processor.Processor" or
    "pipeline.crux_pdk.actions.process.java_processor.JavaProcessor" are company specific.
    These classes are the action steps of a certain company and any validations of this sort
    do not belong here.
    """

    def __init__(self, workflow_dict: Dict):
        """
        Initializes the object with the dictionary containing the workflow. For each
        new Workflow dict you'll need to create a new object.
        :param Dict workflow_dict: The dictionary containing the workflow.
        """
        assert workflow_dict and isinstance(workflow_dict, dict)
        # We may wish to set "self.workflow_dict = normalize_dict(workflow_dict)" later
        # if needed.
        self.unnormalized_workflow_dict = workflow_dict
        # We may need to vary the behavior based on the version of the Workflow.
        self.version = workflow_dict.get("version", "1.0.0")

    def all_pipelines_in_a_workflow_must_have_a_unique_id(self) -> None:
        """
        Checks if all the pipelines in a workflow have a unique ID.
        """
        pipelines = self.unnormalized_workflow_dict.get("pipelines", [])
        # An empty list can be caught by JSON Schema validation.
        assert pipelines and isinstance(pipelines, list)
        ids = set()
        for pipeline in pipelines:
            pipeline_id = pipeline.get("id")
            assert pipeline_id and isinstance(pipeline_id, str)
            if pipeline_id in ids:
                raise Exception(
                    f"Duplicate pipeline ID {pipeline_id} found in the workflow."
                )
            ids.add(pipeline_id)

    def validate_available_deadline_are_unique(self) -> None:
        """
        Validates that all the availability deadlines are unique.
        """
        availability_deadlines = self.unnormalized_workflow_dict.get(
            "availability_deadlines", []
        )
        assert availability_deadlines and isinstance(availability_deadlines, list)
        ids = set()
        for deadline in availability_deadlines:
            deadline_id = json.dumps(deadline, sort_keys=True)
            assert deadline_id and isinstance(deadline_id, str)
            if deadline_id in ids:
                raise Exception(
                    f"Duplicate availability deadline ID {deadline_id} found in the workflow."
                )
            ids.add(deadline_id)

    def validate_schema_def_consistency(self) -> None:
        """
        Validates consistency between the schema definitions within the workflow.
        Ensures that all configured names and data types in declared and observed schema
        definitions match the main schema definition.
        """
        if not self.version >= "1.3.0":
            return
        pipelines = self.unnormalized_workflow_dict.get("pipelines", [])
        for pipeline in pipelines:
            schema_def = (
                pipeline.get("global", {}).get("global", {}).get("schema_def", {})
            )
            if not schema_def:
                continue
            declared_schema_def = (
                pipeline.get("global", {})
                .get("global", {})
                .get("declared_schema_def", {})
            )
            observed_schema_def = (
                pipeline.get("global", {})
                .get("global", {})
                .get("observed_schema_def", {})
            )

            schema_fields = {
                (field["name"], field["data_type"])
                for field in schema_def.get("fields", [])
            }

            def validate_fields(
                schema_def_fields: List[Dict[str, str]],
                schema_type: str,
                schema_fields: Iterable[Tuple[str, str]],
            ) -> None:
                """
                Validates consistency between the schema definitions within the workflow.
                Ensures that all configured names and data types in declared and observed
                schema definitions match the main schema definition.
                """
                for field in schema_def_fields:
                    configured_name = field.get("configured_name")
                    configured_data_type = field.get("configured_data_type")

                    if configured_name and configured_data_type:
                        if (configured_name, configured_data_type) not in schema_fields:
                            raise ValueError(
                                f"{schema_type} field with configured_name '{configured_name}' and "
                                f"configured_data_type '{configured_data_type}' not found in schema_def."
                            )

            if declared_schema_def:
                validate_fields(
                    declared_schema_def.get("fields", []),
                    "declared_schema_def",
                    schema_fields,
                )

            if observed_schema_def:
                validate_fields(
                    observed_schema_def.get("fields", []),
                    "observed_schema_def",
                    schema_fields,
                )

    def validate_cron_schedule(self) -> None:
        """Validates the cron schedule in dag.schedule_interval is valid."""
        if not self.version >= "1.1.0":
            return

        if (
            "dag" not in self.unnormalized_workflow_dict
            or "schedule_interval" not in self.unnormalized_workflow_dict["dag"]
        ):
            raise ValueError("dag.schedule_interval is missing in the workflow.")
        if self.unnormalized_workflow_dict["dag"][
            "schedule_interval"
        ] and not isinstance(
            self.unnormalized_workflow_dict["dag"]["schedule_interval"], str
        ):
            raise ValueError("dag.schedule_interval must be a string.")

        cron_schedule = self.unnormalized_workflow_dict["dag"]["schedule_interval"]
        if not cron_schedule or cron_schedule in ("None", "null", "@once"):
            return  # croniter doesn't understand this but we allow it.
        cron_split = cron_schedule.split()
        if (
            len(cron_split) != 1 and len(cron_split) != 5
        ):  # croniter allows 6 fields but we don't.
            raise ValueError(
                f"Invalid cron schedule '{cron_schedule}' for dag.schedule_interval."
            )
        if not croniter.is_valid(cron_schedule):
            raise ValueError(
                f"Invalid cron schedule '{cron_schedule}' for dag.schedule_interval."
            )

    def validate_all(self) -> None:
        """
        Runs all the custom validations for the dictionary passed in the constructor.
        """
        self.all_pipelines_in_a_workflow_must_have_a_unique_id()
        self.validate_schema_def_consistency()
        self.validate_cron_schedule()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="validate_yaml",
        description="Checks if a YAML file is valid.",
    )
    parser.add_argument("filename", nargs="+", help="List of file names to check.")
    args = parser.parse_args()
    for f in args.filename:
        try:
            validate_yaml(f)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            print(ex, file=sys.stderr)
            sys.exit(1)
    sys.exit(0)
