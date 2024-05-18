import pytest
import shutil
import time

from types import SimpleNamespace

from bincrafters_conan_remote.remote import run_remote_in_thread
from bincrafters_conan_remote.test.helpers import cli_command, env_vars


@pytest.fixture(scope="session", autouse=True)
def setup_module():
    run_remote_in_thread(SimpleNamespace(port=8042))
    print("Sleeping for 10 seconds...")
    time.sleep(10)
    print("Done sleeping")
    shutil.rmtree(env_vars["CONAN_HOME"], ignore_errors=True)
    cli_command(["conan", "user"]) # TODO: Switch ConanV1 / ConanV2
    cli_command(["conan", "config", "set", "general.revisions_enabled=1"]) # TODO: Switch ConanV1 / ConanV2
    cli_command(["conan", "remote", "remove", "conancenter"])
    cli_command(["conan", "remote", "add", "inexorgame", "http://127.0.0.1:8042/r/github+bincrafters_remote+testing_v-998+inexorgame/", "False"])
    cli_command(["conan", "remote", "list"], expected_outputs=["inexorgame",])
