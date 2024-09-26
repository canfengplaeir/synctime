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
      version: "1.0.0",
      updateUrl: "https://gitee.com/canfeng_plaeir/synctime",
      announcement: "重置版"
    });
  } else {
    res.status(405).json({ message: 'Method Not Allowed' });
  }
};