# Led控制
## 介绍
通过简单的命令对linux的LED进行控制，包括开灯和关灯。脚本通过Python实现

## 如何使用
1. 首先需要安装led工具包，在终端中输入以下命令：
    ```
    pip install led_ctl
    ```
2. 在终端中使用led命令 
   - 获取LED列表：
       ```
       led list
       ```
   - 获取LED状态：
       ```
       led get <led_name>
       ```
   - 设置LED状态（开灯或关灯）：
       ```
       led set <led_name> on|off
       ```
   - 通过Web控制LED：
       > 执行这个命令后会启动一个web服务器，默认为<http://IP:8082>，可以通过`--host`和`--port`参数指定端口和IP地址。
       ```
       led web [--host <host>] [--port <port>]
       ```
