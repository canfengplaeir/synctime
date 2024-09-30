# SyncTime - 时间同步工具

SyncTime是一个简单易用的时间同步工具,用于将您的计算机时间与NTP服务器同步。支持windows7 到 windows11.

## 主要特性

- 简洁的图形用户界面
- 支持多个NTP服务器
- 自动检查更新
- 可自定义NTP服务器列表
- 支持Ping测试以选择最佳NTP服务器

## 技术栈

- Python 3
- Tkinter (GUI)
- ttkbootstrap (美化界面)
- ntplib (NTP协议支持)
- requests (网络请求)
- PIL (图标处理)

## 主要功能

1. **时间同步**: 一键将系统时间与选定的NTP服务器同步。

2. **检查更新**: 自动检查是否有新版本可用,并提供更新选项。

3. **NTP服务器管理**: 
   - 查看当前NTP服务器列表
   - 添加新的NTP服务器
   - 删除现有NTP服务器
   - 重置为默认NTP服务器列表

4. **Ping测试**: 对所有NTP服务器进行Ping测试,自动选择延迟最低的服务器。

## 使用说明

1. 运行程序后,点击"时间同步"按钮即可同步时间。
2. 在"设置"中可以管理NTP服务器列表和进行Ping测试。
3. "检查更新"功能可确保您使用的是最新版本。

## 注意事项

- 同步时间需要管理员权限。
- 请确保您的网络连接正常,以便与NTP服务器通信。

## 许可证

本项目采用MIT许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交问题报告和改进建议。如果您想为项目做出贡献,请随时提交Pull Request。

## 联系方式

- QQ: 2147606879
- 博客: [especial.top](https://especial.top)
- GitHub: [https://github.com/canfengplaeir/synctime](https://github.com/canfengplaeir/synctime)
- Gitee: [https://gitee.com/canfeng_plaeir/synctime](https://gitee.com/canfeng_plaeir/synctime)