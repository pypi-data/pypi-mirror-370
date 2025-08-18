import glob
import os
from unittest import mock

import responses  # type: ignore

from smart_tests.test_runners.cucumber import _create_file_candidate_list, clean_uri
from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class CucumberTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath("report/*.xml")), recursive=True):
            reports.append(f)
        result = self.cli('record', 'test', 'cucumber', '--session', self.session_name, '--build',
                          self.build_name, '--base', str(self.test_files_dir), *reports)
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_from_json(self):
        # Override session name lookup to allow session resolution
        responses.replace(
            responses.GET,
            f"{get_base_url()}/intake/organizations/{self.organization}/workspaces/"
            f"{self.workspace}/builds/{self.build_name}/test_session_names/{self.session_name}",
            json={
                'id': self.session_id,
                'isObservation': False,
            },
            status=200)

        reports = []
        for f in glob.iglob(str(self.test_files_dir.joinpath("report/*.json")), recursive=True):
            reports.append(f)
        result = self.cli(
            'record',
            'test',
            'cucumber',
            '--session',
            self.session_name,
            '--build',
            self.build_name,
            "--json",
            *reports)
        self.assert_success(result)
        self.assert_record_tests_payload('record_test_json_result.json')

    def test_create_file_candidate_list(self):
        self.assertCountEqual(_create_file_candidate_list("a-b"), ["a/b", "a-b"])
        self.assertCountEqual(_create_file_candidate_list("a-b-c"), ["a/b/c", "a-b/c", "a/b-c", "a-b-c"])
        self.assertCountEqual(_create_file_candidate_list("a_b_c"), ["a_b_c"])

    def test_clean_uri(self):
        self.assertEqual(clean_uri('foo/bar/baz.feature'), 'foo/bar/baz.feature')
        self.assertEqual(clean_uri('file:foo/bar/baz.feature'), 'foo/bar/baz.feature')
        self.assertEqual(clean_uri('classpath:foo/bar/baz.feature'), 'foo/bar/baz.feature')
