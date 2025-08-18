import json
import os
import tempfile

"""
A module for atomic file saving operations.
This module provides a function to save data to a file atomically,
ensuring that the file is not left in a corrupted state in case of an error.
"""


def _atomic_save(data: dict, path: str):
    """
    Save data to a file atomically.
    data -- The data to save (must be a dictionary).
    path -- The file path where the data should be saved.
    """
    dir_name = os.path.dirname(path)
    base_name = os.path.basename(path)

    try:
        # 1. Create a temp file in the same directory
        with tempfile.NamedTemporaryFile(
            "w", delete=False, dir=dir_name, prefix=base_name + ".", suffix=".tmp"
        ) as tf:
            temp_path = tf.name
            json.dump(data, tf, indent=2)
            tf.flush()
            os.fsync(tf.fileno())  # ensure data is flushed to disk

        # 2. Atomically replace the target file
        os.replace(temp_path, path)  # atomic on POSIX and modern Windows
    except Exception as e:
        # 3. Clean up temp file if something goes wrong
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e  # re-raise the exception for the caller to handle
