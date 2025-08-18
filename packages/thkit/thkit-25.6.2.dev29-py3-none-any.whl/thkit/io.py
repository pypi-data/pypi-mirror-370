from pathlib import Path
from typing import Union

import yaml


#####ANCHOR Read/write files
def write_yaml(jdata: dict, filename: Union[str, Path]):
    """Write data to a YAML file."""
    with open(filename, "w") as f:
        yaml.safe_dump(jdata, f, default_flow_style=False, sort_keys=False)
    return


def read_yaml(filename: Union[str, Path]) -> dict:
    """Read data from a YAML file."""
    with open(filename) as f:
        jdata = yaml.safe_load(f)
    return jdata


#####ANCHOR Modify data
def combine_text_files(files: list[str], output_file: str, chunk_size: int = 1024):
    """
    Combine text files into a single file in a memory-efficient. Read and write in chunks to avoid loading large files into memory

    Args:
        files (list[str]): List of file paths to combine.
        output_file (str): Path to the output file.
        chunk_size (int, optional): Size of each chunk in KB to read/write. Defaults to 1024 KB.
    """
    chunk_size_byte = chunk_size * 1024
    ### Create parent folder if not exist
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    ### Open the output file for writing and append each file's content incrementally
    with open(output_file, "w") as outfile:
        for file in files:
            with open(file, "r") as infile:
                while chunk := infile.read(chunk_size_byte):  # Read in chunks
                    outfile.write(chunk)
    return


def unpack_dict(nested_dict: dict) -> dict:
    """Unpack one level of nested dictionary."""
    # flat_dict = {
    #     key2: val2 for key1, val1 in nested_dict.items() for key2, val2 in val1.items()
    # }

    ### Use for loop to handle duplicate keys
    flat_dict = {}
    for key1, val1 in nested_dict.items():
        for key2, val2 in val1.items():
            if key2 not in flat_dict:
                flat_dict[key2] = val2
            else:
                raise ValueError(
                    f"Key `{key2}` is used multiple times in the same level of the nested dictionary. Please fix it before unpacking dict."
                )
    return flat_dict


#####ANCHOR Download files
def download_rawtext(url: str, outfile: str = None) -> str:
    """Download raw text from a URL."""
    import requests

    res = requests.get(url)
    text = res.text
    if outfile is not None:
        with open(outfile, "w") as f:
            f.write(text)
    return text
