"""
登录/注册窗口模块
提供用户名、密码输入框以及登录、注册两个按钮
"""

import tkinter as tk
from tkinter import messagebox, ttk

from app.user_manager import UserManager


class LoginWindow:
    """
    登录/注册窗口
    登录成功后调用回调函数，传入用户名和密码
    """

    def __init__(self, on_login_success):
        """
        :param on_login_success: 登录成功后的回调函数，签名为 fn(username: str, password: str, crypto_salt: bytes)
        """
        self._on_login_success = on_login_success
        self._user_manager = UserManager()

        self._root = tk.Tk()
        self._root.title("加密文件管理器 - 登录")
        self._root.resizable(False, False)

        self._build_ui()
        self._center_window(400, 280)

    def _build_ui(self) -> None:
        """构建登录界面 UI"""
        # 顶部标题
        title_label = tk.Label(
            self._root,
            text="🔒 加密文件管理器",
            font=("Microsoft YaHei", 18, "bold"),
            pady=20,
        )
        title_label.pack()

        # 表单框架
        form_frame = ttk.Frame(self._root, padding=10)
        form_frame.pack(fill=tk.X, padx=40)

        # 用户名行
        ttk.Label(form_frame, text="用户名：").grid(row=0, column=0, sticky=tk.W, pady=6)
        self._username_var = tk.StringVar()
        self._username_entry = ttk.Entry(form_frame, textvariable=self._username_var, width=24)
        self._username_entry.grid(row=0, column=1, sticky=tk.EW, pady=6)

        # 密码行
        ttk.Label(form_frame, text="密　码：").grid(row=1, column=0, sticky=tk.W, pady=6)
        self._password_var = tk.StringVar()
        self._password_entry = ttk.Entry(
            form_frame, textvariable=self._password_var, show="●", width=24
        )
        self._password_entry.grid(row=1, column=1, sticky=tk.EW, pady=6)

        form_frame.columnconfigure(1, weight=1)

        # 按钮行
        btn_frame = ttk.Frame(self._root, padding=(40, 10, 40, 10))
        btn_frame.pack(fill=tk.X)

        login_btn = ttk.Button(btn_frame, text="登 录", command=self._handle_login)
        login_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))

        register_btn = ttk.Button(btn_frame, text="注 册", command=self._handle_register)
        register_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0))

        # 绑定回车键登录
        self._root.bind("<Return>", lambda _: self._handle_login())
        # 聚焦用户名输入框
        self._username_entry.focus_set()

    def _center_window(self, width: int, height: int) -> None:
        """将窗口居中显示"""
        self._root.update_idletasks()
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self._root.geometry(f"{width}x{height}+{x}+{y}")

    def _get_inputs(self) -> tuple[str, str]:
        """获取输入框内容"""
        return self._username_var.get().strip(), self._password_var.get()

    def _handle_login(self) -> None:
        """处理登录按钮点击"""
        username, password = self._get_inputs()
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码", parent=self._root)
            return

        ok, msg = self._user_manager.login(username, password)
        if ok:
            # 获取注册时存储的加密密钥派生盐
            crypto_salt = self._user_manager.get_crypto_salt(username)
            self._root.destroy()
            self._on_login_success(username, password, crypto_salt)
        else:
            messagebox.showerror("登录失败", msg, parent=self._root)

    def _handle_register(self) -> None:
        """处理注册按钮点击，弹出注册对话框"""
        RegisterDialog(self._root, self._user_manager)

    def run(self) -> None:
        """运行登录窗口主循环"""
        self._root.mainloop()


class RegisterDialog:
    """
    注册对话框（模态窗口）
    """

    def __init__(self, parent: tk.Tk, user_manager: UserManager):
        self._user_manager = user_manager

        self._dialog = tk.Toplevel(parent)
        self._dialog.title("新用户注册")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()  # 模态：阻止操作父窗口

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self) -> None:
        """构建注册表单"""
        form = ttk.Frame(self._dialog, padding=20)
        form.pack(fill=tk.BOTH)

        labels = ["用户名：", "密　码：", "确认密码："]
        self._vars = [tk.StringVar() for _ in labels]

        for i, (lbl, var) in enumerate(zip(labels, self._vars)):
            ttk.Label(form, text=lbl).grid(row=i, column=0, sticky=tk.W, pady=6)
            show = "●" if i > 0 else ""
            entry = ttk.Entry(form, textvariable=var, show=show, width=22)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=6)
            if i == 0:
                entry.focus_set()

        form.columnconfigure(1, weight=1)

        # 提示文字
        ttk.Label(form, text="密码长度至少 6 位", foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky=tk.W
        )

        # 按钮
        btn_frame = ttk.Frame(self._dialog, padding=(20, 0, 20, 20))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确认注册", command=self._handle_register).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6)
        )
        ttk.Button(btn_frame, text="取　消", command=self._dialog.destroy).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0)
        )

        self._dialog.bind("<Return>", lambda _: self._handle_register())

    def _center_on_parent(self, parent: tk.Tk) -> None:
        """将对话框居中于父窗口"""
        self._dialog.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        dw = self._dialog.winfo_width()
        dh = self._dialog.winfo_height()
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        self._dialog.geometry(f"+{x}+{y}")

    def _handle_register(self) -> None:
        """处理注册逻辑"""
        username = self._vars[0].get().strip()
        password = self._vars[1].get()
        confirm = self._vars[2].get()

        if not username:
            messagebox.showwarning("提示", "用户名不能为空", parent=self._dialog)
            return
        if len(password) < 6:
            messagebox.showwarning("提示", "密码长度至少 6 位", parent=self._dialog)
            return
        if password != confirm:
            messagebox.showwarning("提示", "两次输入的密码不一致", parent=self._dialog)
            return

        ok, msg = self._user_manager.register(username, password)
        if ok:
            messagebox.showinfo("注册成功", f"用户 {username!r} 注册成功，请登录", parent=self._dialog)
            self._dialog.destroy()
        else:
            messagebox.showerror("注册失败", msg, parent=self._dialog)
