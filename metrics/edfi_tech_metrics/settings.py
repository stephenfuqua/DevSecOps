# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
import logging
from typing import List
from os import getenv
import sys

from dotenv import load_dotenv
from configargparse import ArgParser
from termcolor import colored


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_PAGE_SIZE = 100


@dataclass
class Configuration:
    """
    Container for holding arguments parsed from command line or environment.
    """

    jira_user_name: str
    jira_token: str
    jira_base_url: str
    log_level: str
    page_size: int

    def info(self, message: str) -> None:
        if self.log_level in ("INFO", "DEBUG"):
            print(colored(message, "blue"))

    def debug(self, message: str) -> None:
        if self.log_level in ("DEBUG"):
            print(colored(message, "yellow"))

    def error(self, message: str) -> None:
        print(colored(message, "red"))


def configure_logging(configuration: Configuration) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=configuration.log_level,
    )


def load_from_env() -> Configuration:
    load_dotenv()

    c = Configuration(
        getenv("JIRA_USER_NAME", ""),
        getenv("JIRA_TOKEN", ""),
        getenv("JIRA_BASE_URL", ""),
        getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
        int(getenv("PAGE_SIZE", DEFAULT_PAGE_SIZE)),
    )
    configure_logging(c)

    return c


def load_configuration(args_in: List[str]) -> Configuration:
    load_dotenv()

    parser = ArgParser()
    parser.add(  # type: ignore
        "-u",
        "--user-name",
        required=True,
        help="Jira user name",
        type=str,
        env_var="JIRA_USER_NAME",
    )

    parser.add(  # type: ignore
        "-t",
        "--token",
        required=True,
        help="Jira user token",
        type=str,
        env_var="JIRA_TOKEN",
    )

    parser.add(  # type: ignore
        "-b",
        "--base-url",
        required=True,
        help="Jira base URL",
        type=str,
        env_var="JIRA_BASE_URL",
    )

    parser.add(  # type: ignore
        "-l",
        "--log-level",
        required=False,
        help="Log level (default: info)",
        default=DEFAULT_LOG_LEVEL,
        type=str,
        env_var="AUDIT_LOG_LEVEL",
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
    )

    parser.add(  # type: ignore
        "-p",
        "--page-size",
        required=False,
        help="Jira API page size",
        default=DEFAULT_PAGE_SIZE,
        type=int,
        env_var="PAGE_SIZE",
    )

    parsed = parser.parse_args(args_in)

    c = Configuration(
        parsed.jira_user_name,
        parsed.token,
        parsed.base_url,
        parsed.log_level,
        parsed.page_size,
    )

    configure_logging(c)

    return c
