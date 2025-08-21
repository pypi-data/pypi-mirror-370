# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict


class AnyModel(BaseModel):
    model_config = ConfigDict(extra="allow")
