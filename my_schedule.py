# -*- coding: utf-8 -*-

import sys
if sys.version >'3':
    import _thread as th
else:
    import thread as th

import platform
import datetime
import json
import time
import os

#用户的定时任务在这个文件中定义
class my_schedule(object):

    def __init__(self, marsiot):
        self.marsiot = marsiot

        if platform.uname()[1] == 'raspberrypi':
            #周期执行任务，第一个参数是任务睡眠的时间
            th.start_new_thread(self.beacon, (20,))

            #这里是读取温湿度的演示，仅供参考
            #th.start_new_thread(self.readtemp, (60,))

    #def __del__(self):

    def beacon(self, arg1):

        time.sleep(5)

        #线程不断的循环执行
        while True:

            res = os.popen('vcgencmd measure_temp').readline()
            cpu_temp = res.replace("temp=","").replace("'C\n","")

            res = os.popen('vcgencmd get_mem arm').readline()
            arm_mem = res.replace("arm=","").replace("M\n","")

            my_chart = {}

            y = []

            #Y轴坐标，目前支持两个序列，Y_0和Y_1
            y_0 = {}
            y_0['name'] = '温度(摄氏度)'
            y_0['value'] = cpu_temp
            y.append(y_0)

            y_1 = {}
            y_1['name'] = '使用内存(M)'
            y_1['value'] = arm_mem
            y.append(y_1)

            my_chart['y'] = y

            #X轴的坐标，这里是时间坐标
            now = datetime.datetime.now()
            my_time = time.strftime("%H:%M:%S", now.timetuple())
            my_chart['x'] = my_time 

            my_chart_json = json.dumps(my_chart)
            self.marsiot.send_message("mychart1", my_chart_json)
            print(my_chart_json)

            #睡眠一段时间后，再执行后面的程序，不断循环
            time.sleep(arg1)


    def readtemp(self, arg1):

        time.sleep(5)
        #线程不断的循环执行
        while True:

            res = os.popen(self.marsiot.fix_path + './tools/dht11/readtemp').readline()
            if not res.startswith('error'):
                rh_temp = res.split(' ',1)

                my_chart = {}

                y = []

                y_0 = {}
                y_0['name'] = '湿度'
                y_0['value'] = rh_temp[0] 
                y.append(y_0)

                y_1 = {}
                y_1['name'] = '温度'
                y_1['value'] = rh_temp[1]
                y.append(y_1)

                my_chart['y'] = y

                now = datetime.datetime.now()
                my_time = time.strftime("%H:%M:%S", now.timetuple())
                my_chart['x'] = my_time 

                my_chart_json = json.dumps(my_chart)
                self.marsiot.send_message("mychart1", my_chart_json)
                print(my_chart_json)

            #睡眠一段时间后，再执行后面的程序，不断循环
            time.sleep(arg1)




