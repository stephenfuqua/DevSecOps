# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_repo_auditor.github_client import GitHubClient


def describe_when_initializing_a_GitHubClient() -> None:
    def describe_given_blank_access_token() -> None:
        def it_raises_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient("   ")
