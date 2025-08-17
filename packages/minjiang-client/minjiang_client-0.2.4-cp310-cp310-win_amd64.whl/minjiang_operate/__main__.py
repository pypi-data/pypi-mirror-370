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

import sys
import json
from pathlib import Path
import os
import hashlib
import secrets
import datetime
import string

sys.path.append(str(Path(os.path.dirname(__file__)).parent))

from minjiang_operate.operate_manager import OperateManager

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in ["--add-user", "-au"]:
        if len(sys.argv) == 4:
            user_name = sys.argv[2]
            auth_code = sys.argv[3]
        elif len(sys.argv) == 3:
            user_name = sys.argv[2]
            auth_code = ""
        else:
            raise RuntimeError("Insufficient parameters, format：`--add-user user_name auth_code` or --add-user user_name")

        random_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        token = hashlib.md5(f"{datetime.datetime.now()}{random_code}".encode()).hexdigest()

        result = OperateManager.add_user(user_name, token, auth_code)
        print(f"user_id: {result['user_id']}\nuser_name: {user_name}\ntoken: {token}")

    elif len(sys.argv) >= 2 and sys.argv[1] in ["--set-oss-auth", "-soa"]:
        if_global = input("If setting global OSS config? [Y/n]: ")
        if if_global not in ["N", "n"]:
            user_id = 0
            if_global = True
        else:
            user_id = int(input("User ID: "))
            if_global = False

        oss_server = input("OSS Server: ")
        oss_bucket = input("OSS Bucket: ")
        oss_ak = input("OSS AK: ")
        oss_sk = input("OSS SK: ")
        config = dict()
        config['host'] = oss_server.strip()
        config['bucket'] = oss_bucket.strip()
        config['access_key'] = oss_ak.strip()
        config['secret_key'] = oss_sk.strip()
        result = OperateManager.set_oss_auth(if_global, user_id, auth_text=json.dumps(config))

    else:
        print("Unknown option.")
        print("  - Use `python -m minjiang_operate -au user_name auth_code for add user.")
        print("  - Use `python -m minjiang_operate -soa user_id [true/false] for setting OSS auth.")
