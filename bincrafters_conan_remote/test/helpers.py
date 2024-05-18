from typing import List

import os
import subprocess

_test_dir = os.path.dirname(os.path.abspath(__file__))
env_vars = {
    "CONAN_HOME": os.path.join(_test_dir, "__test_conan_home"), # ConanV2
    "CONAN_USER_HOME": os.path.join(_test_dir, "__test_conan_home"), # ConanV1
    "CONAN_USER_HOME_SHORT": os.path.join(_test_dir, "__test_c"), # ConanV1
    "CONAN_LOGGING_LEVEL": "10",
}

def _run_command(command:List[str]):
    env = os.environ.copy()
    env.update(env_vars)
    return subprocess.run(command, capture_output=True, text=True, env=env)

def cli_command(command:List[str], expected_returncode:int=0, expected_outputs:List[str]=[]):
    result = _run_command(command)

    print(f"{result.returncode} == {expected_returncode}: {result.stdout}")
    assert result.returncode == expected_returncode

    for expected_output in expected_outputs:
        assert expected_output in result.stdout
