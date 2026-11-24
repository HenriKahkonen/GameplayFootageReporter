"""Module that contains the argparser for the main script"""

import argparse

def parse_args(argv: list):
    """
    Takes the arguments supplied when running the python program and returns a Namespace of the parsed, known arguments

    Params:
        argv: Raw arguments

    Returns:
        Namespace of parsed arguments
    """

    parser = argparse.ArgumentParser(description="Gameplay footage report generator")

    parser.add_argument(
        "--initialize-obsidian",
        action="store_true",
        help="Initialize the Obsidian database to supplement the video footage folder"
        )
    parser.add_argument(
        "--footage-path",
        type=str,
        metavar="Footage_path",
        help="The path where the footage is stored"
        )
    parser.add_argument(
        "--obsidian-path",
        type=str,
        metavar="Obsidian_path",
        help="The path where the complementary obsidian database folder is located"
        )
    parser.add_argument(
        "--output-to",
        type=str,
        metavar="Output_path",
        help="The custom path to output the analysis report to"
        )
    parser.add_argument(
        "--calculate-test-file-hash-baseline",
        action="store_true",
        help="Create a JSON file of all of the test files' sha256 hashes so "
        "that their integrity can be verified."
        )
    #parser.add_argument(
    # "--create-env-files",
    # action="store_true",
    # help="Add the template .env files."
    #)
    parser.add_argument(
        "--unpack-tests",
        action="store_true",
        help="Unpack the test files for the program."
        )
    parser.add_argument(
        "--remove-test-files",
        action="store_true",
        help="Free disk space by removing the test files."
    )

    return parser.parse_args(argv[1:])