"""
主界面模块
左右分栏布局：左侧文件列表（TreeView），右侧文本编辑器（Text）
提供新建、保存、删除按钮及 Ctrl+S 快捷键
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from app.crypto_manager import CryptoManager
from app.file_manager import FileManager


class MainWindow:
    """
    主应用窗口
    """

    def __init__(self, username: str, password: str, crypto_salt: bytes):
        """
        :param username: 登录用户名
        :param password: 明文密码（用于派生加密密钥）
        :param crypto_salt: 注册时随机生成并存储的加密密钥派生盐
        """
        self._username = username
        self._crypto = CryptoManager(password, crypto_salt)
        self._file_manager = FileManager(username, self._crypto)

        # 当前正在编辑的文件名（显示名）
        self._current_file: str | None = None
        # 标记内容是否已修改
        self._dirty = False

        self._root = tk.Tk()
        self._root.title(f"加密文件管理器 — {username}")
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._center_window(920, 620)
        self._refresh_file_list()

    # ────────────────────────────────────────────────────────────────────────
    # UI 构建
    # ────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """构建主界面"""
        self._build_toolbar()
        self._build_main_pane()
        self._build_status_bar()

    def _build_toolbar(self) -> None:
        """构建顶部工具栏"""
        toolbar = ttk.Frame(self._root, padding=(6, 4))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="📄 新建文件", command=self._new_file).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="💾 保存文件", command=self._save_file).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="🗑 删除文件", command=self._delete_file).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        self._user_label = ttk.Label(toolbar, text=f"👤 {self._username}")
        self._user_label.pack(side=tk.RIGHT, padx=4)

    def _build_main_pane(self) -> None:
        """构建左右分栏区域"""
        paned = ttk.PanedWindow(self._root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # ── 左侧文件列表面板 ──
        left_frame = ttk.LabelFrame(paned, text="文件列表", padding=4)
        paned.add(left_frame, weight=1)

        # TreeView 列：文件名 + 修改时间
        columns = ("modified",)
        self._tree = ttk.Treeview(
            left_frame, columns=columns, show="tree headings", selectmode="browse"
        )
        self._tree.heading("#0", text="文件名", anchor=tk.W)
        self._tree.heading("modified", text="修改时间", anchor=tk.W)
        self._tree.column("#0", width=150, minwidth=100)
        self._tree.column("modified", width=140, minwidth=120)

        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=tree_scroll.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 单击选中文件，加载内容到编辑器
        self._tree.bind("<<TreeviewSelect>>", self._on_file_select)

        # ── 右侧编辑器面板 ──
        right_frame = ttk.LabelFrame(paned, text="文件内容", padding=4)
        paned.add(right_frame, weight=3)

        self._text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            undo=True,
            relief=tk.FLAT,
            borderwidth=1,
        )
        text_scroll_y = ttk.Scrollbar(
            right_frame, orient=tk.VERTICAL, command=self._text.yview
        )
        text_scroll_x = ttk.Scrollbar(
            right_frame, orient=tk.HORIZONTAL, command=self._text.xview
        )
        self._text.configure(
            yscrollcommand=text_scroll_y.set, xscrollcommand=text_scroll_x.set
        )

        text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Ctrl+S 快捷键保存
        self._text.bind("<Control-s>", lambda _: self._save_file())
        # 监听文本变动，标记为已修改
        self._text.bind("<<Modified>>", self._on_text_modified)

        # 初始禁用编辑器（未选中文件时不可输入）
        self._set_editor_state(enabled=False)

    def _build_status_bar(self) -> None:
        """构建底部状态栏"""
        self._status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            self._root, textvariable=self._status_var, relief=tk.SUNKEN, anchor=tk.W, padding=4
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ────────────────────────────────────────────────────────────────────────
    # 辅助方法
    # ────────────────────────────────────────────────────────────────────────

    def _center_window(self, width: int, height: int) -> None:
        """将窗口居中"""
        self._root.update_idletasks()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self._root.geometry(f"{width}x{height}+{x}+{y}")

    def _set_status(self, msg: str) -> None:
        """设置状态栏消息"""
        self._status_var.set(msg)

    def _set_editor_state(self, enabled: bool) -> None:
        """切换编辑器的启用/禁用状态"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self._text.configure(state=state)

    def _load_content(self, content: str) -> None:
        """将文本内容加载到编辑器（不触发 dirty 标记）"""
        self._set_editor_state(enabled=True)
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", content)
        # 重置修改标记
        self._text.edit_modified(False)
        self._dirty = False

    def _get_editor_content(self) -> str:
        """获取编辑器当前全部文本"""
        return self._text.get("1.0", tk.END).rstrip("\n")

    def _refresh_file_list(self) -> None:
        """刷新左侧文件列表"""
        selected_name = self._current_file
        # 清空 TreeView
        for item in self._tree.get_children():
            self._tree.delete(item)
        # 重新插入文件
        for finfo in self._file_manager.list_files():
            iid = self._tree.insert(
                "", tk.END, text=finfo["name"], values=(finfo["modified"],)
            )
            # 如果是当前文件，恢复选中状态
            if finfo["name"] == selected_name:
                self._tree.selection_set(iid)
                self._tree.focus(iid)

    # ────────────────────────────────────────────────────────────────────────
    # 事件处理
    # ────────────────────────────────────────────────────────────────────────

    def _on_text_modified(self, _event=None) -> None:
        """文本内容变动时标记为 dirty"""
        if self._text.edit_modified():
            self._dirty = True

    def _on_file_select(self, _event=None) -> None:
        """文件列表选中事件：询问是否保存当前文件，然后加载新文件"""
        selection = self._tree.selection()
        if not selection:
            return

        new_name = self._tree.item(selection[0], "text")

        # 若当前文件已修改，询问是否保存
        if self._dirty and self._current_file:
            answer = messagebox.askyesno(
                "未保存更改",
                f"文件 '{self._current_file}' 有未保存的更改，是否保存？",
                parent=self._root,
            )
            if answer:
                self._save_file()

        # 加载新文件
        self._current_file = new_name
        content = self._file_manager.read_file(new_name)
        if content is None:
            messagebox.showerror("错误", f"无法读取文件 '{new_name}'", parent=self._root)
            return
        self._load_content(content)
        self._set_status(f"已打开：{new_name}")

    def _new_file(self) -> None:
        """新建文件"""
        filename = simpledialog.askstring(
            "新建文件", "请输入文件名：", parent=self._root
        )
        if not filename:
            return
        filename = filename.strip()
        if not filename:
            return

        if self._file_manager.file_exists(filename):
            messagebox.showwarning("提示", f"文件 '{filename}' 已存在", parent=self._root)
            return

        ok, msg = self._file_manager.save_file(filename, "")
        if ok:
            self._current_file = filename
            self._refresh_file_list()
            self._load_content("")
            self._set_status(f"已新建：{filename}")
        else:
            messagebox.showerror("错误", msg, parent=self._root)

    def _save_file(self) -> None:
        """保存当前文件"""
        if not self._current_file:
            messagebox.showinfo("提示", "请先选择或新建一个文件", parent=self._root)
            return

        content = self._get_editor_content()
        ok, msg = self._file_manager.save_file(self._current_file, content)
        if ok:
            self._text.edit_modified(False)
            self._dirty = False
            self._refresh_file_list()
            self._set_status(f"已保存：{self._current_file}")
        else:
            messagebox.showerror("保存失败", msg, parent=self._root)

    def _delete_file(self) -> None:
        """删除当前选中的文件"""
        if not self._current_file:
            messagebox.showinfo("提示", "请先选择一个文件", parent=self._root)
            return

        confirmed = messagebox.askyesno(
            "确认删除", f"确定要删除文件 '{self._current_file}' 吗？", parent=self._root
        )
        if not confirmed:
            return

        ok, msg = self._file_manager.delete_file(self._current_file)
        if ok:
            self._current_file = None
            self._dirty = False
            # 清空编辑器
            self._set_editor_state(enabled=True)
            self._text.delete("1.0", tk.END)
            self._text.edit_modified(False)
            self._set_editor_state(enabled=False)
            self._refresh_file_list()
            self._set_status("文件已删除")
        else:
            messagebox.showerror("错误", msg, parent=self._root)

    def _on_close(self) -> None:
        """窗口关闭时自动保存当前文件"""
        if self._dirty and self._current_file:
            content = self._get_editor_content()
            self._file_manager.save_file(self._current_file, content)
        self._root.destroy()

    # ────────────────────────────────────────────────────────────────────────
    # 运行入口
    # ────────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """启动主窗口事件循环"""
        self._root.mainloop()
