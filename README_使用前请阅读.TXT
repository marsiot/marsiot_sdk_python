
【常见问题】

. 第一次安装SDK需要从MarsIoT网站上下载安装脚本，如果直接从码云上下载会缺少配置文件marsiot.ini

. 复制安装脚本自动下载安装运行后，下一次启动可以从目录下运行./main.py直接启动程序

. 如果要使用最新的SDK，可以重新运行安装脚本，注意在这之前要把你旧的SDK目录换个名字，以免冲突

. 树莓派上自动运行可以看这个文章: http://www.marsiot.com/wiki/doku.php?id=pi-auto-run

. 为了保持代码结构的优雅，用户自己的命令尽量添加到文件my_command.py中


【常见错误】

. 运行后提示错误：No module named 'RPi' 

  这是因为树莓派上PYTHON3缺少了RPi.GPIO的库，安装一下即可：sudo apt-get -y install python3-rpi.gpio
