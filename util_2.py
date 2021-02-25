from util import SSH_Client
import time
import logging
import re
import csv
import os
from multiprocessing import Process
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class RunMethod(Process):
	def getfiledir(self):
		license_lists = os.listdir('/wei/tftp_server_folders')
		file_saves = []
		for i in license_lists:
			file_save = {}
			file_name = os.listdir('/wei/tftp_server_folders/%s'%i)
			file_save['sysname'] = i
			file_save['filename'] = file_name[0]
			file_saves.append(file_save)
			# print(file_save)
		return file_saves
	
	    
    def get_hosts(self):
		with open('hosts_list.txt', 'r') as hlp:
			self.lists = hlp.readlines()
			return self.lists
	
	
    def __init__(self):
		super().__init__()
        self.logger = logging.basicConfig(filename='logging.txt',level=logging.INFO)



	def run(self):
		self.licenses = self.getfiledir()
		self.hosts = self.get_hosts()
		for host in self.hosts:
			self.host = host
			# self.Cmd_Conf_Handler()            # 更改配置使用
            # self.upload_Handler()           # 上传文件使用
			# self.main_func()       # 激活全流程
            # self.Cmd_Handler()        # 直接display使用,用于查看esn号
            # self.Judge_Handler()        # 判断license是否激活
            # self.Cmd_Handler_2()
            # self.License_Active_Handler()  # 当文件已经上传上去，只是需要激活时使用！

			
			
			
			

    def Cmd_Handler(self):
        # 查找esn号使用的，文件放在config_text下的cmd_info.txt文件下
        cmds_info = './config_text/cmd_info.txt'
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            ssh_client.run(cmds_info)
            time.sleep(1)
    
    
    def Cmd_Handler_2(self):
        cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
        with SSH_Client(self.host) as ssh_client:
            if ssh_client:
                ssh_client.run_2(cmds)
                time.sleep(1)
    
    def License_Active_Handler(self):
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            if ssh_client.isNotActive():
                ssh_client.license_active(self.licenses)
                time.sleep(1)
    
    
    def Judge_Handler(self):
        cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            ssh_client.judge_license()
            time.sleep(1)
    
    
    def upload_Handler(self):
        cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
        cmds_info = './config_text/cmd_info.txt'
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            ssh_client.ssh.send_config_set(['security-policy', 'default action permit', 'y'])
            ssh_client.upload_file(cmds_info, self.licenses)
            ssh_client.ssh.send_config_set(['security-policy', 'default action deny', 'y'])
            time.sleep(1)
    
    
    def Cmd_Conf_Handler(self):
        cmds = 'config_text/conf_txt.txt'  # 存放执行命令文件，相对路径
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            ssh_client.run_conf(cmds)
            time.sleep(1)
    
    
    def main_func(self):
        cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
        cmds_info = './config_text/cmd_info.txt'
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            if ssh_client.isNotActive():
                try:
                    reply = ssh_client.ssh.send_config_set(
                        ['security-policy', 'rule name untrust-local', 'source-zone untrust', 'destination-zone local',
                         'action permit'])
                    logging.debug(reply)
                    print('@'* 20 + '开启默认策略成功！'+ '@'* 20)
                except Exception as e:
                    logging.error(ssh_client.host + '开启默认策略失败！！！')
                    print('开启默认策略：', e)
                    return
                ssh_client.upload_file(cmds_info, self.licenses)
                try:
                    reply = ssh_client.ssh.send_config_set(['security-policy', 'undo rule name untrust-local'])
                    print('@'* 20 + '关闭默认策略成功！'+ '@'* 20)
                    logging.debug(reply)
                except Exception as e:
                    print('关闭默认策略：', e)
                    logging.error(ssh_client.host + '关闭默认策略失败！！！')
                    return
                try:
                    if ssh_client.license_active(licenses):
                        print(ssh_client.host + 'license 激活成功！')
                        logging.info(ssh_client.host + 'license 激活成功！')
                    else:
                        print(ssh_client.host + 'license 激活失败！')
                        logging.info(ssh_client.host + 'license 激活失败！！')
                except Exception as e:
                    print(e)
                ssh_client.logout_host()
                time.sleep(1)
    
