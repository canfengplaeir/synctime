# -*- coding:utf-8 -*-
from tkinter import *
from tkinter import messagebox
import os
import webbrowser
import ntplib
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
from ttkbootstrap import Style

# style = Style()
# style = Style(theme='sandstone')
# TOP6 = style.master


version = 1 #版本
updateweb = "baidu.com"
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

    os.system('date %s && time %s' % (_date, _time))

    str1 = "同步后时间:" + str(datetime.datetime.now())[:22]
    messagebox.showinfo("成功同步",str1)



def CheckVersion():
    
    website = "https://effulgent-blini-0290da.netlify.app/"
    soup = BeautifulSoup(urlopen(website), 'html.parser')
    Lastestver = int(soup.p.string)
    print(Lastestver)

    if version == Lastestver:
        messagebox.showinfo("检查更新","你已经是最新版")
    elif version < Lastestver:
        askback = messagebox.askquestion("检查更新","你的版本已经落后了，是否更新？")
        if askback == False:
            print(1) #不更新
            return 0
        else:
            print(2) #确认更新
            update()

def update():
    webbrowser.open(updateweb)


root_window = Tk()

root_window.title('时间自动同步工具')
root_window.geometry('350x250')
root_window["background"] = "#ffffff"
text = Label(root_window, text="时间自动同步", bg="white", fg="black" , font=("",20))
text.pack(pady="50")
button1 = Button(root_window, text="时间同步",width=30, command=synctime)
button2 = Button(root_window, text="关闭",width=30, command=root_window.quit)
button2.pack(side="bottom",pady=10)
button1.pack(side="bottom",pady=5)
#菜单栏
top = Menu(root_window)
menuMore = Menu(top)
top.add_cascade(label="更多",menu=menuMore)
menuMore.add_command(label="检查更新",command=CheckVersion)
root_window.config(menu = top)
root_window.mainloop()