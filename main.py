"""
程序入口模块
启动登录窗口，登录成功后打开主界面
"""

from app.login_window import LoginWindow
from app.main_window import MainWindow


def main() -> None:
    """程序主入口"""
    # 使用列表存储登录信息，供回调写入后在外部读取
    login_info: list[tuple[str, str, bytes]] = []

    def on_login_success(username: str, password: str, crypto_salt: bytes) -> None:
        login_info.append((username, password, crypto_salt))

    # 显示登录窗口
    login_win = LoginWindow(on_login_success=on_login_success)
    login_win.run()

    # 登录成功后打开主界面
    if login_info:
        username, password, crypto_salt = login_info[0]
        main_win = MainWindow(username=username, password=password, crypto_salt=crypto_salt)
        main_win.run()


if __name__ == "__main__":
    main()
