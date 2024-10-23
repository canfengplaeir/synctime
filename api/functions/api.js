const express = require('express');
const serverless = require('serverless-http');
const cors = require('cors');
const app = express();

// 启用 CORS
app.use(cors());

// 版本信息路由
app.get('/api/version', (req, res) => {
  const version = "1.2.0";
  const announcement = `
# SyncTime 更新日志

版本 ${version}

更新日志

版本 1.2.0

1. 改进
   1.1 将原"设置"菜单项改名为"NTP服务器优选"，提高了界面直观性
   1.2 优化了时间同步逻辑，提高了同步成功率

2. 修复
   2.1 修复了某些情况下NTP服务器连接失败时程序卡死的问题
   2.2 上个版本无法在windows7中使用，现已经解决该问题

3. 其他
   3.1 更新了依赖库版本
   3.2 优化了代码结构，提高了可维护性


  `.trim();

  res.json({
    version: version,
    updateUrl: "https://gitee.com/canfeng_plaeir/synctime",
    announcement: announcement
  });
});

// 服务器信息路由
app.get('/api/about', (req, res) => {
  res.json({
    about_content: "感谢使用此软件！\nQQ：2147606879 \n博客地址：especial.top\ngithub仓库：https://github.com/canfengplaeir/synctime\ngitee仓库：https://gitee.com/canfeng_plaeir/synctime"
  });
});

// 处理 404 错误
app.use((req, res) => {
  res.status(404).json({ message: 'Not Found' });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Internal Server Error' });
});

// 导出处理程序
module.exports.handler = serverless(app);
