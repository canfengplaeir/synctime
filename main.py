# -*- coding:utf-8 -*-
from tkinter import *
from tkinter import messagebox
import os
import webbrowser
import ntplib
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
# from ttkbootstrap import Style




version = 1 #版本
updateweb = "https://gitee.com/canfeng_plaeir/synctime/releases"
def synctime():
    c = ntplib.NTPClient()
    hosts = ['edu.ntp.org.cn', 'tw.ntp.org.cn', 'us.ntp.org.cn', 'cn.pool.ntp.org', 'jp.ntp.org.cn']
    for host in hosts:
        try:
            response = c.request(host)
            if response:
                break
        except Exception as e:
            pass

    current_time = response.tx_time

    _date, _time = str(datetime.datetime.fromtimestamp(current_time))[:22].split(' ')

    print("系统当前时间", str(datetime.datetime.now())[:22])

    print("北京标准时间", _date, _time)

    a, b, c = _time.split(':')

    c = float(c) + 0.5

    _time = "%s:%s:%s" % (a, b, c)
    try:
        os.system('date %s && time %s' % (_date, _time))
    except:
        messagebox.showwarning("Failure!","时间同步失败，请检查是否使用了管理员管理员权限。")

    # os.system('date %s && time %s' % (_date, _time))

    str1 = "同步后时间:" + str(datetime.datetime.now())[:22]
    messagebox.showinfo("成功同步",str1)



def CheckVersion():
    
    website = "https://effulgent-blini-0290da.netlify.app/"
    def wangluo():
        try:
            soup = BeautifulSoup(urlopen(website), 'html.parser')
            Lastestver = int(soup.p.string)
            # print("最新版本为",Lastestver)
            
            return Lastestver
        except:
            messagebox.showerror("错误！","请检查是否联网！")
            return 0
    Lastestver = wangluo()
    print(Lastestver)
    if Lastestver != 0:
        if version == Lastestver:
            messagebox.showinfo("检查更新","你已经是最新版")
        elif version < Lastestver:
            askback = messagebox.askyesno("检查更新","你的版本已经落后了，是否更新？")
            if askback == False:
                print("No") #不更新
            else:
                print("Yes") #确认更新
                update()

def update():
    webbrowser.open(updateweb)

#关于
def about_window():
    about = Tk()
    about.title("关于")
    size_about = '%dx%d+%d+%d' % (300, 200, (screenwidth-300)/2, (screenheight-200)/2)
    about.geometry(size_about)
    # about.geometry("300x200")
    about.resizable(False,False)
    text_baout = Text(about,wrap=CHAR,font=("",14))
    text_baout.insert(INSERT,"感谢使用此软件！\n博客地址：   \ngithub仓库：https://github.com/canfengplaeir/synctime \ngitee仓库：https://gitee.com/canfeng_plaeir/synctime ")
    text_baout.pack()
    about.mainloop()

root_window = Tk()
# style = Style()
# style = Style(theme='sandstone')
# TOP6 = style.master
root_window.title('时间自动同步工具')
# root_window.geometry('350x250')
root_window["background"] = "#ffffff"
root_window.resizable(False,False)
screenwidth = root_window.winfo_screenwidth()
screenheight = root_window.winfo_screenheight()
size_geo = '%dx%d+%d+%d' % (350, 250, (screenwidth-350)/2, (screenheight-250)/2)
root_window.geometry(size_geo)
text = Label(root_window, text="时间自动同步", bg="white", fg="black" , font=("",20))
text.pack(pady="50")
button1 = Button(root_window, text="时间同步",width=30, command=synctime)
button2 = Button(root_window, text="关闭",width=30, command=root_window.quit)
button2.pack(side="bottom",pady=10)
button1.pack(side="bottom",pady=5)
#菜单栏
top = Menu(root_window,tearoff=False)
menuMore = Menu(top,tearoff=False)
top.add_cascade(label="更多",menu=menuMore)
menuMore.add_command(label="检查更新",command=CheckVersion)
menuMore.add_command(label="关于",command=about_window)
root_window.config(menu = top)
root_window.mainloop()