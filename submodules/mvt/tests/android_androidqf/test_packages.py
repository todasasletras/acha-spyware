# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 The MVT Authors.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging
from pathlib import Path

import pytest

from mvt.android.modules.androidqf.packages import Packages
from mvt.common.module import run_module

from ..utils import get_android_androidqf, list_files


@pytest.fixture()
def data_path():
    return get_android_androidqf()


@pytest.fixture()
def parent_data_path(data_path):
    return Path(data_path).absolute().parent.as_posix()


@pytest.fixture()
def file_list(data_path):
    return list_files(data_path)


@pytest.fixture()
def module(parent_data_path, file_list):
    m = Packages(target_path=parent_data_path, log=logging)
    m.from_folder(parent_data_path, file_list)
    return m


class TestAndroidqfPackages:
    def test_packages_list(self, module):
        run_module(module)

        # There should just be 7 packages listed, no detections
        assert len(module.results) == 7
        assert len(module.timeline) == 0

    def test_non_appstore_warnings(self, caplog, module):
        run_module(module)

        assert len(module.detected) == 4

        # Not a super test to be searching logs for this but heuristic detections not yet formalised
        assert (
            'Found a non-system package installed via adb or another method: "com.whatsapp"'
            in caplog.text
        )
        whatsapp_detected = [
            pkg for pkg in module.detected if pkg["name"] == "com.whatsapp"
        ]
        assert len(whatsapp_detected) == 1

        assert (
            'Found a package installed via a browser (installer="com.google.android.packageinstaller"): '
            '"app.revanced.manager.flutter"' in caplog.text
        )
        revanced_detected = [
            pkg
            for pkg in module.detected
            if pkg["name"] == "app.revanced.manager.flutter"
        ]
        assert len(revanced_detected) == 1

        assert (
            'Found a package installed via a third party store (installer="org.fdroid.fdroid"): "org.nuclearfog.apollo"'
            in caplog.text
        )
        # We do not currently flag a third party store as a detection, we only flag the app in the logs.
        appollo_detected = [
            pkg for pkg in module.detected if pkg["name"] == "org.nuclearfog.apollo"
        ]
        assert len(appollo_detected) == 0

    def test_packages_ioc_package_names(self, module, indicators_factory):
        module.indicators = indicators_factory(app_ids=["com.malware.blah"])

        run_module(module)

        possible_detected_app = [
            pkg for pkg in module.detected if pkg["name"] == "com.malware.blah"
        ]
        assert len(possible_detected_app) == 1
        assert possible_detected_app[0]["name"] == "com.malware.blah"
        assert (
            possible_detected_app[0]["matched_indicator"]["value"] == "com.malware.blah"
        )

    def test_packages_ioc_sha256(self, module, indicators_factory):
        module.indicators = indicators_factory(
            files_sha256=[
                "31037a27af59d4914906c01ad14a318eee2f3e31d48da8954dca62a99174e3fa"
            ]
        )

        run_module(module)

        possible_detected_app = [
            pkg for pkg in module.detected if pkg["name"] == "com.malware.muahaha"
        ]
        assert len(possible_detected_app) == 1
        assert possible_detected_app[0]["name"] == "com.malware.muahaha"
        assert (
            possible_detected_app[0]["matched_indicator"]["value"]
            == "31037a27af59d4914906c01ad14a318eee2f3e31d48da8954dca62a99174e3fa"
        )

    def test_packages_certificate_hash_ioc(self, module, indicators_factory):
        module.indicators = indicators_factory(
            app_cert_hashes=[
                "c7e56178748be1441370416d4c10e34817ea0c961eb636c8e9d98e0fd79bf730"
            ]
        )

        run_module(module)

        possible_detected_app = [
            pkg for pkg in module.detected if pkg["name"] == "com.malware.muahaha"
        ]
        assert len(possible_detected_app) == 1
        assert possible_detected_app[0]["name"] == "com.malware.muahaha"
        assert (
            possible_detected_app[0]["matched_indicator"]["value"]
            == "c7e56178748be1441370416d4c10e34817ea0c961eb636c8e9d98e0fd79bf730"
        )
