module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    const version = "1.1.0";
    const announcement = `
# SyncTime 更新日志

版本 ${version}

新增功能

1. 日志记录系统
   - 引入 logging 模块，实现全面的日志记录功能
   - 在程序初始化时配置日志系统，记录重要操作和错误信息

2. NTP 服务器管理优化
   - 新增 NTP 服务器：
     - edu.ntp.org.cn
     - ntp.tencent.com
     - cn.pool.ntp.org
   - 实现 NTP 服务器列表的自动排序功能，基于 Ping 结果

3. Ping 测试功能
   - 新增 "Ping所有服务器" 按钮，可同时测试所有 NTP 服务器的延迟
   - 自动选择延迟最低的服务器作为主要 NTP 服务器

性能优化

1. 跨平台兼容性提升
   - 使用 subprocess 模块替代 os.system，提高跨平台兼容性
   - 根据不同操作系统（Windows/非Windows）动态调整 ping 命令参数

2. 错误处理与日志记录增强
   - 在关键操作中添加详细的错误处理和日志记录
   - 优化 Ping 操作的结果解析和错误处理逻辑

用户界面改进

1. 设置界面优化
   - 在设置窗口中添加 "Ping所有服务器" 按钮
   - 新增进度条显示，用于展示 Ping 操作的进度

2. NTP 服务器列表显示优化
   - 使用 Treeview 组件替代简单的列表，提供更好的视觉效果和交互体验

其他改进

1. 代码结构优化
   - 重构部分代码，提高可读性和可维护性
   - 增加辅助方法，如 parse_ping_latency 用于解析 ping 结果

2. 调试信息增强
   - 添加大量调试日志，记录 NTP 服务器的 ping 操作详情
   - 包括服务器名称、IP 地址、响应时间等关键信息

注意事项

- 程序版本号保持为 1.1.0
- 建议用户更新到最新版本以获得更好的使用体验和稳定性

    `.trim();

    res.status(200).json({
      version: version,
      updateUrl: "https://gitee.com/canfeng_plaeir/synctime",
      announcement: announcement
    });
  } else {
    res.status(405).json({ message: 'Method Not Allowed' });
  }
};