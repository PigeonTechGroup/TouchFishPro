# TouchFishPro

机房摸鱼聊天工具（断公网可用）

原软件地址：[https://github.com/2044-space-elevator/TouchFish](https://github.com/2044-space-elevator/TouchFish)

此Pro版本为在原代码的基础上，使用AI对client代码进行重构，功能升级，未经完整测试，会有少许bug，[请在issues里提交](https://github.com/PigeonTechGroup/TouchFishPro/issues)

在client代码中，由于原版本占用版本号v1.1.?，所以client版本号为v1.2.0

在server代码中，由于直接使用原版本文件chat.py，只对其修改做到自动填入ip地址，不做任何版本号及内容的修改

> 以下内容摘自原README

该体系有两个软件：
- server    服务器端，聊天前，必须有一人的电脑作为 server，server 有且只有一台。其除了负责协调信息，什么也不做
- client    客户端，聊天者都使用 client 程序

**server 的使用**

server 需查询自己的内网 IP，打开 cmd，输入 ipconfig，找到“无线局域网适配器 WLAN:”中的“IPv4 地址”一项。自家的路由器应该是 "192.168.x.y"，学校的可能不一样。还有适配端口，适配端口通过 `netstat -an | findstr 要用的端口` 这一项命令来寻找，如果没有返回，就说明该端口空闲。

接着，查询到的 IP 地址复制，打开 server，粘贴自己的 IP，回车。之后要求你输入最大用户数，这个看你的聊天室有多少人（一定是正整数）。然后输入之前试出来的端口。将你的 IP 地址和端口分享给 Client 端的成员（一台机子在一个网内的 IP 是基本恒相等的，端口的空闲与否基本不会改变，分享一次就够了）。

**client 的使用**

Client 是窗口版的，IP 输入 server 的 ip, username 输入自己的昵称（聊天室里显示的就是 username），port 输入 server 的端口。输入在下面的文本框输入，点击确认/Ctrl+Enter就可以发送。
