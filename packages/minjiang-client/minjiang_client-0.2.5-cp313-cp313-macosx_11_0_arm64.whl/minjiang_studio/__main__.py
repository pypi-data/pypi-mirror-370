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

from minjiang_client.com.user import check_user_status, login
from minjiang_client.utils.local import get_user_token, get_gui_addr, set_gui_addr
from minjiang_client.utils.local import get_default_language
import platform
import uvicorn
import threading
import sys
import time


def run_uvicorn(host, port):
    """运行uvicorn服务器的函数"""
    try:
        uvicorn.run(
            "minjiang_studio.app:app",
            host=host,
            port=int(port),
            log_level="warning",
            timeout_keep_alive=60
        )
    except Exception as e:
        print(f"Uvicorn server error: {e}")
        sys.exit(1)


def run_system_tray(web_gui_url):
    """运行系统托盘应用的函数"""
    try:
        from minjiang_studio.utils.status_bar import SystemTrayApp
        app = SystemTrayApp(web_gui_url=web_gui_url)
        if app.os_type != "Darwin":
            app.root.mainloop()
    except Exception as e:
        print(f"System tray error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # 初始化GUI地址
        gui_addr = get_gui_addr()
        if gui_addr is None:
            set_gui_addr("127.0.0.1", 6886)
            gui_addr = get_gui_addr()

        host = gui_addr["server_addr"]
        port = gui_addr["port"]
        login_page = ""

        # 登录逻辑
        if get_user_token() is not None:
            try:
                user_status = check_user_status()
                if user_status is None:
                    if get_default_language() == "en":
                        print("Login ...")
                    else:
                        print("正在尝试登录 ...")
                    user_name = login(get_user_token())
                else:
                    user_name = user_status['user_name']
                if get_default_language() == "en":
                    print(f"Login successfully as user {user_name}.")
                else:
                    print(f"用户 {user_name} 登录成功。")
            except Exception as e:
                login_page = "/login"
                if get_default_language() == "en":
                    print(f"Login failed: {e}")
                else:
                    print(f"登录失败: {e}")
        else:
            login_page = "/login"

        # Print running information
        web_gui_url = f"http://{host}:{port}{login_page}"
        if get_default_language() == "en":
            print(f'Minjiang Studio is running, please visit via {web_gui_url}.')
        else:
            print(f'岷江测控软件Studio正在运行, 请通过 {web_gui_url} 链接进行访问。')

        # Start uvicorn in a separate thread
        uvicorn_thread = threading.Thread(
            target=run_uvicorn,
            args=(host, port),
            daemon=True
        )
        uvicorn_thread.start()

        # Run system tray on main thread for macOS
        if platform.system() == "Darwin":
            run_system_tray(web_gui_url)
        else:
            # For Windows/Linux, we can still use a separate thread
            tray_thread = threading.Thread(
                target=run_system_tray,
                daemon=True,
                args=(web_gui_url,)
            )
            tray_thread.start()

        # Keep the main thread alive (for macOS)
        try:
            while uvicorn_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)
    except Exception as e:
        msg = repr(e)
        print(msg)
        sys.exit(1)
