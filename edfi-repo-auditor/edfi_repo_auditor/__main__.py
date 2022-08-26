# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import sys
import logging

from dotenv import load_dotenv
from errorhandler import ErrorHandler

from edfi_repo_auditor.config import Configuration, load_configuration
from edfi_repo_auditor.auditor import run_audit


def _configure_logging(config: Configuration) -> None:
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=config.log_level,
    )


def _main():
    load_dotenv()
    config = load_configuration(sys.argv[1:])
    _configure_logging(config)

    error_tracker = ErrorHandler()

    try:
        run_audit(config)
    except Exception as e:
        logging.getLogger(__name__).error(e)

    if error_tracker.fired:
        print(
            "A fatal error occurred, please review the log output for more information.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    _main()
