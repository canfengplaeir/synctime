# -*- coding:utf-8 -*-
import tkinter as tk 

import os

import ntplib

import datetime

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

    print("同步后时间:", str(datetime.datetime.now())[:22])

version = 1

root_window = tk.Tk()
# 设置窗口title
root_window.title('时间自动同步工具')
# 设置窗口大小:宽x高,注,此处不能为 "*",必须使用 "x"
root_window.geometry('350x250')
# 更改左上角窗口的的icon图标
root_window.iconphoto(False, tk.PhotoImage(file='time.png'))
# 设置主窗口的背景颜色,颜色值可以是英文单词，或者颜色值的16进制数,除此之外还可以使用Tk内置的颜色常量
root_window["background"] = "#ffffff"
# 添加文本内,设置字体的前景色和背景色，和字体类型、大小 
text = tk.Label(root_window, text="时间自动同步", bg="white", fg="black" , font=("",20),width="30")

# 将文本内容放置在主窗口内
text.pack(pady="30")
# 添加按钮，以及按钮的文本，并通过command 参数设置关闭窗口的功能
button1 = tk.Button(root_window, text="时间同步", command=synctime)
button2 = tk.Button(root_window, text="关闭", command=root_window.quit)
button3 = tk.Button(root_window,text="更多")

# 将按钮放置在主窗口内
button2.pack(side="bottom")
button1.pack(side="bottom")
button3.pack(side="bottom")

# 进入主循环，显示主窗口
root_window.mainloop()