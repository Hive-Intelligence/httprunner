import unittest

from httprunner.make import (
    main_make,
    convert_testcase_path,
    make_files_cache_set,
    make_config_chain_style,
    make_teststep_chain_style,
    pytest_files_set,
)


class TestMake(unittest.TestCase):
    def test_make_testcase(self):
        path = ["examples/postman_echo/request_methods/request_with_variables.yml"]
        testcase_python_list = main_make(path)
        self.assertEqual(
            testcase_python_list[0],
            "examples/postman_echo/request_methods/request_with_variables_test.py",
        )

    def test_make_testcase_with_ref(self):
        path = [
            "examples/postman_echo/request_methods/request_with_testcase_reference.yml"
        ]
        make_files_cache_set.clear()
        pytest_files_set.clear()
        testcase_python_list = main_make(path)
        self.assertEqual(len(testcase_python_list), 1)
        self.assertIn(
            "examples/postman_echo/request_methods/request_with_testcase_reference_test.py",
            testcase_python_list,
        )

        with open(
            "examples/postman_echo/request_methods/request_with_testcase_reference_test.py"
        ) as f:
            content = f.read()
            self.assertIn(
                """
from examples.postman_echo.request_methods.request_with_functions_test import (
    TestCaseRequestWithFunctions as RequestWithFunctions,
)
""",
                content,
            )
            self.assertIn(
                ".call(RequestWithFunctions)", content,
            )

    def test_make_testcase_folder(self):
        path = ["examples/postman_echo/request_methods/"]
        testcase_python_list = main_make(path)
        self.assertIn(
            "examples/postman_echo/request_methods/request_with_functions_test.py",
            testcase_python_list,
        )

    def test_convert_testcase_path(self):
        self.assertEqual(
            convert_testcase_path("mubu.login.yml")[0], "mubu_login_test.py"
        )
        self.assertEqual(
            convert_testcase_path("/path/to/mubu.login.yml")[0],
            "/path/to/mubu_login_test.py",
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/mubu.login.yml")[0],
            "/path/to 2/mubu_login_test.py",
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/mubu.login.yml")[1], "MubuLogin"
        )
        self.assertEqual(
            convert_testcase_path("mubu login.yml")[0], "mubu_login_test.py"
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/mubu login.yml")[1], "MubuLogin"
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/mubu-login.yml")[0],
            "/path/to 2/mubu_login_test.py",
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/mubu-login.yml")[1], "MubuLogin"
        )
        self.assertEqual(
            convert_testcase_path("/path/to 2/幕布login.yml")[0],
            "/path/to 2/幕布login_test.py",
        )
        self.assertEqual(convert_testcase_path("/path/to/幕布login.yml")[1], "幕布Login")

    def test_make_testsuite(self):
        path = ["examples/postman_echo/request_methods/demo_testsuite.yml"]
        make_files_cache_set.clear()
        pytest_files_set.clear()
        testcase_python_list = main_make(path)
        self.assertEqual(len(testcase_python_list), 2)
        self.assertIn(
            "examples/postman_echo/request_methods/demo_testsuite_yml/request_with_functions_test.py",
            testcase_python_list,
        )
        self.assertIn(
            "examples/postman_echo/request_methods/demo_testsuite_yml/request_with_testcase_reference_test.py",
            testcase_python_list,
        )

    def test_make_config_chain_style(self):
        config = {
            "name": "request methods testcase: validate with functions",
            "variables": {"foo1": "bar1", "foo2": 22},
            "base_url": "https://postman-echo.com",
            "verify": False,
            "path": "examples/postman_echo/request_methods/validate_with_functions_test.py",
        }
        self.assertEqual(
            make_config_chain_style(config),
            """Config("request methods testcase: validate with functions").variables(**{'foo1': 'bar1', 'foo2': 22}).base_url("https://postman-echo.com").verify(False)""",
        )

    def test_make_teststep_chain_style(self):
        step = {
            "name": "get with params",
            "variables": {"foo1": "bar1", "foo2": 123, "sum_v": "${sum_two(1, 2)}",},
            "request": {
                "method": "GET",
                "url": "/get",
                "params": {"foo1": "$foo1", "foo2": "$foo2", "sum_v": "$sum_v"},
                "headers": {"User-Agent": "HttpRunner/${get_httprunner_version()}"},
            },
            "testcase": "CLS_LB(TestCaseDemo)CLS_RB",
            "extract": {
                "session_foo1": "body.args.foo1",
                "session_foo2": "body.args.foo2",
            },
            "validate": [
                {"eq": ["status_code", 200]},
                {"eq": ["body.args.sum_v", "3"]},
            ],
        }
        teststep_chain_style = make_teststep_chain_style(step)
        self.assertEqual(
            teststep_chain_style,
            """Step(RunRequest("get with params").with_variables(**{'foo1': 'bar1', 'foo2': 123, 'sum_v': '${sum_two(1, 2)}'}).get("/get").with_params(**{'foo1': '$foo1', 'foo2': '$foo2', 'sum_v': '$sum_v'}).with_headers(**{'User-Agent': 'HttpRunner/${get_httprunner_version()}'}).extract().with_jmespath("body.args.foo1", "session_foo1").with_jmespath("body.args.foo2", "session_foo2").validate().assert_equal("status_code", 200).assert_equal("body.args.sum_v", "3"))""",
        )
