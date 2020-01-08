#!/usr/bin/python2
# -*- coding: utf-8 -*-

import platform
import sys

from marsiot import marsiot

if __name__ == '__main__':
    try:
        fix_path = ''

        if len(sys.argv) > 1:
            #如果有这个参数，则作为固定的文件路径，可以从任何一个位置启动MarsIoT
            #例如添加如下到/etc/rc.local中可以完成开机启动MarsIoT
            #/home/pi/marsiot_sdk_python/main.py /home/pi/marsiot_sdk_python/ 2>&1 &
            #注意树莓派配置rasp-config中要配置成wait for network
            fix_path = sys.argv[1]

        marsiot = marsiot(fix_path)
        print("\nversion - %s\n"%marsiot.version())

        if marsiot.connect():
            #这里可以改为自己的模块名称
            marsiot.set_model_name('test')
            #这里可以改为自己的模块描述
            marsiot.set_model_description('test')

            marsiot.bind_command_processor('my_command')
            marsiot.bind_schedule_processor('my_schedule')
            marsiot.loop_wait_message()

    except IOError as e:
        print(e, "\ncan't find marsiot.ini in " + fix_path + ", pls from www.marsiot.com download and install the SDK");
    except Exception as e:
        print("\ncritical error", e)

