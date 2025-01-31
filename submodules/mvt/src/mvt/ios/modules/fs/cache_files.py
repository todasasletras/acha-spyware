# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 The MVT Authors.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging
import os
import sqlite3
from typing import Optional, Union

from ..base import IOSExtraction


class CacheFiles(IOSExtraction):
    def __init__(
        self,
        file_path: Optional[str] = None,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        module_options: Optional[dict] = None,
        log: logging.Logger = logging.getLogger(__name__),
        results: Optional[list] = None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            target_path=target_path,
            results_path=results_path,
            module_options=module_options,
            log=log,
            results=results,
        )

    def serialize(self, record: dict) -> Union[dict, list]:
        records = []
        for item in self.results[record]:
            records.append(
                {
                    "timestamp": item["isodate"],
                    "module": self.__class__.__name__,
                    "event": "cache_response",
                    "data": f"{record} recorded visit to URL {item['url']}",
                }
            )

        return records

    def check_indicators(self) -> None:
        if not self.indicators:
            return

        self.detected = {}
        for key, values in self.results.items():
            for value in values:
                ioc = self.indicators.check_url(value["url"])
                if ioc:
                    value["matched_indicator"] = ioc
                    if key not in self.detected:
                        self.detected[key] = [
                            value,
                        ]
                    else:
                        self.detected[key].append(value)

    def _process_cache_file(self, file_path):
        self.log.info("Processing cache file at path: %s", file_path)

        conn = self._open_sqlite_db(file_path)
        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM cfurl_cache_response;")
        except sqlite3.OperationalError:
            return

        key_name = os.path.relpath(file_path, self.target_path)
        if key_name not in self.results:
            self.results[key_name] = []

        for row in cur:
            self.results[key_name].append(
                {
                    "entry_id": row[0],
                    "version": row[1],
                    "hash_value": row[2],
                    "storage_policy": row[3],
                    "url": row[4],
                    "isodate": row[5],
                }
            )

    def run(self) -> None:
        self.results = {}
        for root, _, files in os.walk(self.target_path):
            for file_name in files:
                if file_name != "Cache.db":
                    continue

                file_path = os.path.join(root, file_name)
                self._process_cache_file(file_path)
