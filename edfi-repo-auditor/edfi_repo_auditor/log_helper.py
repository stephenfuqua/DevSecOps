# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from requests import Response


def http_error(process: str, response: Response) -> RuntimeError:
    log = {
        "process": process,
        "error_message": response.text,
        "status_code": response.status_code,
    }
    return RuntimeError(log)
