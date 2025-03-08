const express = require('express');
const serverless = require('serverless-http');
const cors = require('cors');
const app = express();

// 启用 CORS
app.use(cors());

// 当前版本
const currentVersion = "1.4.0";

// 版本信息路由
app.get('/api/version', (req, res) => {
  const version = currentVersion;
  const announcement = `
# SyncTime 更新日志

版本 ${version}

## 新增功能

1. API集成
   1.1 新增从API更新NTP服务器列表功能
   1.2 优化服务器管理界面布局，增加第二行按钮区
   1.3 增强用户交互体验，添加进度显示和详细结果反馈

2. NTP服务器管理改进
   2.1 支持从在线API获取最新推荐的NTP服务器
   2.2 添加服务器描述显示
   2.3 优化服务器添加和更新流程

3. 修复
   3.1 修复某些情况下UI响应问题
   3.2 改进网络请求稳定性
   3.3 优化错误处理机制

4. 其他
   4.1 更新API接口文档
   4.2 提升整体性能表现
   4.3 改进用户引导信息
  `.trim();

  res.json({
    version: version,
    updateUrl: "https://gitee.com/canfeng_plaeir/synctime/releases",
    announcement: announcement
  });
});

// 服务器信息路由
app.get('/api/about', (req, res) => {
  const aboutContent = `感谢使用SyncTime时间同步工具！

当前版本: ${currentVersion}

主要功能:
- 一键同步系统时间
- NTP服务器优选与管理
- 自动检测网络延迟最低的服务器
- 从API更新NTP服务器列表

QQ群：2147606879
作者博客：especial.top
源代码仓库：
- GitHub: https://github.com/canfengplaeir/synctime
- Gitee: https://gitee.com/canfeng_plaeir/synctime

更多功能和帮助请查看软件内菜单。
如果您喜欢这个软件，请考虑给项目点一个Star！`;

  res.json({
    about_content: aboutContent
  });
});

// 添加一个新的NTP服务器推荐列表API
app.get('/api/ntp_servers', (req, res) => {
  // 推荐的NTP服务器列表
  const recommendedServers = [
    { server: "edu.ntp.org.cn", description: "中国教育网NTP服务器" },
    { server: "ntp.ntsc.ac.cn", description: "中国科学院NTP服务器" },
    { server: "cn.ntp.org.cn", description: "中国NTP服务器" },
    { server: "ntp1.aliyun.com", description: "阿里云NTP服务器1" },
    { server: "ntp2.aliyun.com", description: "阿里云NTP服务器2" },
    { server: "ntp3.aliyun.com", description: "阿里云NTP服务器3" },
    { server: "ntp4.aliyun.com", description: "阿里云NTP服务器4" },
    { server: "ntp5.aliyun.com", description: "阿里云NTP服务器5" },
    { server: "ntp6.aliyun.com", description: "阿里云NTP服务器6" },
    { server: "ntp7.aliyun.com", description: "阿里云NTP服务器7" },
    { server: "ntp.tencent.com", description: "腾讯NTP服务器" },
    { server: "tw.ntp.org.cn", description: "台湾NTP服务器" },
    { server: "us.ntp.org.cn", description: "美国NTP服务器" },
    { server: "cn.pool.ntp.org", description: "NTP公共服务器池(中国)" },
    { server: "jp.ntp.org.cn", description: "日本NTP服务器" }
  ];

  res.json({
    recommended_servers: recommendedServers,
    last_updated: new Date().toISOString()
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
