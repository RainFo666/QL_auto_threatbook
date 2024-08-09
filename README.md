# Auto_threatbook
***声明：本仓库所有脚本仅用于个人学习和测试，请勿滥用！***
## 功能
本项目为微步情报社区自动获取成长值脚本（不包括发帖、情报打标、被关注等获取方式），支持青龙面板定时运行。获取每日成长值主要包括：  
1.每日登录（10成长值）  
2.每日内容点赞（5成长值×10次上限=50成长值）  
3.每日关注（5成长值×3次上限=15成长值）  
每日共75成长值，不包括可能会有用户回关，被关注+10成长值/个
## 配置
项目根目录下`config.json`为配置文件，包括青龙面板IP和端口、微步社区相关接口（若接口后续有更新则修改配置文件即可）
## 使用
脚本有以下两种部署方式。
#### 1.青龙面板（推荐）
* 安装青龙面板，面板中安装`python`的`requests`依赖库。
* 导入项目文件，青龙面板的`脚本管理`中新建文件夹，文件夹中添加项目所有文件。
* 创建青龙面板应用，青龙面板的`系统设置` > `应用设`置 > `创建应用`，复制`Client ID`和`Client Secret`。
* 修改配置文件`config.json`，
```
"QL_SERVER_IP": "http://127.0.0.1",                      # 填入青龙面板的IP（默认应该是127.0.0.1，因为脚本和面板在同一台服务器上运行）
"QL_SERVER_PORT": "5700",                                # 填入青龙面板的端口号
"QL_APP_CLIENT_ID": "-E9z-XXXXXXX",                      # 填入青龙面板Client ID
"QL_APP_CLIENT_SECRET": "kiXXXXXXXXXXX-2pnXXXX-zX",      # 填入青龙面板Client Secret
```
* 添加环境变量，青龙面板的`环境变量` > `创建变量`，`名称`请务必填写`threatbook_cookie`（否则运行时找不到`cookies`），`值`请自行抓取（登录一次微步社区，`F12`后刷新页面复制请求头中`cookies`）。
* 添加定时任务，青龙面板的`定时任务` > `创建任务`，`命令/脚本`填写`task threatbook_auto/threatbook_auto.py`，`名称`和`定时规则`自行填写，`定时规则`可参考`0 30 * * *`。
* 运行任务查看`cookies`是否正确，是否正常运行每日任务。
#### 2.直接运行脚本
由于本项目目前基于青龙定时任务编写，所以脚本本身没有定时执行功能，需要定时执行功能，请自行完成，或使用`crontab`等工具定时执行。
* 修改`threatbook_auto.py`文件中`17`行（`ThreatbookAuto`类的`__init__`函数中）`self.COOKIE = self.get_threatbook_cookie()`为 -> `self.COOKIE = 'XXX'`，其中`'XXX'`替换为自行抓取到的`cookies`字符串。
* 运行脚本`python3 threatbook_auto.py`。
