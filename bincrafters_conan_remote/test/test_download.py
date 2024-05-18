from bincrafters_conan_remote.test.helpers import cli_command

import pytest


def test_download_revision_latest():
    cli_command(
        ["conan", "download", "-r", "inexorgame", "--recipe", "InexorGlueGen/0.6.11@inexorgame/stable"],
        expected_outputs=[
            "Downloading conanmanifest.txt",
            "Downloading conanfile.py",
            "Downloading conan_sources.tgz"]
        )

def test_download_revision_specific():
    cli_command(
        ["conan", "download", "-r", "inexorgame", "--recipe", "grpc/1.34.1@inexorgame/stable#0"],
        expected_outputs=[
            "Downloading conanmanifest.txt",
            "Downloading conanfile.py",
            "Downloading conan_export.tgz",
            "Downloading conan_sources.tgz"]
        )


def test_download_no_explicit_remote():
    cli_command(
        ["conan", "download", "--recipe", "v8/7.6.66@inexorgame/testing"],
        expected_outputs=[
            "Downloading conanmanifest.txt",
            "Downloading conanfile.py"]
        )
