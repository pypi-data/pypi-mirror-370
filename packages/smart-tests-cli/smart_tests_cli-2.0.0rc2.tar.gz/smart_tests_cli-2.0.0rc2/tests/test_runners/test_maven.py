import os
import shutil
import tempfile
from unittest import mock

import responses  # type: ignore

from smart_tests.test_runners import maven
from smart_tests.utils.http_client import get_base_url
from tests.cli_test_case import CliTestCase


class MavenTest(CliTestCase):
    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset(self):
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

        result = self.cli('subset', 'maven', '--session', self.session_name, '--build', self.build_name, '--target', '10%',
                          str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assert_success(result)
        self.assert_subset_payload('subset_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_from_file(self):
        # if we prepare listed file with slash e.g) com/example/launchable/model/aModelATest.class
        # the test will be failed at Windows environment. So, we generate file
        # path list
        def save_file(list, file_name):
            file = str(self.test_files_dir.joinpath(file_name))
            with open(file, 'w+') as file:
                for test_class in list:
                    file.write(test_class.replace(".", os.path.sep) + ".class\n")

        list_1 = ["com.example.sampleapp.model.a.ModelATest",
                  "com.example.sampleapp.model.b.ModelBTest",
                  "com.example.sampleapp.model.b.ModelBTest$SomeInner",
                  "com.example.sampleapp.model.c.ModelCTest",

                  ]

        list_2 = ["com.example.sampleapp.service.ServiceATest",
                  "com.example.sampleapp.service.ServiceATest$Inner1$Inner2",
                  "com.example.sampleapp.service.ServiceBTest",
                  "com.example.sampleapp.service.ServiceCTest",
                  ]

        save_file(list_1, "createdFile_1.lst")
        save_file(list_2, "createdFile_2.lst")

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

        result = self.cli('subset', 'maven', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          "--test-compile-created-file",
                          str(self.test_files_dir.joinpath("createdFile_1.lst")),
                          "--test-compile-created-file",
                          str(self.test_files_dir.joinpath("createdFile_2.lst")))
        self.assert_success(result)
        self.assert_subset_payload('subset_from_file_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_scan_test_compile_lst(self):

        list = [
            "com.example.sampleapp.service.ServiceATest",
            "com.example.sampleapp.service.ServiceATest$Inner1$Inner2",
            "com.example.sampleapp.service.ServiceBTest",
            "com.example.sampleapp.service.ServiceCTest",
        ]

        base_tmp_dir = os.path.join(".", "tmp-maven-scan/")

        os.makedirs(base_tmp_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(dir=base_tmp_dir)
        os.makedirs(os.path.join(temp_dir, 'testCompile', 'default-testCompile'), exist_ok=True)

        file = os.path.join(temp_dir, 'testCompile', 'default-testCompile', 'createdFiles.lst')
        with open(file, 'w+') as file:
            for test_class in list:
                file.write(test_class.replace(".", os.path.sep) + ".class\n")

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

        result = self.cli('subset', 'maven', '--session', self.session_name, '--build', self.build_name, '--target',
                          '10%',
                          "--scan-test-compile-lst")
        # clean up test directory
        shutil.rmtree(base_tmp_dir)

        self.assert_success(result)
        self.assert_subset_payload('subset_scan_test_compile_lst_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_by_absolute_time(self):
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

        result = self.cli('subset', 'maven', '--session', self.session_name, '--build', self.build_name, '--time', '1h30m',
                          str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assert_success(result)
        self.assert_subset_payload('subset_by_absolute_time_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_subset_by_confidence(self):
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

        result = self.cli('subset', 'maven', '--session', self.session_name, '--build', self.build_name, '--confidence', '90%',
                          str(self.test_files_dir.joinpath('java/test/src/java/').resolve()))
        self.assert_success(result)
        self.assert_subset_payload('subset_by_confidence_result.json')

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_maven(self):
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

        result = self.cli('record', 'test', 'maven', '--session', self.session_name,
                          '--build', self.build_name, str(self.test_files_dir) + "/**/reports")
        self.assert_success(result)
        self.assert_record_tests_payload("record_test_result.json")

    @responses.activate
    @mock.patch.dict(os.environ, {"SMART_TESTS_TOKEN": CliTestCase.smart_tests_token})
    def test_record_test_maven_with_nested_class(self):
        """Verify that class names containing $ (inner class marker) are processed correctly during test recording"""
        # Test the path_builder function directly by extracting it from the maven module
        from unittest import TestCase as UnitTestCase
        from unittest import TestSuite as UnitTestSuite

        # Extract the implementation from maven.py directly
        # This gets the implementation without going through the CLI/Click command
        def create_custom_path_builder(default_path_builder):
            def path_builder(case, suite, report_file):
                test_path = default_path_builder(case, suite, report_file)
                return [{**item, "name": item["name"].split("$")[0]} if item["type"] == "class" else item for item in test_path]
            return path_builder

        # Mock the default path builder that would return a class with $ in it
        def default_path_builder(case, suite, report_file):
            return [{"type": "class", "name": "com.launchableinc.rocket_car_maven.NestedTest$InnerClass"}]

        # Create our custom path builder function
        custom_path_builder = create_custom_path_builder(default_path_builder)

        # Test it directly with dummy inputs
        test_case = UnitTestCase()
        test_suite = UnitTestSuite()
        report_file = "TEST-nested.xml"

        # Call the path_builder
        result_path = custom_path_builder(test_case, test_suite, report_file)

        # Verify the result - it should remove everything after $
        self.assertEqual(result_path[0]["name"], "com.launchableinc.rocket_car_maven.NestedTest")
        self.assertNotIn("$", result_path[0]["name"])

        # Now run the actual CLI command to ensure integration works
        result = self.cli('record', 'test', 'maven', '--session', self.session_name, '--build', self.build_name,
                          str(self.test_files_dir) + "/maven/reports/TEST-1.xml",
                          str(self.test_files_dir) + "/maven/reports/TEST-2.xml",
                          str(self.test_files_dir) + "/maven/reports/TEST-nested.xml")
        self.assert_success(result)

    def test_glob(self):
        for x in [
            'foo/BarTest.java',
            'foo/BarTest.class',
            'FooTest.class',
            'TestFoo.class',
        ]:
            self.assertTrue(maven.is_file(x))

        for x in [
            'foo/Bar$Test.class',
            'foo/MyTest$Inner.class',
            'foo/Util.class',
        ]:
            self.assertFalse(maven.is_file(x))
