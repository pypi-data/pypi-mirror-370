"""
Collection of routines related to merging YAML files together.
"""

import argparse
import asyncio
import copy
import logging
import os
import pathlib
import re
import sys
import time
from collections import OrderedDict
from typing import Union, List, Dict, Set

import yaml
from ruamel.yaml import YAML


log = logging.getLogger()

# Do it once since we'll use this a lot.
yaml_regexp = re.compile("\\.yaml$")


class MergeDicts(dict):
    """Dictionary of deeply merged dictionaries.
    Takes dictionaries as arguments, in order of precedence (defaults) to most precedence
    and deeply merges them, resulting in a single merged dict. The deep merging includes
    merging of deeply nested dicts and lists. By default lists are merged by concatenating
    them together.
    The merge code comes from Salt's PillarStack:
    https://github.com/saltstack/salt/blob/develop/salt/pillar/stack.py
    Merging can be controlled by merge strategies, by default merge-last is used.
    For dicts that means key conflicts are won by dicts later in the args order.
    For lists that means the latter lists are appended to the proceeding lists.
    Strings, ints, bools, and other non-collections are overwritten.
    Example:
        >>> default_config = {
        >>>     'base_value': 'something',
        >>>     'some_dict': {
        >>>         'some_key1': 'value1',
        >>>         'some_key2': 'value2'
        >>>     }
        >>> }
        >>> config = {
        >>>     'some_dict': {
        >>>         'some_key3': 'value3'
        >>>     },
        >>>     'some_list': [1, 2, 3]
        >>> }
        >>> local_config = {
        >>>     'some_dict': {
        >>>         'some_key2': 'overwrite_value2'
        >>>     },
        >>>     'some_list': [4, 5]
        >>> }
        >>> MergeDicts(default_config, config, local_config)
        {
            "base_value": "something",
            "some_dict": {
                "some_key1": "value1",
                "some_key2": "overwrite_value2",
                "some_key3": "value3"
            },
            "some_list": [
                1,
                2,
                3,
                4,
                5
            ]
        }
    Author: Anton
    """

    def __init__(self, *dicts):
        """Initialize MergedDict by merging dicts and turning self into the result.
        Args:
            *dicts (dict): One or more dictionaries to merge. Ordered from least
                precedence (e.g., defaults) to most precedence (e.g., local overwrites).
        """
        self.merge_strategies = {"overwrite", "merge-first", "merge-last", "remove"}
        base_dict = {}
        for next_dict in dicts:
            self._merge_dict(base_dict, next_dict)

        super().__init__(base_dict)

    def _cleanup(self, obj):
        """Clean up merge strategies in dicts (keys of '__')."""
        if obj:
            if isinstance(obj, dict):
                obj.pop("__", None)
                for k, v in obj.items():
                    obj[k] = self._cleanup(v)
            elif isinstance(obj, list) and isinstance(obj[0], dict) and "__" in obj[0]:
                del obj[0]
        return obj

    def _merge_dict(self, base_dict, next_dict_input):
        """Merge dictionaries recursively.
        Args:
             base_dict (dict): Base dict that will be merged into (i.e., least precedence).
             next_dict (dict): Dict to be merged into `base_dict` (i.e., most precedence).
        Returns:
            dict: Resulting merged dict.
        """
        try:
            next_dict = copy.deepcopy(next_dict_input)
            # Get strategy from '__' key, default to 'merge-last'.
            strategy = next_dict.pop("__", "merge-last")

            if strategy not in self.merge_strategies:
                raise Exception(
                    f'Unknown strategy "{strategy}", should be one of {self.merge_strategies}'
                )  # pylint: disable=broad-exception-raised

            if strategy == "overwrite":
                return self._cleanup(next_dict)

            for k, v in next_dict.items():
                if strategy == "remove":
                    base_dict.pop(k, None)
                    continue
                if k in base_dict:
                    if strategy == "merge-first":
                        # merge-first is same as merge-last but the other way round,
                        # so let's switch base_dict[k] and v.
                        base_dict_k = base_dict[k]
                        base_dict[k] = self._cleanup(v)
                        v = base_dict_k
                    if not isinstance(base_dict[k], type(v)):
                        base_dict[k] = self._cleanup(v)
                    elif isinstance(v, dict):
                        base_dict[k] = self._merge_dict(base_dict[k], v)
                    elif isinstance(v, list):
                        base_dict[k] = self._merge_list(base_dict[k], v)
                    else:
                        base_dict[k] = v
                else:
                    base_dict[k] = self._cleanup(v)

            return base_dict
        except Exception as exc:
            log.error("Current Dicts base: %s", base_dict)
            log.error("Current Dicts next: %s", next_dict_input)
            raise exc

    def _merge_list(self, base_list, next_list):
        """Merge lists.
        Args:
             base_list (list): Base list that will be merged into (i.e., least precedence).
             next_list (list): List to be merged into `base_list` (i.e., most precedence).
                By default the lists will be concatenated `base_list + next_list`.
        Returns:
            dict: Resulting merged dict.
        """

        strategy = "merge-last"

        # Check for strategy in first item of list.
        if next_list and isinstance(next_list[0], dict) and "__" in next_list[0]:
            strategy = next_list[0]["__"]
            del next_list[0]

        if strategy not in self.merge_strategies:
            raise Exception(
                f'Unknown strategy "{strategy}", should be one of {self.merge_strategies}'
            )  # pylint: disable=broad-exception-raised

        if strategy == "overwrite":
            return next_list
        if strategy == "remove":
            return [item for item in base_list if item not in next_list]

        if strategy == "merge-first":
            next_list, base_list = base_list, next_list

        if (
            base_list
            and next_list
            and all(
                bool(isinstance(i, dict) and ("id" in i or "name" in i))
                for i in base_list + next_list
            )
        ):

            def const_ordered_dict(dict_list):
                output_dict = OrderedDict()
                for d in dict_list:
                    dict_key = d.get("id") or d.get("name")
                    output_dict[dict_key] = d
                return output_dict

            base_list_dict = const_ordered_dict(base_list)
            next_list_dict = const_ordered_dict(next_list)

            output_list = []
            for base_id, base_val in base_list_dict.items():
                if base_id in next_list_dict:
                    next_val = next_list_dict[base_id]
                    output_list.append(self._merge_dict(base_val, next_val))
                    next_list_dict.pop(base_id, None)
                else:
                    output_list.append(base_val)
            for next_val in next_list_dict.values():
                output_list.append(next_val)

            return output_list

        # merge-last concatenates the lists.
        return base_list + next_list


def yaml_file_to_dict(yaml_file: str) -> dict:
    """
    Convert a YAML file to a dictionary we that can use with the constructor of YAMLMergeDicts
    or if you just need the dictionary version of the YAML file.
    :param yaml_file: YAML file to read in.
    """
    assert yaml_file and isinstance(yaml_file, str)

    try:
        with open(yaml_file, "r", encoding="utf-8") as fh:
            yaml_obj = YAML(typ="safe")
            # This prevents the conversion of dates into something like datetime.date(2017, 8, 19)
            # I got this code from here:
            # https://stackoverflow.com/questions/50900727/skip-converting-entities-while-loading-a-yaml-string-using-pyyaml
            yaml_obj.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
                yaml_obj.constructor.yaml_constructors["tag:yaml.org,2002:str"]
            )
            return yaml_obj.load(fh)
    except Exception as exc:
        logging.error(
            "Failed to load YAML configuration file %s. Syntax error: %s",
            yaml_file,
            exc,
        )
        raise Exception(
            f"Failed to load YAML configuration file {yaml_file}. Syntax error: {exc}"
        ) from exc  # pylint: disable=broad-exception-raised


def write_configuration(yaml_file: str, config: Union[dict, MergeDicts]) -> None:
    """
    Write the configuration to the YAML file given. This routine DOES NOT take a version
    argument. If you want to set the version of the YAML file, set it in the passed
    dictionary ("version:") and it will be written out.
    :param str yaml_file: The YAML file to write the configuration to. If - write to
    stdout.
    :param Union[dict,MergeDicts] config: The dict containing the merged YAML to write.
    """
    assert yaml_file and isinstance(yaml_file, str)
    assert config

    # We have to get rid of the "classness" of MergedDict even though it inherits
    # from dict. Otherwise, the YAML writer puts the dictionary of this class in
    # a "dictitems" variable. The dict(config) gets rid of the class and makes it
    # a regular dict.
    write_config = dict(config) if isinstance(config, MergeDicts) else config
    if yaml_file == "-":
        yaml.dump(write_config, sys.stdout)
    else:
        with open(yaml_file, "w", encoding="utf-8") as fh:
            yaml.dump(write_config, fh)


class YAMLFileClosures:
    """
    Get a set of YAML files grouped together via the parent: field. This class is used when
    you have a potentially partial YAML file and you want a list that contains the paths
    of all the YAML files that are either parents of this file or this file is a parent
    of some children. For example, if you have a hierarchy A -> B -> C, and you give it
    B, it will return A, B, C. If you have a hierarchy A -> B -> {C,D} (both C and D are
    below B), then it will return two sets: (A,B,C) and (A,B,D).

    This class has a bunch of helper routines and it we put these helper routines in this
    class because it encapsulates them nicely.
    """

    def __init__(self, *yamls: List[str], src_dir: str = ""):
        """
        Returns a list of the YAML files given as sets with their parents and all
        their children in each set.
        :param src_dir: The directory to look for the YAML files in.
        Defaults to the current directory.
        :param yamls: The YAML files to merge. These can be relative or absolute
        paths. If they are relative, they should the RELATIVE TO THE src_dir,
        NOT RELATIVE TO THE CURRENT DIRECTORY.
        """
        assert src_dir and isinstance(src_dir, str)
        assert os.path.isdir(src_dir)
        assert all(f and isinstance(f, str) for f in yamls)

        self.source_directory = str(
            pathlib.Path(src_dir).resolve(strict=True)
        )  # Make full path
        # Convert YAML paths to full paths and make sure they exist and that they are
        # contained under the source directory.
        new_yaml_files = []
        for yf in yamls:
            assert re.compile(r"\.yaml$", re.IGNORECASE).search(yf)
            full_path = pathlib.Path(yf)
            if not pathlib.Path(yf).is_absolute():
                if yf.startswith(src_dir):
                    full_path = yf
                else:
                    full_path = os.path.join(self.source_directory, yf)
            full_path = str(
                pathlib.Path(full_path).resolve(strict=True)
            )  # Checks for existence
            # We want to use the pathlib.is_relative_to() function but it is only
            # in Python 3.12 and later!
            assert src_dir in full_path
            new_yaml_files.append(full_path)
        self.yaml_files = new_yaml_files

    def get_id_from_path(self, yaml_path: str) -> str:
        """
        Gets the id of the YAML file from the full file path. This function assumes
        that the file name matches the "id:" line in the file (it must). Also, the file extension
        MUST end with ".yaml".

        :param str yaml_path: The full path to the file on disk.
        :return: The ID that should exist in the YAML file that we get by parsing the path.
        """
        assert yaml_path and isinstance(yaml_path, str)

        if not yaml_regexp.search(yaml_path):
            raise Exception(
                f'{yaml_path} isn\'t of format "*.yaml"'
            )  # pylint: disable=broad-exception-raised
        return pathlib.PurePath(yaml_path).name[:-5]  # Remove .yaml suffix

    async def _populate_mappings(
        self,
        yaml_file: str,
        id_to_path: Dict[str, str],
        up_tree: Dict[str, str],
        down_tree: Dict[str, set],
    ) -> None:
        """
        Populates the id to relpath table, up_tree and the down_tree mapping table.

        :param str yaml_file: The YAML file we'll read for id: and parent: lines.
        :param Dict[str,str] id_to_path: Mapping of YAML ID to the full path.
        :param Dict[str,str] up_tree: Key is YAML ID, value is parent.
        :param Dict[str,set] down_tree: Children before YAML file (the children point
        to this parent).
        """
        assert yaml_file and isinstance(yaml_file, str)
        assert isinstance(id_to_path, dict)
        assert isinstance(down_tree, dict)

        # Algorithm:
        # Get the short name from the relative path.
        # Populate the short name to relative path table
        # Go through each line of the YAML file {
        #   if line is "id:" line, check that the short ID name matches file name.
        #     If not, error.
        #   if line is a parent line {
        #     Add entry in up_tree from this node to parent
        #     Add entry in down_tree from parent to this node
        #   }
        # }
        short_id = self.get_id_from_path(yaml_file)
        id_to_path[short_id] = yaml_file
        with open(yaml_file, encoding="utf-8") as fh:
            file_contents = fh.read()

        for line in file_contents.splitlines():
            if re.compile("^id:").match(line):
                line = re.sub("^id:", "", line)
                line = line.strip()
            if re.compile("^parent:").match(line):
                line = re.sub("^parent:", "", line)
                line = line.strip()
                parent_id = self.get_id_from_path(line)
                up_tree[short_id] = parent_id
                if parent_id in down_tree:
                    down_tree_value: Set[str] = down_tree[parent_id]
                    down_tree_value.add(short_id)
                    down_tree[parent_id] = down_tree_value
                else:
                    down_tree[parent_id] = {short_id}

    def _file_path_already_processed(
        self, file_lists_to_return: List[list], yaml_file: str
    ) -> bool:
        """
        Sees if this yaml_file has already been processed. This will only be true if a different yaml file
        was processed and a list was seen already including this file.

        :param List[list] file_lists_to_return: The lists of list of files we already processed.
        :param str yaml_file: The yaml file we want to see if it is already processed.
        :return: True if it was already processed, false otherwise.
        """
        assert isinstance(file_lists_to_return, list)
        assert yaml_file and isinstance(yaml_file, str)

        for l in file_lists_to_return:
            if yaml_file in l:
                return True
        return False

    def _add_all_parent_yamls(
        self,
        id_to_yaml_mapping: Dict[str, str],
        up_tree: Dict[str, str],
        yamls_for_this_iteration: List[str],
        yaml_file: str,
    ) -> None:
        """
        Goes up the parent tree if this YAML refers to a parent and adds all the parent YAMLs.
        Parent are PREPENDED to the list since they must be processed first by the inheritance
        hierarchy routines.

        :param Dict[str,str] id_to_yaml_mapping: Mapping of ID to full YAML path.
        :param Dict[str,str] up_tree: Key is a YAML ID and the value is the ID of the parent.
        :param Set[str] yamls_for_this_iteration: A list of YAMLs we've processed already.
        This is the data structure updated in this routine.
        :param str yaml_file: New yaml we are processing.
        """
        assert isinstance(id_to_yaml_mapping, dict)
        assert isinstance(yamls_for_this_iteration, list)
        assert yaml_file and isinstance(yaml_file, str)

        yamls_for_this_iteration.insert(0, yaml_file)
        cur_yaml = yaml_file
        while True:
            short_id = self.get_id_from_path(cur_yaml)
            if short_id in up_tree:
                cur_yaml = id_to_yaml_mapping[up_tree[short_id]]
                yamls_for_this_iteration.insert(0, cur_yaml)
            else:
                break

    def _search_for_children_pointing_to_this_parent(
        self,
        id_to_path: Dict[str, str],
        down_tree: Dict[str, set],
        yaml_list: List[str],
        yaml_file: str,
    ) -> List[list]:
        """
        Uses the down_tree to create new list of lists of files to check. When we go down the tree, we can
        create additional lists if the node has 2 or more children. That is why the return value is a list
        of lists. Each list within the outer list contains a list of all the relative paths to merge
        together to make a single YAML file.

        :param Dict[str,str] id_to_path: Mapping of YAML ID to the full path.
        :param Dict[str,set] down_tree: Children below this YAML file (the children point
        to this parent).
        :param List[str] yaml_list: The List of children down the tree for this node.
        :param str yaml_file: The current node in the tree we are processing.
        :return: A list of sets for each child.
        """
        assert isinstance(id_to_path, dict)
        assert isinstance(down_tree, dict)
        assert isinstance(yaml_list, list)
        assert yaml_file and isinstance(yaml_file, str)

        # Algorithm:
        # 	if no parent entry for yaml_file:
        # 		return list_of_yamls
        # 	yaml_lists_to_return = []
        # 	for each child of yaml_file {
        # 		Make new_yaml_list including yaml_list and the child
        # 		yaml_lists.extend(search_for_children_pointing_to_this_parent(id_to_path, down_tree, new_yaml_list, child))
        # 	}
        # 	return yamls_lists
        short_id = self.get_id_from_path(yaml_file)
        if short_id not in down_tree:
            # We return a list of lists since we are going down the tree. Here there is only one
            # list in the embedded list since we don't have any children.
            return [yaml_list]

        children = down_tree[short_id]
        yaml_lists_to_return: List[list] = []
        for child in children:
            new_yaml_list = yaml_list.copy()
            long_child = id_to_path[child]
            new_yaml_list.append(long_child)  # Must go on end!
            yaml_lists_to_return.extend(
                self._search_for_children_pointing_to_this_parent(
                    id_to_path, down_tree, new_yaml_list, long_child
                )
            )
        return yaml_lists_to_return

    async def get_lists(self, verbose: bool = False) -> List[List[str]]:
        """
        Returns the lists of the YAML files in down child order. Each list always returned parent
        first followed by the child below that followed by the child below that.

        Concatenation of YAMLs isn't real concatenation but more complex. See the
        MergeDicts() logic for that. The files are returned from the
        top most parent to the lowest child. This is important as during the coalescing,
        the parent values are taken first, then overridden by its child values and so on.
        Therefore, we need to order the files correctly so YAMLMergeDicts()
        can apply them in the right order.

        When computing the "lists" of each of the files, it follows parents up the tree
        and looks for children down in the tree to compute the sets. This routine contains
        the main logic for computing these sets.

        This function is async for performance reasons. In Python, async functions are viral.
        That is, the functions they call should be async too (if they block in any way).

        :param bool verbose: Print out how long it takes to read all the YAML files.
        :return: The YAML files as lists of lists. Each list element is a list of YAML files
        that should be concatenated together using the MergedDicts algorithm.
        The paths returned are always full paths.
        """
        # Algorithm:
        # for each entry in the source directory tree that is a YAML file  {
        #   Call _populate_mappings() which populates id_to_path, up_tree, and down_tree
        #
        # file_lists_to_return = {}
        # for yaml_file in yaml_files_in_project {
        #     if file in any of file_lists_to_return {
        # 	      continue # previously processed.
        #     }
        #     yamls_for_this_iteration = {}
        #     # Add all parents
        #     add_all_parent_yamls(id_to_path, yamls_for_this_iteration, yaml_file)
        #     # Now find the children
        #     file_lists_to_return.extend(
        #       _search_for_children_point_to_this_parent(id_to_path, down_tree,
        #           yamls_for_this_iteration, yaml_file)
        #     )
        #  }
        # return file_sets_to_return
        id_to_path: Dict[str, str] = {}
        down_tree: Dict[str, set] = {}
        up_tree: Dict[str, str] = {}
        start_time = time.time()
        for root, _, files in os.walk(self.source_directory):
            for file in files:
                full_file_path = f"{root}/{file}"
                if os.path.isfile(full_file_path) and re.compile(
                    r"\.yaml$", re.IGNORECASE
                ).search(file):
                    await self._populate_mappings(
                        full_file_path, id_to_path, up_tree, down_tree
                    )
        end_time = time.time()
        if verbose:
            log.debug(
                "Reading all YAML files under %s (%d secs)",
                self.source_directory,
                int(end_time - start_time),
            )

        file_lists_to_return: List[list] = []
        for yaml_file in self.yaml_files:
            if self._file_path_already_processed(file_lists_to_return, yaml_file):
                continue

            yamls_for_this_iteration: List[str] = []
            self._add_all_parent_yamls(
                id_to_path, up_tree, yamls_for_this_iteration, yaml_file
            )
            # The _search_for_children_pointing_to_this_parent() call may return MULTIPLE sets of files to check
            # since the tree branches multiple ways downward.
            file_lists_to_return.extend(
                self._search_for_children_pointing_to_this_parent(
                    id_to_path, down_tree, yamls_for_this_iteration, yaml_file
                )
            )

        return file_lists_to_return


def normalize_dict(d: dict) -> dict:
    """
    Normalize a YAML dict moving the global sections down into the children of the pipeline
    and steps. It moves global sections down in pipelines too.
    :param d: A denormalized Workflow dictionary.
    :return: The YAML file with the outer global settings removed and moved down into the
    steps sections. Note: all global declarations are for steps information, not pipeline
    information. Some are just named (e.g., extract) or unnamed for all steps (i.e., global).
    """
    assert d and isinstance(d, dict)
    assert (
        "pipelines" in d
    )  # Assures we don't have a YAML fragment and pipelines exists.
    assert isinstance(d["pipelines"], list)

    d_copy = copy.deepcopy(d)  # Don't modify original.
    # Later on if we change the YAML so we don't look for nested "global"s we need to parse
    # a little differently. We can check this version and do that. This isn't currently used.
    version = d_copy.get("version", "1.0.0")  # pylint: disable=unused-variable

    outer_global = inner_global = None
    if "global" in d_copy:
        outer_global = d_copy.pop("global")
        assert isinstance(outer_global, dict)
        if "global" in outer_global:
            inner_global = outer_global.pop("global")
            assert isinstance(inner_global, dict)

    pipelines = d_copy["pipelines"]
    for pipe_count in range(len(pipelines)):  # pylint: disable=consider-using-enumerate
        pipe = pipelines[pipe_count]
        assert isinstance(pipe, dict)
        assert "id" in pipe
        assert isinstance(pipe["id"], str)
        assert "steps" in pipe
        assert isinstance(pipe["steps"], list)

        pipe_outer_global = pipe_inner_global = None
        if "global" in pipe:
            pipe_outer_global = pipe.pop("global")
            assert isinstance(pipe_outer_global, dict)
            if "global" in pipe_outer_global:
                pipe_inner_global = pipe_outer_global.pop("global")
                assert isinstance(pipe_inner_global, dict)

        for step_count in range(
            len(pipe["steps"])
        ):  # We need to modify the list in place.
            step = pipe["steps"][step_count]
            assert isinstance(step, dict)
            assert "id" in step
            assert isinstance(step["id"], str)

            step_id = step["id"]
            if outer_global:
                if step_id in outer_global:
                    # Use the MergeDicts algorithm and NOT the update() method. The update() method
                    # replaces the dictionary. We want to merge them.
                    step = MergeDicts(step, outer_global[step_id])
            # inner_global may be set and outer_global may be an empty dictionary which can
            # evaluate to False. Therefore, don't nest inner_global in the outer_global block.
            if inner_global:
                step = MergeDicts(step, inner_global)
            if pipe_outer_global:
                if step_id in pipe_outer_global:
                    step = MergeDicts(step, pipe_outer_global[step_id])
            if pipe_inner_global:
                step = MergeDicts(step, pipe_inner_global)
            d_copy["pipelines"][pipe_count]["steps"][step_count] = step

    return d_copy


def _key_in_every_pipe_step(step_key: str, step_value, pipe: dict) -> None:
    """
    Determines if the key and value are in every step in a pipeline.
    :param str key: The key to look for in the steps.
    :param value: The value to look for in the steps.
    :param dict pipe: Pipeline dictionary.
    """
    assert step_key and isinstance(step_key, str)
    assert pipe and isinstance(pipe, dict)

    for step in pipe["steps"]:
        if step_key not in step or step[step_key] != step_value:
            return False
    return True


def _key_in_every_pipeline_step(key: str, value, pipelines: list) -> None:
    """
    Checks to see if the step key and value (both must match) is in every step in every pipeline.
    :param str key: The key to look for in the steps.
    :param value: The value to look for in the steps.
    :param list pipelines: The list of pipelines to look in.
    """
    assert key and isinstance(key, str)
    assert pipelines and isinstance(pipelines, list)

    for pipe in pipelines:
        if not _key_in_every_pipe_step(key, value, pipe):
            return False
    return True


def _delete_key_from_every_step(step_key, pipelines) -> None:
    """
    Deletes the key from every step in every pipeline.
    :param str key: The key to look for in the steps.
    :param value: The value to look for in the steps.
    :param list pipelines: The list of pipelines to look in.
    """
    assert step_key and isinstance(step_key, str)
    assert pipelines and isinstance(pipelines, list)

    for pipe in pipelines:
        for step in pipe["steps"]:
            del step[step_key]


def denormalize_dict(d: dict) -> dict:
    """
    Denormalize a YAML dict moving any common settings in steps to either the global section
    for each step or to the global section specific to a pipeline.
    This routine DOES NOT use the pattern based global section. The pattern based global section
    can always be replaced with a non-pattern based global section at the pipeline level.
    We always use the global section local to the pipelines.
    """

    assert d and isinstance(d, dict)
    assert (
        "pipelines" in d
    )  # Assures we don't have a YAML fragment and pipelines exists.
    assert isinstance(d["pipelines"], list)

    d_copy = copy.deepcopy(d)  # Don't modify original.
    # Later on if we change the YAML so we don't look for nested "global"s we need to parse
    # a little differently. We can check this version and do that. This isn't currently used.
    version = d_copy.get("version", "1.0.0")  # pylint: disable=unused-variable

    if "global" in d_copy:
        raise Exception("Outer global section shouldn't exist")

    pipelines = d_copy["pipelines"]
    promotion_globals = {}
    for pipe in pipelines:
        assert pipe["id"]
        pipe_id = pipe["id"]
        if "global" in pipe:
            raise Exception(
                f"Pipeline global section in pipeline {pipe_id} shouldn't exist"
            )
        pipeline_globals = {}
        for step_count in range(len(pipe["steps"])):
            step = pipe["steps"][step_count]
            assert step["id"]
            step_id = step["id"]
            if "global" in step:
                # Probably don't need to check for this but let's be safe.
                raise Exception(
                    f"Step global section in pipeline {pipe_id} step {step_id} shouldn't exist"
                )
            # We have to make a copy of the step since we are modifying it in place.
            for step_key, step_value in step.copy().items():
                if (
                    step_key == "id" or step_key not in step
                ):  # May not be in step since we previously deleted it.
                    continue
                if _key_in_every_pipeline_step(step_key, step_value, pipelines):
                    if step_key not in promotion_globals:
                        promotion_globals[step_key] = step_value
                    _delete_key_from_every_step(step_key, pipelines)
                elif _key_in_every_pipe_step(step_key, step_value, pipe):
                    pipeline_globals[step_key] = step_value
                    # We use the same function that goes through all the pipelines but we make a
                    # list of a single pipeline to clear it out. Since dictionaries are passed by
                    # reference, this should work.
                    _delete_key_from_every_step(step_key, [pipe])
        if pipeline_globals:
            pipe["global"] = {}
            pipe["global"]["global"] = pipeline_globals
    if promotion_globals:
        d_copy["global"] = {}
        d_copy["global"]["global"] = promotion_globals
    return d_copy


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            f"""Usage: python {sys.argv[0]} merge [yaml_file1]...
or
python {sys.argv[0]} file_closure [yaml_file]...""",
            file=sys.stderr,
        )
        sys.exit(1)
    operator = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if operator == "merge":
        parser = argparse.ArgumentParser(
            description="Output a set of files to the stdout according to"
            " the MergedDict algorithm.",
        )
        parser.add_argument(
            "yaml_files",
            nargs="*",
            help="The YAML files to merge",
        )
        args = parser.parse_args()

        yaml_files = args.yaml_files

        for f in yaml_files:
            assert re.compile(r"\.yaml$").search(f, re.IGNORECASE)
        dicts_to_coalesce = [yaml_file_to_dict(f) for f in yaml_files]
        conf_with_merged_yamls = MergeDicts(*dicts_to_coalesce)
        write_configuration("-", conf_with_merged_yamls)
        sys.exit(0)

    if operator == "file_closure":
        parser = argparse.ArgumentParser(
            description="Get a list of YAML files grouped together via the parent: field.",
        )
        parser.add_argument(
            "source_directory", help="The top level directory to look for YAML files."
        )
        parser.add_argument(
            "yaml_files",
            nargs="*",
            help="The YAML files look for parents or children.",
        )
        args = parser.parse_args()
        assert os.path.isdir(args.source_directory)  # Check is a directory.
        source_directory = pathlib.PosixPath(args.source_directory)

        # Check each file exists and is a YAML.
        for f in args.yaml_files:
            assert re.compile(r"\.yaml$", re.IGNORECASE).search(f)
            path = pathlib.PosixPath(f)
            if path.is_absolute():
                assert path.exists()
            else:
                assert os.path.exists(os.path.join(args.source_directory, f))

        yaml_closure = YAMLFileClosures(*args.yaml_files, src_dir=str(source_directory))
        file_lists = asyncio.run(yaml_closure.get_lists())
        for fl in file_lists:
            JOINED_PATHS = ",\n".join(str(f) for f in fl)
            print(f"[\n{JOINED_PATHS}\n]")

        sys.exit(0)
