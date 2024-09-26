module.exports = (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
    if (req.method === 'OPTIONS') {
      res.status(200).end();
      return;
    }
  
    if (req.method === 'GET') {
      res.status(200).json({
        about_content: "感谢使用此软件！\nQQ：2147606879 \n博客地址：especial.top\ngithub仓库：https://github.com/canfengplaeir/synctime\ngitee仓库：https://gitee.com/canfeng_plaeir/synctime"
      });
    } else {
      res.status(405).json({ message: 'Method Not Allowed' });
    }
  };