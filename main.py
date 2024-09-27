import os
import webbrowser
import ntplib
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import requests
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import ctypes
import json
import subprocess  # 新增
import platform    # 新增
import logging


class SyncTimeApp:
    def __init__(self, root):
        self.root = root
        self.version = "1.0.0"  # 更新版本号格式为x.x.x
        self.update_api = "https://synctimeapi.vercel.app/api/version"  # 替换为您的Vercel API地址
        self.about_api = "https://synctimeapi.vercel.app/api/about"  # 新增关于页API地址
        self.last_check_time = 0
        self.check_interval = 3600  # 1小时

        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()

        self.ntp_servers_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntp_servers.json")
        self.load_ntp_servers()
        self.primary_ntp_server = self.ntp_servers[0] if self.ntp_servers else None

        self.setup_window()
        self.create_widgets()
        self.create_menu()
        self.load_icon()  # 确保加载图标

        logging.basicConfig(
            filename='synctime_debug.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_window(self):
        self.root.title("时间同步工具")
        self.root.resizable(False, False)
        # 将位置坐标转换为整数
        x_pos = int((self.screenwidth - 500) / 2)
        y_pos = int((self.screenheight - 310) / 2)
        size_geo = f'{500}x{310}+{x_pos}+{y_pos}'
        self.root.geometry(size_geo)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_widgets(self):
        # 创建一个主框架并居中
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True)

        # 标签
        self.text = tk.Label(main_frame, text="时间同步", bg="white", fg="black", font=("", 25))
        self.text.pack(pady=20)

        # 按钮
        self.button_synctime = tk.Button(main_frame, text="时间同步", width=30, height=2, command=self.synctime)
        self.button_close = tk.Button(main_frame, text="关闭", width=30, height=2, command=self.close_window)
        self.button_synctime.pack(pady=10)
        self.button_close.pack(pady=10)

    def create_menu(self):
        top_menu = tk.Menu(self.root, tearoff=False)
        menu_more = tk.Menu(top_menu, tearoff=False)
        top_menu.add_cascade(label="更多", menu=menu_more)
        menu_more.add_command(label="检查更新", command=self.CheckVersion)
        menu_more.add_command(label="关于", command=self.about_window)
        top_menu.add_command(label="设置", command=self.open_settings)  # 添加设置按钮
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
        if self.is_admin():
            # 显示同步动画
            self.show_sync_animation()
            threading.Thread(target=self.sync_time_task).start()
        else:
            messagebox.showwarning("权限不足", "同步时间需要管理员权限。请以管理员身份运行程序。")

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def sync_time_task(self):
        try:
            if not self.primary_ntp_server:
                self.root.after(0, lambda: messagebox.showerror("错误", "没有可用的NTP服务器。"))
                return

            c = ntplib.NTPClient()
            try:
                response = c.request(self.primary_ntp_server, timeout=5)
            except Exception:
                self.root.after(0, lambda: messagebox.showerror("错误", f"无法连接到NTP服务器: {self.primary_ntp_server}"))
                return

            if response:
                current_time = response.tx_time
                dt = datetime.datetime.fromtimestamp(current_time)
                _date = dt.strftime("%Y-%m-%d")
                _time = dt.strftime("%H:%M:%S")
                print("系统当前时间", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                print("北京标准时间", _date, _time)
                a, b, c_sec = _time.split(':')
                c_sec = float(c_sec) + 0.5
                _time = f"{a}:{b}:{c_sec:.1f}"
                try:
                    os.system(f'date { _date } && time { _time }')
                    str1 = f"同步后时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    self.root.after(0, lambda: messagebox.showinfo("成功同步", str1))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showwarning("失败", f"时间同步失败: {e}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "无法连接到任何NTP服务器。"))
        except Exception as ex:
            self.root.after(0, lambda: messagebox.showerror("错误", f"发生异常: {ex}"))
        finally:
            # 隐藏同步动画
            self.hide_sync_animation()

    def CheckVersion(self):
        # 创建并显示加载动画窗口
        loading_window = tk.Toplevel(self.root)
        self.set_window_icon(loading_window)  # 设置图标
        loading_window.title("检查更新")
        loading_window.resizable(False, False)
        x_pos = int((self.screenwidth - 400) / 2)
        y_pos = int((self.screenheight - 250) / 2)
        size_geo = f'400x250+{x_pos}+{y_pos}'
        loading_window.geometry(size_geo)
        
        # 显示加载动画
        loading_label = tk.Label(loading_window, text="正在检查更新，请稍候...", font=("", 12))
        loading_label.pack(pady=10)

        progress = ttk.Progressbar(loading_window, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)

        # 启动线程进行版本检查
        threading.Thread(target=self.check_version_task, args=(loading_window, progress, loading_label)).start()

    def check_version_task(self, loading_window, progress, loading_label):
        try:
            response = requests.get(self.update_api)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('version')
                update_url = data.get('updateUrl')
                announcement = data.get('announcement', '')

                if self.version == latest_version:
                    self.root.after(0, lambda: self.show_message(
                        loading_window,
                        progress,
                        "你已经是最新版。",
                        "info",
                        announcement
                    ))
                elif self.compare_versions(self.version, latest_version) < 0:
                    self.root.after(0, lambda: self.show_update_options(
                        loading_window,
                        progress,
                        "你的版本已经落后了，是否更新？",
                        update_url,
                        announcement
                    ))
                else:
                    self.root.after(0, lambda: self.show_message(
                        loading_window,
                        progress,
                        "当前版本高于最新版本。",
                        "warning",
                        announcement
                    ))
            else:
                raise Exception(f"API请求失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            error_message = f"网络请求失败: {e}"
            self.root.after(0, lambda: self.show_error_message(loading_window, progress, loading_label, error_message))
        except Exception as ex:
            error_message = f"发生异常: {ex}"
            self.root.after(0, lambda: self.show_error_message(loading_window, progress, loading_label, error_message))

    def show_error_message(self, loading_window, progress, loading_label, error_message):
        # 停止并销毁进度条和加载标签
        progress.stop()
        progress.destroy()
        loading_label.destroy()

        # 显示错误信息
        error_label = tk.Label(loading_window, text="检查更新失败", font=("", 14, "bold"), fg="red")
        error_label.pack(pady=10)

        error_details = tk.Text(loading_window, wrap=tk.WORD, height=5, width=40)
        error_details.insert(tk.END, error_message)
        error_details.config(state=tk.DISABLED)
        error_details.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # 添加关闭按钮
        tk.Button(loading_window, text="关闭", command=loading_window.destroy).pack(pady=10)

    def show_message(self, loading_window, progress, message, msg_type, announcement):
        # 这里假设 show_message 仅在检查更新时使用，因此 reset_ntp_servers 不需要调用它
        # 停止并销毁进度条
        if progress:
            progress.stop()
            progress.destroy()

        # 更新加载窗口内容
        for widget in loading_window.winfo_children():
            widget.destroy()

        msg_color = {"info": "green", "error": "red", "warning": "orange"}
        tk.Label(loading_window, text=message, font=("", 12), fg=msg_color.get(msg_type, "black")).pack(pady=10)

        if announcement:
            announcement_frame = tk.Frame(loading_window)
            announcement_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
            
            announcement_label = tk.Label(announcement_frame, text="更新公告:", font=("", 10, "bold"))
            announcement_label.pack(anchor="w")
            
            announcement_text = tk.Text(announcement_frame, wrap=tk.WORD, height=5, width=40)
            announcement_text.insert(tk.END, announcement)
            announcement_text.config(state=tk.DISABLED)
            announcement_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(loading_window, text="关闭", command=loading_window.destroy).pack(pady=10)

    def show_update_options(self, loading_window, progress, message, update_url, announcement):
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
            
            announcement_label = tk.Label(announcement_frame, text="更新公告:", font=("", 10, "bold"))
            announcement_label.pack(anchor="w")
            
            announcement_text = tk.Text(announcement_frame, wrap=tk.WORD, height=5, width=40)
            announcement_text.insert(tk.END, announcement)
            announcement_text.config(state=tk.DISABLED)
            announcement_text.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(loading_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="更新", command=lambda: self.update(update_url)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=loading_window.destroy).pack(side=tk.LEFT, padx=5)

    def update(self, update_url):
        webbrowser.open(update_url)

    def about_window(self):
        if hasattr(self, 'about_window_instance') and self.about_window_instance and self.about_window_instance.winfo_exists():
            self.about_window_instance.lift()
            return

        self.about_window_instance = tk.Toplevel(self.root)
        self.set_window_icon(self.about_window_instance)
        self.about_window_instance.title("关于")
        # 将位置坐标转换为整数
        x_pos = int((self.screenwidth - 370) / 2)
        y_pos = int((self.screenheight - 230) / 2)
        size_about = f'{370}x{230}+{x_pos}+{y_pos}'
        self.about_window_instance.geometry(size_about)
        self.about_window_instance.resizable(False, False)

        # 显示加载动画
        loading_label = tk.Label(self.about_window_instance, text="正在加载关于信息，请稍候...", font=("", 12))
        loading_label.pack(pady=10)

        progress = ttk.Progressbar(self.about_window_instance, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)

        # 启动线程加载关于信息
        threading.Thread(target=self.load_about_content, args=(loading_label, progress)).start()

    def load_about_content(self, loading_label, progress):
        default_about_content = (
            "远程公告加载失败，这是默认内容\n"
            "感谢使用此软件！\n"
            "QQ：2147606879 \n"
            "博客地址：especial.top\n"
            "github仓库：https://github.com/canfengplaeir/synctime\n"
            "gitee仓库：https://gitee.com/canfeng_plaeir/synctime"
        )
        try:
            response = requests.get(self.about_api, timeout=5)
            if response.status_code == 200:
                data = response.json()
                about_content = data.get('aboutContent', default_about_content)
            else:
                about_content = default_about_content
        except Exception as e:
            print(f"加载关于信息失败: {e}")
            about_content = default_about_content

        # 更新关于窗口内容
        self.root.after(0, lambda: self.display_about_content(loading_label, progress, about_content))

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
        if hasattr(self, 'icon_image'):
            window.iconphoto(False, self.icon_image)

    def show_sync_animation(self):
        # 创建同步动画窗口
        self.sync_window = tk.Toplevel(self.root)
        self.set_window_icon(self.sync_window)
        self.sync_window.title("同步时间")
        self.sync_window.resizable(False, False)
        x_pos = int((self.screenwidth - 300) / 2)
        y_pos = int((self.screenheight - 100) / 2)
        size_geo = f'300x100+{x_pos}+{y_pos}'
        self.sync_window.geometry(size_geo)
        self.sync_window.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁用关闭按钮

        tk.Label(self.sync_window, text="正在同步时间，请稍候...", font=("", 12)).pack(pady=10)
        progress = ttk.Progressbar(self.sync_window, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start(10)
        self.sync_progress = progress

    def hide_sync_animation(self):
        if hasattr(self, 'sync_window'):
            self.sync_progress.stop()
            self.sync_window.destroy()

    def compare_versions(self, version1, version2):
        """
        比较两个版本号字符串
        """
        v1 = list(map(int, version1.split('.')))
        v2 = list(map(int, version2.split('.')))
        return (v1 > v2) - (v1 < v2)

    def load_ntp_servers(self):
        try:
            with open(self.ntp_servers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.ntp_servers = data.get('ntp_servers', [])
        except FileNotFoundError:
            print("ntp_servers.json文件未找到，使用默认NTP服务器列表。")
            self.ntp_servers = [
                'edu.ntp.org.cn', 
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
                'tw.ntp.org.cn', 
                'us.ntp.org.cn', 
                'cn.pool.ntp.org', 
                'jp.ntp.org.cn'
            ]
            self.save_ntp_servers()

    def save_ntp_servers(self):
        try:
            with open(self.ntp_servers_file, 'w', encoding='utf-8') as f:
                json.dump({"ntp_servers": self.ntp_servers}, f, ensure_ascii=False, indent=4)
            print("NTP服务器列表已保存。")
        except Exception as e:
            print(f"保存NTP服务器列表失败: {e}")

    def reset_ntp_servers(self):
        self.ntp_servers = [
            'edu.ntp.org.cn', 
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
            'tw.ntp.org.cn', 
            'us.ntp.org.cn', 
            'cn.pool.ntp.org', 
            'jp.ntp.org.cn'
        ]
        self.save_ntp_servers()
        self.ntp_tree.delete(*self.ntp_tree.get_children())
        for server in self.ntp_servers:
            self.ntp_tree.insert("", tk.END, values=(server, "待测"))
        messagebox.showinfo("重置成功", "已重置NTP服务器列表为默认值。", parent=self.settings_window_instance)

    def open_settings(self):
        if hasattr(self, 'settings_window_instance') and self.settings_window_instance and self.settings_window_instance.winfo_exists():
            self.settings_window_instance.lift()
            return

        self.settings_window_instance = tk.Toplevel(self.root)
        self.set_window_icon(self.settings_window_instance)
        self.settings_window_instance.title("设置")
        self.settings_window_instance.resizable(False, False)
        size_geo = f'500x500+{int((self.screenwidth - 500) / 2)}+{int((self.screenheight - 500) / 2)}'
        self.settings_window_instance.geometry(size_geo)

        # NTP服务器列表框使用Treeview
        ntp_frame = tk.Frame(self.settings_window_instance)
        ntp_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        tk.Label(ntp_frame, text="NTP服务器列表:", font=("", 12, "bold")).pack(anchor="w")

        columns = ("服务器地址", "延迟(ms)")
        self.ntp_tree = ttk.Treeview(ntp_frame, columns=columns, show='headings')
        for col in columns:
            self.ntp_tree.heading(col, text=col)
            self.ntp_tree.column(col, width=200, anchor='center')
        self.ntp_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        for server in self.ntp_servers:
            self.ntp_tree.insert("", tk.END, values=(server, "待测"))

        # 按钮框
        button_frame = tk.Frame(self.settings_window_instance)
        button_frame.pack(pady=10)

        add_button = tk.Button(button_frame, text="添加服务器", command=lambda: self.add_ntp_server(self.settings_window_instance))
        delete_button = tk.Button(button_frame, text="删除选中", command=self.delete_selected_ntp_server)
        reset_button = tk.Button(button_frame, text="重置为默认", command=self.reset_ntp_servers)

        add_button.pack(side=tk.LEFT, padx=5)
        delete_button.pack(side=tk.LEFT, padx=5)
        reset_button.pack(side=tk.LEFT, padx=5)

        # Ping按钮
        ping_button = tk.Button(self.settings_window_instance, text="Ping所有服务器", command=self.ping_all_ntp_servers)
        ping_button.pack(pady=5)

    def add_ntp_server(self, parent_window):
        def save_new_server():
            new_server = entry.get().strip()
            if new_server and new_server not in self.ntp_servers:
                self.ntp_servers.append(new_server)
                self.save_ntp_servers()
                self.ntp_tree.insert("", tk.END, values=(new_server, "待测"))
                add_window.destroy()
            else:
                messagebox.showwarning("无效输入", "请输入有效且未存在的NTP服务器地址。", parent=add_window)

        add_window = tk.Toplevel(parent_window)
        self.set_window_icon(add_window)
        add_window.title("添加NTP服务器")
        add_window.resizable(False, False)

        # 获取屏幕尺寸
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        window_width = 300
        window_height = 150
        x_pos = int((screen_width - window_width) / 2)
        y_pos = int((screen_height - window_height) / 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

        tk.Label(add_window, text="服务器地址:", font=("", 12)).pack(pady=10)
        entry = tk.Entry(add_window, width=40)
        entry.pack(pady=5)
        tk.Button(add_window, text="添加", command=save_new_server).pack(pady=10)

    def delete_selected_ntp_server(self):
        selected = self.ntp_tree.selection()
        if selected:
            item = selected[0]
            server = self.ntp_tree.item(item, 'values')[0]
            confirm = messagebox.askyesno("确认删除", f"是否删除NTP服务器: {server}?", parent=self.settings_window_instance)
            if confirm:
                self.ntp_tree.delete(item)
                index = self.ntp_servers.index(server)
                self.ntp_servers.pop(index)
                self.save_ntp_servers()
                if server == self.primary_ntp_server:
                    self.primary_ntp_server = self.ntp_servers[0] if self.ntp_servers else None
        else:
            messagebox.showwarning("未选择", "请先选择要删除的NTP服务器。", parent=self.settings_window_instance)

    def ping_all_ntp_servers(self):
        threading.Thread(target=self.ping_ntp_servers_task).start()

    def ping_ntp_servers_task(self):
        try:
            system_platform = platform.system().lower()
            logging.debug(f"当前操作系统: {system_platform}")
            if system_platform == "windows":
                ping_cmd = ["ping", "-n", "1", "{server}"]
            else:
                ping_cmd = ["ping", "-c", "1", "{server}"]

            ping_results = {}
            for server in self.ntp_servers:
                logging.debug(f"开始Ping服务器: {server}")
                try:
                    # 构建正确的ping命令
                    cmd = ping_cmd[:]
                    cmd[-1] = cmd[-1].format(server=server)
                    
                    logging.debug(f"执行命令: {' '.join(cmd)}")
                    response = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=3
                    )
                    logging.debug(f"Ping命令输出 for {server}:\n{response.stdout}")
                    latency = self.parse_ping_latency(response.stdout, system_platform)
                    logging.debug(f"解析后的延迟 for {server}: {latency} ms")
                    if latency is not None:
                        ping_results[server] = latency
                        # 更新Treeview中的延迟
                        for item in self.ntp_tree.get_children():
                            if self.ntp_tree.item(item, 'values')[0] == server:
                                self.ntp_tree.item(item, values=(server, f"{latency} ms"))
                                logging.debug(f"Treeview 中已更新服务器 {server} 的延迟为 {latency} ms")
                                break
                except Exception as e:
                    logging.error(f"Ping {server} 失败: {e}")

            logging.debug(f"Ping结果: {ping_results}")
            if ping_results:
                # 找到延迟最低的服务器
                best_server = min(ping_results, key=ping_results.get)
                self.primary_ntp_server = best_server
                message = "Ping结果：\n" + "\n".join([f"{s}: {ms} ms" for s, ms in ping_results.items()]) + f"\n\n优选服务器设置为: {best_server}"
                logging.debug(f"最佳服务器: {best_server}")
                self.root.after(0, lambda: messagebox.showinfo("Ping结果", message, parent=self.settings_window_instance))
            else:
                logging.warning("无法Ping任何NTP服务器。")
                self.root.after(0, lambda: messagebox.showerror("错误", "无法Ping任何NTP服务器。", parent=self.settings_window_instance))
        except Exception as ex:
            error_message = f"发生异常: {ex}"
            logging.error(error_message)
            self.root.after(0, lambda: self.show_error_message(self.settings_window_instance, None, None, error_message))

    def parse_ping_latency(self, ping_response, platform_system):
        import re
        logging.debug(f"解析Ping响应: {ping_response}")
        if platform_system == "windows":
            match = re.search(r"时间[=<]\s*(\d+)ms", ping_response)
        else:
            match = re.search(r"time[=<]\s*(\d+\.\d+) ms", ping_response)
        if match:
            latency = float(match.group(1))
            logging.debug(f"匹配到延迟: {latency} ms")
            return latency
        logging.warning("未能解析到延迟。")
        return None

if __name__ == "__main__":
    root_window = ttk.Window(themename="litera")
    app = SyncTimeApp(root_window)
    root_window.mainloop()