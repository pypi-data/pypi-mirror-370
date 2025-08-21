import datetime
import importlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
import botocore

from . import report_generator
from .checklist import *  # noqa: F403
from .utils import common, language, level_const

# from .utils.language import get_translator


class SecurityBaselineTester:
    def __init__(self, profile, lang_code, output_dir):
        self.profile = profile
        self.language = lang_code
        self.output = output_dir
        self.session = self._create_session()
        self.config = self._load_config()
        ## Call module 'language' and pass the string 'lang_code'
        self.translator = language.get_translator("main", lang_code)

    def _create_session(self):
        if self.profile == "default":
            return boto3.Session()
        return boto3.Session(profile_name=self.profile)

    def _load_config(self):
        ## Get the absolute directory where *this script* is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.json")

        try:
            # with open("./config.json", "r") as file:
            with open(config_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("config.json file not found. Please ensure it exists in the same directory as this script.")
            raise
        except json.JSONDecodeError:
            logging.error("Error parsing config.json. Please ensure it is a valid JSON file.")
            raise

    def run(self):
        try:
            self._validate_session()
            caller_identity = self._get_caller_identity()
            self._print_auditor_info(caller_identity)

            logging.info(self.translator.translate("start_test"))

            account_id, results = self._execute_tests()
            self._generate_report(account_id, results)

            logging.info(self.translator.translate("test_completed"))
        except Exception as e:
            logging.error(
                f"An error occurred during the security baseline test: {str(e)}",
                exc_info=True,
            )

    def _validate_session(self):
        if self.session.region_name is None:
            raise ValueError('AWS region is not specified. Run "aws configure" to set it.')

    def _get_caller_identity(self):
        try:
            return self.session.client("sts").get_caller_identity()
        except botocore.exceptions.ClientError as e:
            logging.error(f"Failed to get caller identity: {str(e)}")
            raise

    def _print_auditor_info(self, caller_identity):
        logging.info("==================== AUDITOR INFO ====================")
        logging.info(f"USER ID : {caller_identity['UserId']}")
        logging.info(f"ACCOUNT : {caller_identity['Account']}")
        logging.info(f"ARN     : {caller_identity['Arn']}")
        logging.info("=====================================================")

    def _execute_tests(self):
        iam_client = self.session.client("iam")
        sts_client = self.session.client("sts")

        account_id = common.get_account_id(sts_client)
        logging.info(self.translator.translate("request_credential_report"))
        credential_report = common.generate_credential_report(iam_client)

        with ThreadPoolExecutor(max_workers=self.config.get("max_workers", 5)) as executor:
            futures = {
                executor.submit(self._run_check, check_name, credential_report): check_name
                for check_name in self.config.get("checks", [])
            }

            results = {
                level: [] for level in ["Success", "Warning", "Danger", "Error", "Info"] if isinstance(level, str)
            }
            for future in as_completed(futures):
                result = future.result()
                results[result.level].append(result)

        return account_id, results

    def _run_check(self, check_name, credential_report):
        # check_module = __import__(f"checklist.{check_name}", fromlist=[check_name])
        check_module = importlib.import_module(f"runbooks.security_baseline.checklist.{check_name}")
        check_method = getattr(check_module, self.config["checks"][check_name])
        translator = language.get_translator(check_name, self.language)

        if check_name in [
            "alternate_contacts",
            "account_level_bucket_public_access",
            "bucket_public_access",
            "cloudwatch_alarm_configuration",
            "direct_attached_policy",
            "guardduty_enabled",
            "multi_region_instance_usage",
            "multi_region_trail",
            "trail_enabled",
            "iam_password_policy",
        ]:
            return check_method(self.session, translator)
        elif check_name in [
            "root_mfa",
            "root_usage",
            "root_access_key",
            "iam_user_mfa",
        ]:
            return check_method(self.session, translator, credential_report)
        elif check_name == "trusted_advisor":
            return check_method(translator)
        else:
            raise ValueError(f"Unknown check method: {check_name}")

    def _check_result_directory(self):
        """
        Ensures that the 'results' directory (located next to this script) exists.

        :return: A Path object pointing to the results directory.
        """

        # directory_name = "./results"
        # if not os.path.exists(directory_name):
        #     os.makedirs(directory_name)
        #     logging.info(self.translator.translate("results_folder_created"))
        # else:
        #     logging.info(self.translator.translate("results_folder_already_exists"))

        ## ISSUE: creates results/ next to the module files in, e.g, .../site-packages/runbooks/security_baseline/results
        # script_dir = Path(__file__).resolve().parent
        # results_dir = script_dir / "results"
        ## Use the current working directory instead of the script directory
        if self.output:
            results_dir = Path(self.output).resolve()
        else:
            results_dir = Path.cwd() / "results"

        if not results_dir.exists():
            results_dir.mkdir(parents=True, exist_ok=True)
            logging.info(self.translator.translate("results_folder_created"))
        else:
            logging.info(self.translator.translate("results_folder_already_exists"))

        return results_dir

    def _generate_report(self, account_id, results):
        """
        Generates an HTML security report and writes it to the 'results' directory.

        :param account_id: The AWS account ID or similar identifier.
        :param results:    A dictionary containing the security baseline results.
        """
        html_report = report_generator.generate_html_report(account_id, results, self.language)

        current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        short_account_id = account_id[-4:]

        ## Ensure the results directory exists
        results_dir = self._check_result_directory()

        ## Build the report filename
        report_filename = f"security-report-{short_account_id}-{current_time}.html"
        report_path = results_dir / report_filename

        ## Get the absolute directory where *this script* is located
        # test_report_dir = os.path.dirname(os.path.abspath(__file__))
        # test_report_path = os.path.join(test_report_dir, report_filename)

        # with open(test_report_path, "w") as file:
        ## Write the report to disk
        with report_path.open("w", encoding="utf-8") as file:
            file.write(html_report)

        logging.info(self.translator.translate("generate_result_report"))
