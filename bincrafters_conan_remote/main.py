import argparse
from bincrafters_conan_remote.generate import run_generate
from bincrafters_conan_remote.remote import run_remote


def run():
    parser = argparse.ArgumentParser(description="Experimental. Don't use.")
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Run a local Conan remote that fetches external files.")
    run_parser.add_argument("--port", type=int, default=8042, help="Port to run the local server on.")

    generate_parser = subparsers.add_parser("generate", help="Generate a static Conan remote from an existing Conan remote.")
    generate_parser.add_argument("--port", type=int, default=8043, help="Port to run the local server on.")
    generate_parser.add_argument("--remote-url", type=str, default="https://bincrafters.jfrog.io/artifactory/api/conan/conan-legacy-inexorgame/", help="Remote URL to generate the static remote from. It can not contain spaces or plus signs (+) and has to end on a slash.")
    generate_parser.add_argument("--remote-name", type=str, default="inexorgame", help="Remote URL to generate the static remote from.")

    args = parser.parse_args()

    if args.command == "run":
        run_remote(args)
    elif args.command == "generate":
        run_generate(args)
