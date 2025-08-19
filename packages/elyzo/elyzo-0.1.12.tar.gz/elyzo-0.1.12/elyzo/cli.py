# File: elyzo/cli.py
# Description: The main entrypoint for the Elyzo CLI.

import argparse
from elyzo.auth import get_api_key, reset_api_key
from elyzo.deploy import deploy_agent
from elyzo.test_run import test_agent_run
from elyzo.run_agent import execute_agent_run
from elyzo.init import initialize_project

def main():
    """
    The main function that parses arguments and executes commands.
    """
    parser = argparse.ArgumentParser(
        prog="elyzo",
        description="The official command-line interface for Elyzo.",
        epilog="Run 'elyzo <command> --help' for more information on a specific command."
    )
    # Removed `required=True` to allow running the CLI without a command.
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- "init" command ---
    subparsers.add_parser("init", help="Create an elyzo.toml configuration file.")

    # --- "deploy" command ---
    deploy_parser = subparsers.add_parser("deploy", help="Deploy an agent.")
    deploy_parser.add_argument("--api-key", help="Your Elyzo API key.")

    # --- "reset-key" command ---
    subparsers.add_parser("reset-key", help="Reset and save your Elyzo API key.")

    # --- "test" command ---
    test_parser = subparsers.add_parser(
        "test",
        help="Perform a dry-run of your agent with specified inputs."
    )
    test_parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        metavar="KEY=VALUE",
        help="An input for the agent, as a key-value pair. Repeat for multiple inputs."
    )
    test_parser.add_argument(
        "--secret",
        action="append",
        dest="secrets",
        metavar="KEY=VALUE",
        help="A secret for the agent, as a key-value pair. Repeat for multiple secrets."
    )
    test_parser.add_argument(
        "--output",
        dest="output_path",
        metavar="PATH",
        help="Path to a directory where output files will be saved. Defaults to the current directory."
    )
    test_parser.add_argument("--api-key", help="Your Elyzo API key.")

    # --- "run" command ---
    run_parser = subparsers.add_parser(
        "run",
        help="Run a deployed agent with specified inputs."
    )
    run_parser.add_argument("agent_id", help="The ID or name of the agent to run.")
    run_parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        metavar="KEY=VALUE",
        help="An input for the agent. Repeat for multiple inputs."
    )
    run_parser.add_argument(
        "--secret",
        action="append",
        dest="secrets",
        metavar="KEY=VALUE",
        help="A secret for the agent. Repeat for multiple secrets."
    )
    run_parser.add_argument(
        "--output",
        dest="output_path",
        metavar="PATH",
        help="Path to a directory where output files will be saved."
    )
    run_parser.add_argument("--api-key", help="Your Elyzo API key.")

    args = parser.parse_args()

    # --- Command Handling ---
    # Handle 'elyzo' (no command)
    if args.command is None:
        parser.print_help()

    elif args.command == "init":
        initialize_project()

    elif args.command == "deploy":
        api_key = get_api_key(args.api_key)
        deploy_agent(api_key)

    elif args.command == "reset-key":
        reset_api_key()

    elif args.command == "test":
        api_key = get_api_key(args.api_key)
        input_args = args.inputs or []
        secret_args = args.secrets or []
        test_agent_run(api_key, input_args, secret_args, args.output_path)
        
    elif args.command == "run":
        api_key = get_api_key(args.api_key)
        input_args = args.inputs or []
        secret_args = args.secrets or []
        execute_agent_run(args.agent_id, api_key, input_args, secret_args, args.output_path)

if __name__ == "__main__":
    main()