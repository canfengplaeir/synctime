import os
import webbrowser
import ntplib
import datetime
import tkinter as tk
from tkinter import messagebox
import threading
import requests
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import ctypes
import json
import subprocess  # 新增
import platform  # 新增
import logging
import tkinter.simpledialog as simpledialog


class SyncTimeApp:
    def __init__(self, root):
        self.root = root
        self.version = "1.4.0"  # 更新版本号以反映从API更新NTP服务器列表功能
        self.update_api = (
            "https://synctime-api.netlify.app/api/version"  # API地址
        )
        self.about_api = (
            "https://synctime-api.netlify.app/api/about"  # 关于页API地址
        )
        self.last_check_time = 0
        self.check_interval = 3600  # 1小时

        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()

        self.ntp_servers_filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "ntp_servers.json"
        )
        self.load_ntp_server_list()
        self.primary_ntp_server = (
            self.ntp_server_list[0] if self.ntp_server_list else None
        )

        self.setup_window()
        self.create_widgets()
        self.create_menu()
        self.load_icon()  # 确保加载图标

        logging.basicConfig(
            filename="synctime_debug.log",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        self.ping_progress = None  # 添加这行来存储进度条引用

    def setup_window(self):
        self.root.title("时间同步工具")
        self.root.resizable(False, False)
        
        # 居中窗口
        window_width, window_height = 500, 310
        self.center_window(self.root, window_width, window_height)
        
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_widgets(self):
        # 创建一个主框架并居中
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True)

        # 标签
        self.text = tk.Label(
            main_frame, text="时间同步", bg="white", fg="black", font=("", 25)
        )
        self.text.pack(pady=20)

        # 按钮
        self.button_synctime = tk.Button(
            main_frame, text="时间同步", width=30, height=2, command=self.synctime
        )
        self.button_close = tk.Button(
            main_frame, text="关闭", width=30, height=2, command=self.close_window
        )
        self.button_synctime.pack(pady=10)
        self.button_close.pack(pady=10)

    def create_menu(self):
        top_menu = tk.Menu(self.root, tearoff=False)
        menu_more = tk.Menu(top_menu, tearoff=False)
        top_menu.add_cascade(label="更多", menu=menu_more)
        menu_more.add_command(label="检查更新", command=self.check_version)
        menu_more.add_command(label="关于", command=self.about_window)
        top_menu.add_command(
            label="NTP服务器优选", command=self.open_ntp_preference
        )  # 修改菜单标签和命令
        self.root.config(menu=top_menu)

    def load_icon(self):
        try:
            # 获取当前脚本的绝对路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "app.ico")

            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(False, photo)
                self.icon_image = photo  # 保持引用，防止被垃圾回收
                print(f"图标加载成功: {icon_path}")
            else:
                print(f"图标文件不存在: {icon_path}")
        except AttributeError as e:
            print(f"AttributeError: {e}")
        except Exception as e:
            print(f"加载图标失败: {e}")

    def close_window(self):
        self.root.destroy()

    def synctime(self):
        if not self.is_admin():
            messagebox.showwarning(
                "权限不足", "同步时间需要管理员权限。请以管理员身份运行程序。"
            )
            return
            
        # 检查系统时间是否需要初始校准
        self._check_and_correct_system_time()
        
        # 显示同步动画
        self.show_sync_animation()
        threading.Thread(target=self.sync_time_task).start()

    def _check_and_correct_system_time(self):
        """检查系统时间是否异常，如果年份偏差过大则进行初步校准"""
        current_time = datetime.datetime.now()
        target_year = 2024
        if abs(current_time.year - target_year) > 20:
            try:
                target_time = datetime.datetime(2024, 1, 1, 0, 0, 0)
                self.execute_hidden_command(
                    f'date {target_time.strftime("%Y-%m-%d")} && time {target_time.strftime("%H:%M:%S")}'
                )
            except Exception as e:
                messagebox.showerror("错误", f"调整时间失败: {e}")

    def execute_hidden_command(self, command, capture_output=False):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        if capture_output:
            result = subprocess.run(
                command,
                startupinfo=startupinfo,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout
        else:
            subprocess.run(command, startupinfo=startupinfo, shell=True, check=True)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def sync_time_task(self):
        try:
            if not self.primary_ntp_server:
                self.root.after(
                    0, lambda: messagebox.showerror("错误", "没有可用的NTP服务器。")
                )
                return

            c = ntplib.NTPClient()
            try:
                response = c.request(self.primary_ntp_server, timeout=5)
            except Exception:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "错误", f"无法连接到NTP服务器: {self.primary_ntp_server}"
                    ),
                )
                return

            if response:
                current_time = response.tx_time
                dt = datetime.datetime.fromtimestamp(current_time)
                _date = dt.strftime("%Y-%m-%d")
                _time = dt.strftime("%H:%M:%S")
                print(
                    "系统当前时间",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                print("北京标准时间", _date, _time)
                a, b, c_sec = _time.split(":")
                c_sec = float(c_sec) + 0.5
                _time = f"{a}:{b}:{c_sec:.1f}"
                try:
                    os.system(f"date { _date } && time { _time }")
                    str1 = f"同步后时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    self.root.after(0, lambda: self.show_sync_success_message(str1))
                except Exception as e:
                    self.root.after(
                        0, lambda: messagebox.showwarning("失败", f"时间同步失败: {e}")
                    )
            else:
                self.root.after(
                    0, lambda: messagebox.showerror("错误", "无法连接到任何NTP服务器。")
                )
        except Exception as ex:
            self.root.after(0, lambda: messagebox.showerror("错误", f"发生异常: {ex}"))
        finally:
            # 隐藏同步动画
            self.hide_sync_animation()

    def show_sync_success_message(self, message):
        dialog = CustomDialog(self.root, "成功同步", message)
        if dialog.result:
            self.root.after(100, self.close_application)  # 使用新方法来关闭应用

    def close_application(self):
        self.root.quit()
        self.root.destroy()  # 确保窗口被销毁
        os._exit(0)  # 强制退出程序

    def check_version(self):
        # 创建并显示加载动画窗口
        loading_window = tk.Toplevel(self.root)
        self.set_window_icon(loading_window)  # 设置图标
        loading_window.title("检查更新")
        loading_window.resizable(False, False)
        
        # 居中窗口
        window_width, window_height = 400, 250
        self.center_window(loading_window, window_width, window_height)

        # 显示加载动画
        loading_label = tk.Label(
            loading_window, text="正在检查更新，请稍候...", font=("", 12)
        )
        loading_label.pack(pady=10)

        progress = ttk.Progressbar(loading_window, mode="indeterminate")
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)

        # 启动线程进行版本检查
        threading.Thread(
            target=self.check_version_task,
            args=(loading_window, progress, loading_label),
        ).start()

    def check_version_task(self, loading_window, progress, loading_label):
        try:
            response = requests.get(self.update_api)

            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("version")
                update_url = data.get("updateUrl")
                announcement = data.get("announcement", "")

                if self.version == latest_version:
                    self.root.after(
                        0,
                        lambda: self.show_message(
                            loading_window,
                            progress,
                            "你已经是最新版。",
                            "info",
                            announcement,
                        ),
                    )
                elif self.compare_versions(self.version, latest_version) < 0:
                    self.root.after(
                        0,
                        lambda: self.show_update_options(
                            loading_window,
                            progress,
                            "你的版本已经落后了，是否更新？",
                            update_url,
                            announcement,
                        ),
                    )
                else:
                    self.root.after(
                        0,
                        lambda: self.show_message(
                            loading_window,
                            progress,
                            "当前版本高于最新版本。",
                            "warning",
                            announcement,
                        ),
                    )
            else:
                raise Exception(f"API请求失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            error_message = f"网络请求失败: {e}"
            self.root.after(
                0,
                lambda: self.show_error_message(
                    loading_window, progress, loading_label, error_message
                ),
            )
        except Exception as ex:
            error_message = f"发生异常: {ex}"
            self.root.after(
                0,
                lambda: self.show_error_message(
                    loading_window, progress, loading_label, error_message
                ),
            )

    def show_error_message(
        self, loading_window, progress, loading_label, error_message
    ):
        # 停止并销毁进度条和加载标签
        progress.stop()
        progress.destroy()
        loading_label.destroy()

        # 显示错误信息
        error_label = tk.Label(
            loading_window, text="检查更新失败", font=("", 14, "bold"), fg="red"
        )
        error_label.pack(pady=10)

        error_details = tk.Text(loading_window, wrap=tk.WORD, height=5, width=40)
        error_details.insert(tk.END, error_message)
        error_details.config(state=tk.DISABLED)
        error_details.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # 添加关闭按钮
        tk.Button(loading_window, text="关闭", command=loading_window.destroy).pack(
            pady=10
        )

    def show_message(self, loading_window, progress, message, msg_type, announcement):
        # 停止并销毁进度条
        if progress:
            progress.stop()
            progress.destroy()

        # 更新加载窗口内容
        for widget in loading_window.winfo_children():
            widget.destroy()

        msg_color = {"info": "green", "error": "red", "warning": "orange"}
        tk.Label(
            loading_window,
            text=message,
            font=("", 12),
            fg=msg_color.get(msg_type, "black"),
        ).pack(pady=10)

        if announcement:
            announcement_frame = tk.Frame(loading_window)
            announcement_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            announcement_label = tk.Label(
                announcement_frame, text="更新公告:", font=("", 10, "bold")
            )
            announcement_label.pack(anchor="w")

            announcement_text = tk.Text(
                announcement_frame, wrap=tk.WORD, height=5, width=40
            )
            announcement_text.insert(tk.END, announcement)
            announcement_text.config(state=tk.DISABLED)
            announcement_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(loading_window, text="关闭", command=loading_window.destroy).pack(
            pady=10
        )

    def show_update_options(
        self, loading_window, progress, message, update_url, announcement
    ):
        # 停止并销毁进度条
        if progress:
            progress.stop()
            progress.destroy()

        # 更新加载窗口内容
        for widget in loading_window.winfo_children():
            widget.destroy()

        tk.Label(loading_window, text=message, font=("", 12)).pack(pady=10)

        if announcement:
            announcement_frame = tk.Frame(loading_window)
            announcement_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            announcement_label = tk.Label(
                announcement_frame, text="更新公告:", font=("", 10, "bold")
            )
            announcement_label.pack(anchor="w")

            announcement_text = tk.Text(
                announcement_frame, wrap=tk.WORD, height=5, width=40
            )
            announcement_text.insert(tk.END, announcement)
            announcement_text.config(state=tk.DISABLED)
            announcement_text.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(loading_window)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame, text="更新", command=lambda: self.update(update_url)
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=loading_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def update(self, update_url):
        webbrowser.open(update_url)

    def about_window(self):
        if (
            hasattr(self, "about_window_instance")
            and self.about_window_instance
            and self.about_window_instance.winfo_exists()
        ):
            self.about_window_instance.lift()
            return

        # 创建关于窗口
        self.about_window_instance = tk.Toplevel(self.root)
        self.set_window_icon(self.about_window_instance)
        self.about_window_instance.title("关于")
        
        # 居中窗口
        window_width, window_height = 370, 230
        self.center_window(self.about_window_instance, window_width, window_height)
        self.about_window_instance.resizable(False, False)

        # 显示加载动画
        loading_label = tk.Label(
            self.about_window_instance,
            text="正在加载关于信息，请稍候...",
            font=("", 12),
        )
        loading_label.pack(pady=10)

        progress = ttk.Progressbar(self.about_window_instance, mode="indeterminate")
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)

        # 启动线程加载关于信息
        threading.Thread(
            target=self.load_about_content, args=(loading_label, progress)
        ).start()

    def load_about_content(self, loading_label, progress):
        default_about_content = (
            "远程公告加载失败，这是默认内容\n"
            "感谢使用此软件！\n"
            "QQ：2147606879 \n"
            "博客地址：especial.top\n"
            "github仓库：https://github.com/canfengplaeir/synctime\n"
            "gitee仓库：https://gitee.com/canfeng_plaeir/synctime"
        )
        
        about_content = default_about_content
        try:
            with requests.get(self.about_api, timeout=5) as response:
                if response.status_code == 200:
                    data = response.json()
                    about_content = data.get("about_content", default_about_content)
                    if about_content == default_about_content:
                        logging.warning("未能从API获取about_content，使用默认内容")
                else:
                    logging.error(f"API请求失败，状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"加载关于信息失败: {e}")
            print(f"加载关于信息失败: {e}")

        # 更新关于窗口内容
        self.root.after(
            0,
            lambda: self.display_about_content(loading_label, progress, about_content),
        )

    def display_about_content(self, loading_label, progress, about_content):
        # 停止并销毁进度条和加载标签
        progress.stop()
        progress.destroy()
        loading_label.destroy()

        text_about = tk.Text(self.about_window_instance, wrap=tk.CHAR, font=("", 14))
        text_about.insert(tk.INSERT, about_content)
        text_about.config(state=tk.DISABLED)
        text_about.pack(padx=10, pady=10)

    def set_window_icon(self, window):
        """
        设置顶层窗口的图标为主窗口的图标
        """
        if hasattr(self, "icon_image"):
            window.iconphoto(False, self.icon_image)
            
    def center_window(self, window, width, height):
        """
        使窗口在屏幕上居中显示
        
        参数:
            window: 要居中的窗口
            width: 窗口宽度
            height: 窗口高度
        """
        x_pos = int((self.screenwidth - width) / 2)
        y_pos = int((self.screenheight - height) / 2)
        window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

    def show_sync_animation(self):
        # 创建同步动画窗口
        self.sync_window = tk.Toplevel(self.root)
        self.set_window_icon(self.sync_window)
        self.sync_window.title("同步时间")
        self.sync_window.resizable(False, False)
        
        # 居中窗口
        window_width, window_height = 300, 100
        self.center_window(self.sync_window, window_width, window_height)
        self.sync_window.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁用关闭按钮

        tk.Label(self.sync_window, text="正在同步时间，请稍候...", font=("", 12)).pack(
            pady=10
        )
        progress = ttk.Progressbar(self.sync_window, mode="indeterminate")
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)
        self.sync_progress = progress

    def hide_sync_animation(self):
        if hasattr(self, "sync_window"):
            self.sync_progress.stop()
            self.sync_window.destroy()

    def compare_versions(self, version1, version2):
        """
        比较两个版本号字符串
        """
        v1 = list(map(int, version1.split(".")))
        v2 = list(map(int, version2.split(".")))
        return (v1 > v2) - (v1 < v2)

    def load_ntp_server_list(self):
        try:
            with open(self.ntp_servers_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.ntp_server_list = data.get("ntp_servers", [])
        except FileNotFoundError:
            print("ntp_servers.json文件未找到，使用默认NTP服务器列表。")
            self.ntp_server_list = [
                "edu.ntp.org.cn",
                "ntp.ntsc.ac.cn",
                "cn.ntp.org.cn",
                "ntp1.aliyun.com",
                "ntp2.aliyun.com",
                "ntp3.aliyun.com",
                "ntp4.aliyun.com",
                "ntp5.aliyun.com",
                "ntp6.aliyun.com",
                "ntp7.aliyun.com",
                "ntp.tencent.com",
                "tw.ntp.org.cn",
                "us.ntp.org.cn",
                "cn.pool.ntp.org",
                "jp.ntp.org.cn",
            ]
            self.save_ntp_server_list()

    def save_ntp_server_list(self):
        try:
            with open(self.ntp_servers_filepath, "w", encoding="utf-8") as f:
                json.dump(
                    {"ntp_servers": self.ntp_server_list},
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
            print("NTP服务器列表已保存。")
        except Exception as e:
            print(f"保存NTP服务器列表失败: {e}")

    def reset_ntp_server_list(self):
        self.ntp_server_list = [
            "edu.ntp.org.cn",
            "ntp.ntsc.ac.cn",
            "cn.ntp.org.cn",
            "ntp1.aliyun.com",
            "ntp2.aliyun.com",
            "ntp3.aliyun.com",
            "ntp4.aliyun.com",
            "ntp5.aliyun.com",
            "ntp6.aliyun.com",
            "ntp7.aliyun.com",
            "ntp.tencent.com",
            "tw.ntp.org.cn",
            "us.ntp.org.cn",
            "cn.pool.ntp.org",
            "jp.ntp.org.cn",
        ]
        self.save_ntp_server_list()
        
        # 更新主服务器为列表中的第一个
        self.primary_ntp_server = self.ntp_server_list[0]
        
        # 更新显示
        if hasattr(self, "current_server_label"):
            self.current_server_label.config(text=self.primary_ntp_server)
        
        # 刷新列表
        self._refresh_ntp_server_tree()
        
        messagebox.showinfo(
            "重置成功",
            "已重置NTP服务器列表为默认值。",
            parent=self.settings_window_instance,
        )

    def open_ntp_preference(self):
        if (
            hasattr(self, "settings_window_instance")
            and self.settings_window_instance
            and self.settings_window_instance.winfo_exists()
        ):
            self.settings_window_instance.lift()
            return

        # 创建设置窗口
        self.settings_window_instance = tk.Toplevel(self.root)
        self.set_window_icon(self.settings_window_instance)
        self.settings_window_instance.title("NTP服务器优选")
        self.settings_window_instance.resizable(False, False)
        
        # 居中窗口，增加宽度以容纳更现代的布局
        window_width, window_height = 750, 950
        self.center_window(self.settings_window_instance, window_width, window_height)
        
        # 使用更现代的ttk风格
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)  # 增加行高
        style.map('Treeview', 
                 background=[('selected', '#0078D7')],  # Windows 10 蓝色
                 foreground=[('selected', 'white')])
        
        # 创建主框架
        main_frame = tk.Frame(self.settings_window_instance)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== 创建信息和设置分组 =====
        info_frame = ttk.LabelFrame(main_frame, text="服务器信息与设置", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # 当前选中的NTP服务器
        current_server_frame = tk.Frame(info_frame)
        current_server_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            current_server_frame, 
            text="当前选中的NTP服务器:", 
            font=("", 11, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.current_server_label = tk.Label(
            current_server_frame,
            text=self.primary_ntp_server if self.primary_ntp_server else "无",
            font=("", 11),
            fg="blue"
        )
        self.current_server_label.pack(side=tk.LEFT)
        
        # 分隔线
        ttk.Separator(info_frame, orient="horizontal").pack(fill=tk.X, pady=8)
        
        # 设置部分 - 使用网格布局使其更整齐
        settings_frame = tk.Frame(info_frame)
        settings_frame.pack(fill=tk.X)
        
        # Ping超时设置
        tk.Label(
            settings_frame,
            text="Ping超时设置(秒):",
            font=("", 10)
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        # 设置Ping超时默认值
        self.ping_timeout = tk.StringVar(value="2")
        timeout_entry = tk.Entry(settings_frame, textvariable=self.ping_timeout, width=5)
        timeout_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # 添加提示标签
        tk.Label(
            settings_frame,
            text="(推荐值: 1-5秒)",
            font=("", 9),
            fg="gray"
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # 自动选择最佳服务器选项
        self.auto_select_best = tk.BooleanVar(value=False)
        auto_select_cb = tk.Checkbutton(
            settings_frame,
            text="Ping完成后自动选择延迟最低的服务器为主服务器",
            variable=self.auto_select_best,
            font=("", 10)
        )
        auto_select_cb.grid(row=1, column=0, columnspan=3, sticky="w", pady=5)
        
        # ===== 创建服务器列表分组 =====
        servers_frame = ttk.LabelFrame(main_frame, text="NTP服务器列表", padding=10)
        servers_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # 创建一个框架来容纳Treeview和滚动条
        tree_frame = tk.Frame(servers_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # 创建垂直滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建水平滚动条
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # 添加一个新列来显示是否为当前选中的服务器
        columns = ("服务器地址", "延迟(ms)", "状态")
        self.ntp_server_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=12,  # 设置固定高度使界面更协调
            selectmode="browse"  # 只允许单选
        )
        
        # 设置列标题和宽度
        self.ntp_server_tree.heading("服务器地址", text="服务器地址")
        self.ntp_server_tree.heading("延迟(ms)", text="延迟(ms)")
        self.ntp_server_tree.heading("状态", text="状态")
        
        self.ntp_server_tree.column("服务器地址", width=300, anchor="center", minwidth=150)
        self.ntp_server_tree.column("延迟(ms)", width=150, anchor="center", minwidth=100)
        self.ntp_server_tree.column("状态", width=150, anchor="center", minwidth=80)
        
        self.ntp_server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 配置滚动条
        vsb.config(command=self.ntp_server_tree.yview)
        hsb.config(command=self.ntp_server_tree.xview)

        # 填充服务器列表并标记当前选中的服务器
        self._refresh_ntp_server_tree()
        
        # 添加选择和双击事件处理
        self.ntp_server_tree.bind("<Double-1>", self._on_server_double_click)
        self.ntp_server_tree.bind("<<TreeviewSelect>>", self._on_server_select)
        
        # 操作说明框
        help_frame = tk.Frame(servers_frame)
        help_frame.pack(fill=tk.X, pady=(5, 0))
        
        help_text = "操作说明: 双击服务器可直接设为主服务器; Ping完成后会按延迟排序显示"
        tk.Label(
            help_frame,
            text=help_text,
            font=("", 9),
            fg="gray"
        ).pack(side=tk.LEFT)
        
        # ===== 创建操作按钮分组 =====
        actions_frame = ttk.LabelFrame(main_frame, text="操作", padding=10)
        actions_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 服务器管理按钮框
        manage_frame = tk.Frame(actions_frame)
        manage_frame.pack(fill=tk.X, pady=(0, 10))
        
        manage_label = tk.Label(manage_frame, text="服务器管理:", font=("", 10))
        manage_label.pack(side=tk.LEFT, padx=(0, 10))
        
        add_button = ttk.Button(
            manage_frame,
            text="添加服务器",
            command=lambda: self.add_ntp_server_entry(self.settings_window_instance),
            width=12
        )
        delete_button = ttk.Button(
            manage_frame, text="删除选中", command=self.remove_selected_ntp_server,
            width=12
        )
        reset_button = ttk.Button(
            manage_frame, text="重置为默认", command=self.reset_ntp_server_list,
            width=12
        )
        select_button = ttk.Button(
            manage_frame, text="设为主服务器", command=self.set_selected_as_primary,
            width=12
        )
        export_button = ttk.Button(
            manage_frame, text="导出列表", command=self.export_ntp_server_list,
            width=12
        )

        add_button.pack(side=tk.LEFT, padx=5)
        delete_button.pack(side=tk.LEFT, padx=5)
        reset_button.pack(side=tk.LEFT, padx=5)
        select_button.pack(side=tk.LEFT, padx=5)
        export_button.pack(side=tk.LEFT, padx=5)

        # 添加第二行按钮
        manage_frame2 = tk.Frame(actions_frame)
        manage_frame2.pack(fill=tk.X, pady=(5, 0))
        
        # 从API更新按钮
        update_api_button = ttk.Button(
            manage_frame2,
            text="从API更新服务器列表",
            command=self.update_ntp_servers_from_api,
            width=20
        )
        update_api_button.pack(side=tk.LEFT, padx=5)

        # 分隔线
        ttk.Separator(actions_frame, orient="horizontal").pack(fill=tk.X, pady=8)
        
        # Ping测试按钮和进度显示
        ping_frame = tk.Frame(actions_frame)
        ping_frame.pack(fill=tk.X)
        
        ping_label = tk.Label(ping_frame, text="Ping测试:", font=("", 10))
        ping_label.pack(side=tk.LEFT, padx=(0, 10))

        # Ping按钮
        self.ping_button = ttk.Button(
            ping_frame, text="开始Ping所有服务器", 
            command=self.ping_all_ntp_servers_latency,
            width=20
        )
        self.ping_button.pack(side=tk.LEFT)
        
        # 状态标签
        self.ping_status_label = tk.Label(
            ping_frame, 
            text="",
            font=("", 9),
            fg="blue"
        )
        self.ping_status_label.pack(side=tk.LEFT, padx=10)

        # 进度条（初始时隐藏）
        self.ping_progress = ttk.Progressbar(
            actions_frame, mode="indeterminate", length=400
        )
        self.ping_progress.pack(fill=tk.X, pady=(10, 0))
        self.ping_progress.pack_forget()  # 初始时隐藏进度条
        
    def _on_server_select(self, event):
        """处理服务器选中事件，提供视觉反馈"""
        # 获取选中的项目
        selected = self.ntp_server_tree.selection()
        if selected:
            # 高亮显示选中行
            self.ntp_server_tree.focus(selected[0])
            
    def export_ntp_server_list(self):
        """导出NTP服务器列表到文本文件"""
        if not self.ntp_server_list:
            messagebox.showwarning(
                "导出失败",
                "NTP服务器列表为空，无法导出。",
                parent=self.settings_window_instance,
            )
            return
            
        try:
            # 默认导出路径为程序所在目录
            default_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "ntp_servers_exported.txt"
            )
            
            # 写入文件
            with open(default_path, "w", encoding="utf-8") as f:
                # 写入标题行
                f.write("# SyncTime NTP服务器列表导出\n")
                f.write(f"# 导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# 当前选中的主服务器已标记为 [主]\n\n")
                
                # 写入服务器列表
                for server in self.ntp_server_list:
                    if server == self.primary_ntp_server:
                        f.write(f"{server} [主]\n")
                    else:
                        f.write(f"{server}\n")
            
            # 显示成功消息
            messagebox.showinfo(
                "导出成功",
                f"NTP服务器列表已导出到：\n{default_path}",
                parent=self.settings_window_instance,
            )
        except Exception as e:
            logging.error(f"导出NTP服务器列表失败: {e}")
            messagebox.showerror(
                "导出失败",
                f"导出NTP服务器列表时发生错误：\n{e}",
                parent=self.settings_window_instance,
            )

    def _refresh_ntp_server_tree(self):
        """刷新NTP服务器列表显示"""
        # 清空现有项目
        self.ntp_server_tree.delete(*self.ntp_server_tree.get_children())
        
        # 重新填充列表
        for index, server in enumerate(self.ntp_server_list):
            status = "当前选中" if server == self.primary_ntp_server else ""
            item = self.ntp_server_tree.insert("", tk.END, values=(server, "待测", status))
            
            # 设置交替行背景色以提高可读性
            if index % 2 == 0:
                self.ntp_server_tree.item(item, tags=("evenrow",))
            else:
                self.ntp_server_tree.item(item, tags=("oddrow",))
        
        # 配置标签颜色
        self.ntp_server_tree.tag_configure("evenrow", background="#f0f0f0")
        self.ntp_server_tree.tag_configure("oddrow", background="white")
            
    def _on_server_double_click(self, event):
        """处理服务器列表的双击事件"""
        self.set_selected_as_primary()
        
    def set_selected_as_primary(self):
        """将选中的服务器设置为主NTP服务器"""
        selected = self.ntp_server_tree.selection()
        if not selected:
            messagebox.showwarning(
                "未选择",
                "请先选择要设置为主服务器的NTP服务器。",
                parent=self.settings_window_instance,
            )
            return
            
        item = selected[0]
        server = self.ntp_server_tree.item(item, "values")[0]
        
        # 如果已经是主服务器，不需要重复设置
        if server == self.primary_ntp_server:
            messagebox.showinfo(
                "提示",
                f"{server} 已经是当前选中的主NTP服务器。",
                parent=self.settings_window_instance,
            )
            return
        
        # 更新主服务器
        self.primary_ntp_server = server
        
        # 更新显示
        self.current_server_label.config(text=server)
        
        # 高亮显示选中的服务器（通过刷新列表）
        self._refresh_ntp_server_tree()
        
        # 选中并滚动到当前服务器
        for item in self.ntp_server_tree.get_children():
            if self.ntp_server_tree.item(item, "values")[0] == server:
                self.ntp_server_tree.selection_set(item)
                self.ntp_server_tree.see(item)  # 确保可见
                break
        
        messagebox.showinfo(
            "设置成功",
            f"已将 {server} 设置为主NTP服务器。",
            parent=self.settings_window_instance,
        )

    def add_ntp_server_entry(self, parent_window):
        def save_new_server():
            new_server = entry.get().strip()
            if new_server and new_server not in self.ntp_server_list:
                self.ntp_server_list.append(new_server)
                self.save_ntp_server_list()
                
                # 如果这是第一个服务器，将其设为主服务器
                if len(self.ntp_server_list) == 1:
                    self.primary_ntp_server = new_server
                    if hasattr(self, "current_server_label"):
                        self.current_server_label.config(text=new_server)
                
                # 更新列表显示
                status = "当前选中" if new_server == self.primary_ntp_server else ""
                self.ntp_server_tree.insert("", tk.END, values=(new_server, "待测", status))
                
                add_window.destroy()
            else:
                messagebox.showwarning(
                    "无效输入", "请输入有效且未存在的NTP服务器地址。", parent=add_window
                )

        add_window = tk.Toplevel(parent_window)
        self.set_window_icon(add_window)
        add_window.title("添加NTP服务器")
        add_window.resizable(False, False)

        # 居中窗口
        window_width, window_height = 350, 150
        self.center_window(add_window, window_width, window_height)

        # 使用更现代的布局
        frame = ttk.Frame(add_window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="服务器地址:", font=("", 11)).pack(pady=(0, 10))
        entry = ttk.Entry(frame, width=40)
        entry.pack(pady=5, fill=tk.X)
        
        # 按钮框
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(15, 0), fill=tk.X)
        
        ttk.Button(btn_frame, text="取消", command=add_window.destroy, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="添加", command=save_new_server, width=10).pack(side=tk.RIGHT, padx=5)
        
        # 设置焦点并绑定回车键
        entry.focus_set()
        entry.bind("<Return>", lambda event: save_new_server())
        add_window.bind("<Escape>", lambda event: add_window.destroy())

    def remove_selected_ntp_server(self):
        selected = self.ntp_server_tree.selection()
        if selected:
            item = selected[0]
            server = self.ntp_server_tree.item(item, "values")[0]
            
            confirm = messagebox.askyesno(
                "确认删除",
                f"是否删除NTP服务器: {server}?",
                parent=self.settings_window_instance,
            )
            if confirm:
                self.ntp_server_tree.delete(item)
                index = self.ntp_server_list.index(server)
                self.ntp_server_list.pop(index)
                self.save_ntp_server_list()
                
                # 如果删除的是当前主服务器，则更新主服务器
                if server == self.primary_ntp_server:
                    self.primary_ntp_server = (
                        self.ntp_server_list[0] if self.ntp_server_list else None
                    )
                    # 更新显示
                    if hasattr(self, "current_server_label"):
                        self.current_server_label.config(
                            text=self.primary_ntp_server if self.primary_ntp_server else "无"
                        )
                    # 刷新列表以更新状态
                    self._refresh_ntp_server_tree()
        else:
            messagebox.showwarning(
                "未选择",
                "请先选择要删除的NTP服务器。",
                parent=self.settings_window_instance,
            )

    def ping_all_ntp_servers_latency(self):
        """开始Ping所有NTP服务器"""
        # 禁用Ping按钮
        self.ping_button.config(state=tk.DISABLED)
        
        # 显示初始状态
        self.update_ping_status("正在准备Ping测试...")
        self.ping_progress.start(10)  # 开始进度条动画
        
        # 启动线程执行Ping测试
        threading.Thread(target=self.perform_ping_ntp_servers).start()

    def perform_ping_ntp_servers(self):
        try:
            system_platform = platform.system().lower()
            logging.debug(f"当前操作系统: {system_platform}")
            
            # 获取用户设置的超时时间（秒）
            try:
                timeout_seconds = float(self.ping_timeout.get())
                if timeout_seconds <= 0:  # 确保超时值为正数
                    timeout_seconds = 2  # 默认2秒
            except (ValueError, AttributeError):
                timeout_seconds = 2  # 默认2秒
                
            logging.debug(f"设置的Ping超时时间: {timeout_seconds}秒")
            
            # 根据不同系统设置ping命令格式
            if system_platform == "windows":
                ping_cmd = f"ping -n 1 -w {int(timeout_seconds * 1000)} {{server}}"  # Windows使用毫秒
            else:
                ping_cmd = f"ping -c 1 -W {int(timeout_seconds)} {{server}}"  # Linux/Mac使用秒

            ping_results = {}
            total_servers = len(self.ntp_server_list)
            processed = 0
            
            for server in self.ntp_server_list:
                processed += 1
                if processed % 2 == 0:  # 每处理2个服务器更新一次进度状态
                    status_text = f"正在测试服务器... ({processed}/{total_servers})"
                    self.root.after(0, lambda t=status_text: self.update_ping_status(t))
                    
                logging.debug(f"开始Ping服务器: {server}")
                try:
                    cmd = ping_cmd.format(server=server)
                    logging.debug(f"执行命令: {cmd}")

                    output = self.execute_hidden_command(cmd, capture_output=True)

                    logging.debug(f"Ping命令输出 for {server}:\n{output}")
                    latency = self.extract_ping_latency(output, system_platform)
                    logging.debug(f"解析后的延迟 for {server}: {latency}")
                    if latency is not None:
                        if isinstance(latency, (int, float)):
                            ping_results[server] = latency
                            status = f"{latency} ms"
                        else:
                            status = latency  # 使用返回的错误信息
                    else:
                        status = "无法解析延迟"
                    # 更新Treeview中的状态
                    for item in self.ntp_server_tree.get_children():
                        if self.ntp_server_tree.item(item, "values")[0] == server:
                            # 保持状态列不变
                            current_status = self.ntp_server_tree.item(item, "values")[2]
                            self.ntp_server_tree.item(item, values=(server, status, current_status))
                            logging.debug(
                                f"Treeview 中已更新服务器 {server} 的状态为 {status}"
                            )
                            break
                except Exception as e:
                    logging.error(f"Ping {server} 失败: {e}")
                    status = "Ping失败"
                    for item in self.ntp_server_tree.get_children():
                        if self.ntp_server_tree.item(item, "values")[0] == server:
                            current_status = self.ntp_server_tree.item(item, "values")[2]
                            self.ntp_server_tree.item(item, values=(server, status, current_status))
                            break

            # 清除状态更新
            self.root.after(0, lambda: self.update_ping_status("测试完成，正在处理结果..."))
                
            logging.debug(f"Ping结果: {ping_results}")
            if ping_results:
                # 按延迟从小到大排序
                sorted_servers = sorted(ping_results.items(), key=lambda item: item[1])
                
                # 更新服务器列表顺序
                self.ntp_server_list = [server for server, _ in sorted_servers]
                self.save_ntp_server_list()  # 保存排序后的服务器列表
                
                # 重新显示排序后的列表
                self._refresh_sorted_server_tree(ping_results)

                # 找到延迟最低的服务器
                best_server = self.ntp_server_list[0]
                
                # 判断是否自动选择最佳服务器
                auto_select = hasattr(self, "auto_select_best") and self.auto_select_best.get()
                if auto_select and best_server:
                    # 更新主服务器为延迟最低的服务器
                    old_primary = self.primary_ntp_server
                    self.primary_ntp_server = best_server
                    
                    # 更新显示
                    if hasattr(self, "current_server_label"):
                        self.current_server_label.config(text=best_server)
                    
                    # 刷新列表状态
                    self._refresh_sorted_server_tree(ping_results)
                    
                    # 选中并滚动到当前服务器
                    for item in self.ntp_server_tree.get_children():
                        if self.ntp_server_tree.item(item, "values")[0] == best_server:
                            self.ntp_server_tree.selection_set(item)
                            self.ntp_server_tree.see(item)  # 确保可见
                            self.ntp_server_tree.focus(item)  # 设置焦点
                            break
                    
                    auto_select_message = f"已自动将延迟最低的服务器 {best_server} 设为主服务器。"
                else:
                    auto_select_message = ""
                
                # 构建消息
                message = "Ping结果：\n" + "\n".join([f"{s}: {ms} ms" for s, ms in sorted_servers])
                
                # 添加建议信息
                message += f"\n\n延迟最低的服务器是: {best_server}"
                
                # 如果自动选择了最佳服务器，显示通知
                if auto_select and best_server:
                    message += f"\n\n{auto_select_message}"
                # 如果没有自动选择，且当前选择的不是最佳的，给出提示
                elif best_server != self.primary_ntp_server:
                    message += f"\n当前选中的服务器是: {self.primary_ntp_server}"
                    message += "\n\n您可以双击服务器或使用“设为主服务器”按钮来更改选择。"
                
                logging.debug(f"最佳服务器: {best_server}")
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Ping结果", message, parent=self.settings_window_instance
                    ),
                )
            else:
                logging.warning("无法Ping任何NTP服务器。")
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "错误",
                        "无法Ping任何NTP服务器。",
                        parent=self.settings_window_instance
                    ),
                )
        except Exception as ex:
            error_message = f"发生异常: {ex}"
            logging.error(error_message)
            self.root.after(
                0,
                lambda: self.show_error_message(
                    self.settings_window_instance, None, None, error_message
                ),
            )
        finally:
            # 在主线程中更新UI
            self.root.after(0, self.finish_ping_task)
    
    def update_ping_status(self, status_text):
        """更新Ping状态信息"""
        if hasattr(self, "ping_status_label"):
            self.ping_status_label.config(text=status_text)
            
            # 如果有状态文本则显示进度条，否则隐藏
            if status_text:
                if not self.ping_progress.winfo_ismapped():
                    self.ping_progress.pack(fill=tk.X, pady=(10, 0))
            else:
                if self.ping_progress.winfo_ismapped():
                    self.ping_progress.pack_forget()
                    
        # 强制更新UI，确保状态立即显示
        if hasattr(self, "settings_window_instance") and self.settings_window_instance.winfo_exists():
            self.settings_window_instance.update_idletasks()

    def _refresh_sorted_server_tree(self, ping_results):
        """根据ping结果重新排序并刷新服务器列表"""
        # 清空现有项目
        self.ntp_server_tree.delete(*self.ntp_server_tree.get_children())
        
        # 重新填充列表
        for index, server in enumerate(self.ntp_server_list):
            status = "当前选中" if server == self.primary_ntp_server else ""
            if server in ping_results:
                latency_text = f"{ping_results.get(server)} ms"
            else:
                latency_text = "Ping失败"
                
            item = self.ntp_server_tree.insert("", tk.END, values=(server, latency_text, status))
            
            # 设置交替行背景色以提高可读性
            if index % 2 == 0:
                self.ntp_server_tree.item(item, tags=("evenrow",))
            else:
                self.ntp_server_tree.item(item, tags=("oddrow",))
        
        # 配置标签颜色
        self.ntp_server_tree.tag_configure("evenrow", background="#f0f0f0")
        self.ntp_server_tree.tag_configure("oddrow", background="white")

    def finish_ping_task(self):
        """结束Ping任务时的清理工作"""
        self.ping_progress.stop()  # 停止进度条动画
        self.update_ping_status("")  # 清除状态文本，这会隐藏进度条
        self.ping_button.config(state=tk.NORMAL)  # 重新启用按钮

    def extract_ping_latency(self, ping_response, platform_system):
        """
        从ping响应中提取延迟时间
        
        参数:
            ping_response: ping命令的输出
            platform_system: 操作系统类型
        
        返回:
            延迟时间(毫秒)或None(如果无法解析)
        """
        import re
        
        logging.debug(f"解析Ping响应: {ping_response}")
        
        # 根据不同系统使用不同的正则表达式
        patterns = {
            "windows": r"时间[=<]\s*(\d+)ms",
            "linux": r"time[=<]\s*(\d+\.\d+) ms",
            "darwin": r"time[=<]\s*(\d+\.\d+) ms"  # macOS使用与Linux相同的模式
        }
        
        # 获取合适的正则表达式，如果没有匹配的系统则默认使用Windows的
        pattern = patterns.get(platform_system.lower(), patterns["windows"])
        
        match = re.search(pattern, ping_response)
        if match:
            latency = float(match.group(1))
            logging.debug(f"匹配到延迟: {latency} ms")
            return latency
            
        logging.warning("未能解析到延迟。")
        return None

    def update_ntp_servers_from_api(self):
        """从API获取并更新NTP服务器列表"""
        if not hasattr(self, 'ntp_servers_api'):
            self.ntp_servers_api = "https://synctime-api.netlify.app/api/ntp_servers"
            
        # 显示进度窗口
        progress_window = tk.Toplevel(self.settings_window_instance)
        self.set_window_icon(progress_window)
        progress_window.title("从API更新服务器列表")
        progress_window.resizable(False, False)
        progress_window.transient(self.settings_window_instance)
        progress_window.grab_set()
        
        # 居中显示
        window_width, window_height = 300, 120
        self.center_window(progress_window, window_width, window_height)
        
        # 提示标签
        tk.Label(
            progress_window, 
            text="正在从API获取最新的NTP服务器列表...",
            font=("", 10)
        ).pack(pady=(15, 10))
        
        # 进度条
        progress = ttk.Progressbar(progress_window, mode="indeterminate", length=250)
        progress.pack(pady=5, padx=20, fill=tk.X)
        progress.start(10)
        
        # 启动线程进行API请求
        threading.Thread(
            target=self._fetch_ntp_servers_task,
            args=(progress_window, progress)
        ).start()
    
    def _fetch_ntp_servers_task(self, progress_window, progress):
        """异步获取NTP服务器列表的任务"""
        result = {"success": False, "message": "", "servers": []}
        
        try:
            # 发送API请求
            response = requests.get(self.ntp_servers_api, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recommended_servers = data.get("recommended_servers", [])
                
                if recommended_servers:
                    # 提取服务器列表
                    new_servers = [server["server"] for server in recommended_servers]
                    
                    # 获取服务器描述（用于显示在消息中）
                    server_descriptions = {server["server"]: server["description"] 
                                          for server in recommended_servers}
                    
                    # 更新结果
                    result["success"] = True
                    result["message"] = f"成功从API获取了 {len(new_servers)} 个NTP服务器"
                    result["servers"] = new_servers
                    result["descriptions"] = server_descriptions
                else:
                    result["message"] = "API返回的服务器列表为空"
            else:
                result["message"] = f"API请求失败，状态码: {response.status_code}"
                
        except requests.RequestException as e:
            result["message"] = f"网络请求失败: {e}"
        except ValueError as e:
            result["message"] = f"解析API响应失败: {e}"
        except Exception as e:
            result["message"] = f"发生未知错误: {e}"
        
        # 在主线程中更新UI
        self.root.after(0, lambda: self._process_api_result(progress_window, progress, result))
    
    def _process_api_result(self, progress_window, progress, result):
        """处理API结果并更新UI"""
        # 停止进度条
        progress.stop()
        
        # 关闭进度窗口
        progress_window.destroy()
        
        if result["success"]:
            # 如果成功获取服务器列表
            old_server_count = len(self.ntp_server_list)
            new_server_count = len(result["servers"])
            added_servers = [s for s in result["servers"] if s not in self.ntp_server_list]
            
            # 构建确认消息
            message = f"从API获取了 {new_server_count} 个NTP服务器\n\n"
            
            if added_servers:
                message += "新增服务器:\n"
                for server in added_servers[:5]:  # 只显示前5个
                    desc = result["descriptions"].get(server, "")
                    message += f"• {server} - {desc}\n"
                
                if len(added_servers) > 5:
                    message += f"...以及其他 {len(added_servers) - 5} 个服务器\n"
                
                message += f"\n是否更新NTP服务器列表？"
                
                # 显示确认对话框
                if messagebox.askyesno("更新确认", message, parent=self.settings_window_instance):
                    # 保存原有的主服务器
                    original_primary = self.primary_ntp_server
                    
                    # 更新服务器列表
                    self.ntp_server_list = result["servers"]
                    self.save_ntp_server_list()
                    
                    # 如果原主服务器不在新列表中，设置第一个为主服务器
                    if original_primary not in self.ntp_server_list:
                        self.primary_ntp_server = self.ntp_server_list[0] if self.ntp_server_list else None
                        if hasattr(self, "current_server_label"):
                            self.current_server_label.config(
                                text=self.primary_ntp_server if self.primary_ntp_server else "无"
                            )
                    
                    # 刷新服务器列表显示
                    self._refresh_ntp_server_tree()
                    
                    # 显示成功消息
                    messagebox.showinfo(
                        "更新成功", 
                        f"NTP服务器列表已更新，当前共有 {len(self.ntp_server_list)} 个服务器。",
                        parent=self.settings_window_instance
                    )
            else:
                messagebox.showinfo(
                    "服务器列表已是最新", 
                    f"API返回的服务器列表与当前列表匹配，无需更新。",
                    parent=self.settings_window_instance
                )
        else:
            # 如果获取失败
            messagebox.showerror(
                "更新失败", 
                f"无法从API获取NTP服务器列表:\n{result['message']}",
                parent=self.settings_window_instance
            )


class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.create_widgets(message)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.wait_window(self)

    def create_widgets(self, message):
        tk.Label(self, text=message, wraplength=300).pack(pady=10)
        tk.Label(self, text="是否退出程序？").pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="退出程序", width=10, command=self.ok).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="取消", width=10, command=self.cancel).pack(
            side=tk.LEFT, padx=5
        )

    def ok(self):
        self.result = True
        self.destroy()

    def cancel(self):
        self.result = False
        self.destroy()


if __name__ == "__main__":
    root_window = ttk.Window(themename="litera")

    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # 设置程序缩放
    root_window.tk.call("tk", "scaling", ScaleFactor / 75)

    # 创建应用实例
    app = SyncTimeApp(root_window)

    # 检查DPI适配是否正常
    current_dpi = root_window.winfo_fpixels("1i")
    expected_dpi = 96 * (ScaleFactor / 100)
    if abs(current_dpi - expected_dpi) > 1:
        print(
            f"警告: DPI适配可能不正常。当前DPI: {current_dpi:.2f}, 预期DPI: {expected_dpi:.2f}"
        )
    else:
        print(f"DPI适配正常。当前DPI: {current_dpi:.2f}")

    root_window.mainloop()
