#!/usr/bin/python3
# -*- coding: utf8 -*-
# Copyright (c) 2025 ZWDX, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from minjiang_client.com.user import add_user
from minjiang_client.com.oss import set_oss_auth

class OperateManager(object):
    @staticmethod
    def add_user(user_name: str, token: str, auth_code: str):
        return add_user(user_name, token, auth_code)

    @staticmethod
    def set_oss_auth(if_global: bool, user_id: int = None, auth_text: str = None, disabled: bool = False):
        return set_oss_auth(if_global, user_id, auth_text, disabled)