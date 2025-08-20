import json

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from halerium_utilities.board import Board
from halerium_utilities.file.card_ids import assign_new_card_ids_to_board
from halerium_utilities.hal_es import BoardPathSession, HalE
from halerium_utilities.logging.exceptions import TestEvaluationError, TestExecutionError
from halerium_utilities.prompt.models import call_model_async

from .schemas import TestCase


def _trim_dict(full_dict: Dict[str, Any], minimal_dict: Dict[str, Any],
               recursion_break_keys=["attachments"]) -> Dict[str, Any]:
    """
    Recursively trim the full_dict to only contain keys present in minimal_dict.
    """
    trimmed_dict = {}
    for key, value in minimal_dict.items():
        if key in full_dict:
            if key in recursion_break_keys:
                trimmed_dict[key] = full_dict[key]
            elif isinstance(value, dict) and isinstance(full_dict[key], dict):
                trimmed_dict[key] = _trim_dict(full_dict[key], value)
            else:
                trimmed_dict[key] = full_dict[key]
    return trimmed_dict


def _truncate_strings(data, max_length):
    if isinstance(data, dict):
        return {key: _truncate_strings(value, max_length) for key, value in data.items()}
    elif isinstance(data, list):
        return [_truncate_strings(item, max_length) for item in data]
    elif isinstance(data, str):
        return data[:max_length]
    else:
        return data


def instantiate_test(test_case, test_dir="."):
    """
    Validate and instantiate a test case, preparing it for execution.

    Parameters
    ----------
    test_case : dict
        The test case specification as a dictionary.
    test_dir : str, optional
        Directory where test artifacts will be stored (default is current directory).

    Returns
    -------
    session : BoardPathSession
        The session object for the instantiated test.
    test_case : TestCase
        The validated and prepared test case object.

    Raises
    ------
    ValidationError
        If the test case does not conform to the expected schema.
    """
    test_case = TestCase.validate(test_case)

    name = test_case.hale_name

    template_path = test_case.board_path
    if not template_path:
        template_path = HalE.from_name(test_case.hale_name).template_board
        template_path = Path("/home/jovyan/") / template_path.lstrip("/")
    template_path = Path(template_path)
    template_board = Board.from_json(template_path)

    if not name:
        name = template_path.stem

    test_name = test_case.test_name

    # create test_folder
    test_folder = Path(test_dir) / name / test_name / datetime.now().isoformat()
    test_folder.mkdir(parents=True)

    # write instance file
    new_board = assign_new_card_ids_to_board(template_board, {}, inplace=True)
    board_path = test_folder / template_path.name
    new_board.to_json(board_path)

    session = BoardPathSession(board_path)
    if test_case.user_info:
        session.user_info = test_case.user_info.dict()

    return session, test_case


compatible_actions = {
    "note": {"insert_text"},
    "bot": {"insert_text", "send_prompt", "append_bot_element"},
    "upload": {"upload_file"},
    "action-chain": {"execute_actions"},
}


def execute_test(session, test_case):
    """
    Execute the actions defined in a test case using the provided session.

    Parameters
    ----------
    session : BoardPathSession
        The session object in which to execute the test.
    test_case : TestCase
        The test case containing the actions to execute.

    Returns
    -------
    BoardPathSession
        The session object

    Raises
    ------
    TestExecutionError
        If there is an error during the execution of the test actions.
    """
    for i, step in enumerate(test_case.test_steps):
        try:
            element = session.get_elements()[step.index]
            if step.action_type not in compatible_actions.get(element.type, set()):
                raise TypeError(
                    f"Action {step.action_type} cannot be applied to element {step.index} of type {element.type}.")

            if step.action_type == "insert_text":
                session.insert_text(element.id, text=step.action.text, field=step.action.field)
            elif step.action_type == "send_prompt":
                session.send_prompt(element.id)
            elif step.action_type == "append_bot_element":
                session.append_bot_element(element.id)
            elif step.action_type == "upload_file":
                session.upload_file(element.id, file_path=step.action.file_path)
            elif step.action_type == "execute_actions":
                session.execute_actions(element.id)
            else:
                raise ValueError(f"Unknown action_type: {step.action_type}.")

        except Exception as exc:
            raise TestExecutionError(f"Test step {i} {str(step)} failed with {type(exc)}: {exc}.")

    return session


async def evaluate_test(session, test_case):
    """
    Evaluate the results of a test case within a given session.

    Parameters
    ----------
    session : BoardPathSession
        The session object containing the elements to be evaluated.
    test_case : TestCase
        The test case containing evaluation specifications.

    Returns
    -------
    results : list of dict
        A list of dictionaries, each indicating the success or failure of an evaluation.
        Each dictionary contains:
            - 'success': bool, True if the evaluation passed, False otherwise.
            - 'reason': str, optional, the reason for failure if the evaluation did not pass.

    Notes
    -----
    - Each evaluation in the test case is processed in sequence.
    - Evaluations may use programmatic comparison or LLM-based prompts, depending on the test case specification.
    """
    results = []

    for evaluation in test_case.evaluations:
        try:
            await _single_evaluation(session, evaluation)
            results.append({"success": True})
        except Exception as exc:
            results.append({"success": False, "reason": str(exc)})

    return results


async def _single_evaluation(session, evaluation):
    board_path = session.session_info["sessionContent"]["path"]
    eval_llm_log_path = Path.home() / board_path.lstrip('/')
    eval_llm_log_path = eval_llm_log_path.parent / "llm_eval_logs"
    eval_llm_log_path.mkdir(exist_ok=True)

    element = session.get_elements()[evaluation.index]

    if evaluation.expected_value:
        expected = evaluation.expected_value.dict(exclude_none=True)
        observed = _trim_dict(element.dict(), expected)
    else:
        expected = None
        observed = element.dict()

    if evaluation.eval_prompt:
        n_retries = 3
        for i in range(n_retries):
            try:
                result, messages = await _call_eval_llm(
                    eval_prompt=evaluation.eval_prompt,
                    expected_dict=expected,
                    observed_dict=observed)
                with open(eval_llm_log_path / f"{str(datetime.now())}.json", "w") as f:
                    json.dump(messages, f)
                break
            except Exception as exc:
                if i == (n_retries - 1):
                    raise exc

        if not result.get("success"):
            # truncate strings to avoid overflow due to attachments
            expected = _truncate_strings(expected, 500)
            observed = _truncate_strings(observed, 500)
            raise TestEvaluationError(
                f"LLM-based evaluation failed.\nExpected:\n{expected}\nObserved:\n"
                f"{observed}\nReason: {result.get('reason')}")

    else:

        if expected != observed:
            # truncate strings to avoid overflow due to attachments
            expected = _truncate_strings(expected, 500)
            observed = _truncate_strings(observed, 500)
            raise TestEvaluationError(f"Data-based evaluation failed.\nExpected:\n{expected}\nObserved:\n{observed}")


async def _call_eval_llm(eval_prompt, expected_dict, observed_dict):
    system_prompt = (
        "You are a test evaluator that will be given a expected JSON and an observed JSON as well as an evaluation prompt.\n"
        "Your job is to compare the expected and observed JSON under the instructions of the evaluation prompt.\n"
        "If no expected JSON is provided you are to judge the test solely by the observed JSON and the evaluation prompt.\n"
        "In the end you will answer again with JSON that is structured as\n"
        "```JSON\n"
        '{"success": bool,  # use true for a passed test\n'
        ' "reason": ... }  # null for a passed test and a string for a failed test\n'
        "```"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": eval_prompt},
    ]
    if expected_dict:
        messages.append({"role": "user", "content": f"Expected:\n```{json.dumps(expected_dict)}```"})

    messages.append({"role": "user", "content": f"Observed:\n```{json.dumps(observed_dict)}```"})

    generator = call_model_async("chat-gpt-41", body={
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "max_completion_tokens": 1000,
    }, parse_data=True)

    answer = ""
    async for event in generator:
        if event.event == "chunk":
            answer += event.data.get("chunk", "")

    result = json.loads(answer)

    messages.append({"role": "assistant", "content": result})
    return result, messages
