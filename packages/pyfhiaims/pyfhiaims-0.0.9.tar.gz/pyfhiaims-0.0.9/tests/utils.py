"""Utility functions for pyaims test suite."""

import yaml

from pyfhiaims.outputs.parser import StdoutParser


def prepare_ref_data(data_dir):
    """Prepare reference data for the output files in `data_dir`.

    Args:
        data_dir : str

    """

    def remove_key(data, key_to_remove):
        if isinstance(data, dict):
            # Remove the key if it exists, then recursively check values
            data.pop(key_to_remove, None)
            for value in data.values():
                remove_key(value, key_to_remove)
        elif isinstance(data, list):
            # Apply the function to each item in the list
            for item in data:
                remove_key(item, key_to_remove)

    for file_name in data_dir.iterdir():
        if file_name.is_file():
            parser = StdoutParser(file_name)
            results = parser.parse()
            remove_key(results, "geometry")
            remove_key(results, "start_time")
            remove_key(results, "end_time")
            remove_key(results, "input")
            remove_key(results, "self_energy")

            with open(data_dir / "ref" / (file_name.stem + ".yaml"), "w") as outfile:
                yaml.dump(results, outfile, default_flow_style=False)


def is_subset(json1, json2):
    """Check if json1 is a subset of a (larger) json2."""

    def _is_subset_list(list1, list2):
        """Check if all dicts in list1 are subsets of dicts in list2."""
        if len(list1) != len(list2):
            return False
        for el1, el2 in zip(list1, list2, strict=False):
            if type(el1) is not type(el2):
                return False
            if isinstance(el1, dict):
                if not _is_subset_dict(el1, el2):
                    return False
            elif isinstance(el1, list):
                if not _is_subset_list(el1, el2):
                    return False
            elif el1 != el2:
                return False
        return True

    def _is_subset_dict(dict1, dict2):
        """Check if dict1 is a subset of dict2."""
        for k, v in dict1.items():
            if k not in dict2:
                return False
            if type(v) is not type(dict2[k]):
                return False
            if isinstance(v, dict):
                if not _is_subset_dict(v, dict2[k]):
                    return False
            elif isinstance(v, list):
                if not _is_subset_list(v, dict2[k]):
                    return False
            elif v != dict2[k]:
                return False
        return True

    return _is_subset_dict(json1, json2)
