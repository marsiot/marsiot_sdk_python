# -*- coding: utf-8 -*-

#用户的命令尽量在这个文件中定义
class my_command(object):

    def __init__(self, marsiot):
        self.marsiot = marsiot

    #def __del__(self):

    def test(self, args):
        self.marsiot.send_message("message", args['cool'])


