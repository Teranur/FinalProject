#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("c292f96e-db6f-4937-b0e8-069df21108cc")
    APP_PASSWORD = os.environ.get("8496f60a-b17b-46c8-97fe-04603bd8efa6")
