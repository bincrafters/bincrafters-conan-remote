from bincrafters_conan_remote.test.helpers import cli_command

import pytest
import time

def test_download_revision_latest():
    print("Sleeping for 25 seconds...")
    time.sleep(25)
    cli_command(
        ["conan", "download", "-r", "inexorgame", "--recipe", "InexorGlueGen/0.6.11@inexorgame/stable"],
        expected_outputs=[
            "Downloading conanmanifest.txt",
            "Downloading conanfile.py",
            "Downloading conan_sources.tgz"]
        )
