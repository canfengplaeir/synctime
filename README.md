# SyncTime - 时间同步工具

SyncTime是一个简单易用的时间同步工具,用于将您的计算机时间与NTP服务器同步。支持windows7 到 windows11.

## 主要特性

- 简洁的图形用户界面
- 支持多个NTP服务器
- 手动选择或自动推荐NTP服务器
- 自动检查更新
- 可自定义NTP服务器列表
- 支持Ping测试以选择最佳NTP服务器
- 可导出NTP服务器列表
- 支持从API更新NTP服务器列表

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
   - 手动选择主NTP服务器
   - 导出服务器列表到文本文件
   - 从API更新服务器列表

4. **NTP服务器优选**: 
   - 对所有NTP服务器进行Ping测试,显示延迟情况
   - 自动按延迟从小到大排序服务器列表
   - 可选择自动将延迟最低的服务器设为主服务器
   - 推荐延迟最低的服务器
   - 支持双击或按钮选择服务器为主服务器
   - 可自定义Ping超时时间

## 使用说明

1. 运行程序后,点击"时间同步"按钮即可同步时间。
2. 在"NTP服务器优选"中可以管理NTP服务器列表、进行Ping测试和选择主服务器。
3. "检查更新"功能可确保您使用的是最新版本。
4. 对于网络状况不佳的环境，可以调整Ping超时时间以提高成功率。
5. 点击"从API更新服务器列表"按钮可从在线API获取最新推荐的NTP服务器列表。

## 注意事项

- 同步时间需要管理员权限。
- 请确保您的网络连接正常,以便与NTP服务器通信。
- 选择延迟低的服务器可以提高同步精度。
- 在防火墙严格的环境中，可能需要添加防火墙例外以允许Ping和NTP请求。

## 开发环境

- Python 3.6+
- 依赖模块: pillow, ttkbootstrap, ntplib, requests
- 打包工具: PyInstaller

## 更新日志

### 版本 1.4.0
- 添加从API更新NTP服务器列表功能
- 优化服务器管理界面布局
- 增强用户交互体验

### 版本 1.3.0
- 优化NTP服务器优选界面
- 增加服务器列表交替行背景色
- 支持手动选择主NTP服务器
- 添加服务器列表导出功能
- 添加Ping超时时间设置

### 版本 1.2.0
- 更新版本号格式为x.x.x
- 增加关于页API功能
- 修复DPI适配问题

## 许可证

本项目采用MIT许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交问题报告和改进建议。如果您想为项目做出贡献,请随时提交Pull Request。

## 联系方式

- QQ: 2147606879
- 博客: [especial.top](https://especial.top)
- GitHub: [https://github.com/canfengplaeir/synctime](https://github.com/canfengplaeir/synctime)
- Gitee: [https://gitee.com/canfeng_plaeir/synctime](https://gitee.com/canfeng_plaeir/synctime)