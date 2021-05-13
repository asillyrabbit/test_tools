# 测试工具平台
## 目标
让日常测试工作中频繁的（如更新环境）、麻烦的（如日报统计）等各种操作变得简单、高效。

## 实现思路
封装各种操作，以web平台统一管理，实现一键轻松完成。
![首页](https://github.com/asillyrabbit/temp/blob/main/%E9%A6%96%E9%A1%B5.PNG?raw=true)

## 主要技术
- 编程语言：python3.7
- 框架：Django==2.2.9
- 样式：django-bootstrap4==3.0.0

## 后台功能
管理各种配置信息。
#### 配置管理
- 环境信息：服务器、数据库...
- 命令信息：shell、python、redis...

## 前台功能
首页展示各操作入口，点击跳转到相应执行页面。

#### 执行页面示例
- __更新环境__：执行后，点击“状态”（成功/失败），查看更新日志。
![更新环境](https://github.com/asillyrabbit/temp/blob/main/%E6%9B%B4%E6%96%B0%E7%8E%AF%E5%A2%83.PNG?raw=true)

- __统计日报__：根据自定义报表样式，返回bug统计结果。
![统计日报](https://github.com/asillyrabbit/temp/blob/main/%E7%BB%9F%E8%AE%A1%E6%97%A5%E6%8A%A5.PNG?raw=true)

