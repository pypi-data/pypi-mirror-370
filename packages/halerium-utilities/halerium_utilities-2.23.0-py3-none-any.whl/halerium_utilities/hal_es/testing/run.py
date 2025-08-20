import json
import logging
import os
import textwrap

from pathlib import Path
from urllib.parse import urljoin, quote

from .evaluation import execute_test, instantiate_test, evaluate_test


async def run_tests(spec_dir="specs", run_dir="runs", n_repeat=1, show_progress=True):
    """
    Run all test cases found in a directory, execute them, and report results.

    Parameters
    ----------
    spec_dir : str, optional
        Directory containing test specification files (default is "specs").
        Can also be the path of a single test*.json file.
    run_dir : str, optional
        Directory where test run data will be stored (default is "runs").
    n_repeat : int, optional
        Number of times to repeat each test (default is 1).
    show_progress: bool, optional
        Whether to print out test progress.
        The default is True.

    Returns
    -------
    total_report : dict
        A summary report containing:
            - 'tests_run': int, total number of tests executed
            - 'tests_passed': int, number of tests passed
            - 'tests_failed': int, number of tests failed
            - 'test_reports': list of dict, individual test reports

    Notes
    -----
    - Test specification files are expected to be JSON files with names matching 'test*.json'.
    - An example specification file can be generated with the `create_example_test` function.
    - Each test is instantiated, executed, and evaluated.
    - A sharing link to the session is generated for each test.
    """
    def print_progress(s):
        if show_progress:
            print(s)

    # Collect all test_*.json files recursively
    spec_path = Path(spec_dir)
    if spec_path.is_dir():
        test_files = list(spec_path.glob("**/test*.json"))
    elif spec_path.is_file() and spec_path.match("test*.json"):
        test_files = [spec_path]
    else:
        test_files = []

    total_report = {
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "test_reports": []
    }

    for test_file in test_files:
        try:
            with open(test_file, "r") as f:
                test_case = json.load(f)
        except json.JSONDecodeError as exc:
            logging.warning(f"Skipping {test_file} as it could not be decoded: {exc}")
            continue

        for repetition in range(n_repeat):

            session, test_case = instantiate_test(test_case, test_dir=run_dir)

            test_name = test_case.test_name
            # get session workspace path
            session_path = session.session_info["sessionContent"]["path"]
            # create sharing link to session
            sharing_link = _create_session_share_link(session_path)

            print_progress(
                f"Performing test {test_name}\n{sharing_link}")

            execute_test(session=session, test_case=test_case)
            results = await evaluate_test(session=session, test_case=test_case)

            passed = all([r.get("success", False) for r in results])

            total_report["tests_run"] += 1
            if passed:
                total_report["tests_passed"] += 1
            else:
                total_report["tests_failed"] += 1

            # Prepare report
            report = {
                "test_name": test_name,
                "board_link": sharing_link,
                "result": results,
                "passed": passed,
            }
            total_report["test_reports"].append(report)

            session_runner_path = Path("/home/jovyan/") / session_path.lstrip("/")
            report_path = session_runner_path.parent / "report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            print_progress(f"Test {test_name} (repetition {repetition}) complete.")
            if not passed:
                shortened_report = {
                    "board_link": report["board_link"],
                    "failures": [
                        {"failed_evaluation": i, "reason": r.get("reason").split("\n")}
                        for i, r in enumerate(report["result"])
                        if not r["success"]
                    ]}
                print_progress(f"Test {test_name} (repetition {repetition} failed.\n"
                               f"{json.dumps(shortened_report, indent=2)}")

    return total_report


def _create_session_share_link(session_path):

    base_url = os.getenv("HALERIUM_BASE_URL")
    workspace = os.getenv("HALERIUM_PROJECT_ID")
    tenant = os.getenv("HALERIUM_TENANT_KEY")

    sharing_link = urljoin(
        base_url,
        f"{tenant}"
        f"/{workspace}"
        f"/contents/" + quote(session_path.lstrip("/"))
    )

    return sharing_link


def create_example_test(filepath="test_example.json"):
    """
    Create and example test specification JSON file.

    Parameters
    ----------
    filepath : str or Path
        Where to store the example file

    Returns
    -------

    """

    example = """
    {
        // This is an example test specification for illustration purposes.
        //
        // Note that you will have to remove all of the comments starting with // to make this a valid JSON
        "board_path": "your_board_name.board",
        "hale_name": "My Hal-E", // will only be used if no board path is provided)
        "test_name": "generic test case",
        "user_info": {  // use this to simulate a user in the test
            "username": "john.doe@domain.com",
            "name": "John Doe"
        },
        "test_steps": [
            {
                "index": 1,
                "action_type": "insert_text", // can be used if element of index 1 is of type 'bot' or 'note'
                "action": {
                    "text": "Hello, what is your name?",
                    "field": "prompt_input"
                    // 'prompt_input' or 'prompt_output' for 'bot' elements. 'title' or 'message' for 'note' elements.
                }
            },
            {
                "index": 1,
                "action_type": "send_prompt" // can be used if index 1 is of type 'bot'.
            },
            {
                "index": 1,
                "action_type": "append_bot_element"
                 // can be used if index 1 is of type 'bot'.
                 // note that this inserts a 'bot' type element at index 2
            },
            {
                "index": 2,
                "action_type": "send_prompt"
            },
            {
                "index": 0,
                "action_type": "upload_file", // can be used if index 0 is of type 'upload'.
                "action": {
                    "file_path": "example.pdf" // the file to be put into the session (simulated upload)
                }
            },
            {
                "index": 3,
                "action_type": "execute_actions" // can be used if index 3 is of type 'action-chain'.
            }
        ],
        "evaluations": [
            {
                "index": 0,
                // specifying only 'expected_value' will make a direct (==) comparison of the expected values
                "expected_value": {
                    "type": "note", // Note that this would fail as element 0 is of type upload
                    "type_specific": {
                        "title": "",
                        "message": "Hello! My name is __bot_name__."
                    }
                }
            },
            {
                "index": 1,
                // specifying only 'eval_prompt' will let chatGPT evaluate the element
                "eval_prompt": "Confirm that the bot introduces itself."
            },
            {
                "index": 4,
                // specifying both 'expected_value' and 'eval_prompt' will let chatGPT evaluate the element
                // with the expected value in the context.
                "expected_value": {
                    "type": "note",
                    "type_specific": {
                        "title": "",
                        "message": "The file has been processed."
                    }
                },
                "eval_prompt": "Confirm that the message reads 'The file has been processed'."
            }
        ]
    }
    """
    example = textwrap.dedent(example)

    with open(filepath, "w") as f:
        f.write(example)
