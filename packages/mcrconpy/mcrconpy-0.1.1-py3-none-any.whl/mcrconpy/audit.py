# -*- coding: utf-8 -*-
"""
"""

from mcrconpy.pathclass import PathClass

import json


class Audit:

    LOG_DIR = PathClass.user_log_dir("mcrconpy")
    FILE_PATH = PathClass.join(LOG_DIR, "audit.jsonl")

    """
    """
    @staticmethod
    def to_save(
        data: dict
    ) -> None:
        """
        """
        PathClass.makedirs(Audit.LOG_DIR)
        with open(Audit.FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')

    @staticmethod
    def to_load() -> dict:
        """
        """
        try:
            with open(Audit.FILE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
            return data
        except FileNotFoundError as e:
            return {}
