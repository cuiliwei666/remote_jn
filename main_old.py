from util import SSH_Client
import time
import logging
import re
import csv
import os
from multiprocessing import Process
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(filename='logging.txt',level=logging.INFO)


def getfiledir():
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


def Cmd_Handler(host):
    # 查找esn号使用的，文件放在config_text下的cmd_info.txt文件下
    cmds_info = './config_text/cmd_info.txt'
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
        ssh_client.run(cmds_info)
        time.sleep(1)


def Cmd_Handler_2(host):
    cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
    with SSH_Client(host) as ssh_client:
        if ssh_client:
            ssh_client.run_2(cmds)
            time.sleep(1)

def License_Active_Handler(host,licenses):
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
        if ssh_client.isNotActive():
            ssh_client.license_active(licenses)
            time.sleep(1)


def Judge_Handler(host):
    cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
        ssh_client.judge_license()
        time.sleep(1)


def upload_Handler(host, licenses):
    cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
    cmds_info = './config_text/cmd_info.txt'
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
        ssh_client.ssh.send_config_set(['security-policy', 'default action permit', 'y'])
        ssh_client.upload_file(cmds_info, licenses)
        ssh_client.ssh.send_config_set(['security-policy', 'default action deny', 'y'])
        time.sleep(1)


def Cmd_Conf_Handler(host):
    cmds = 'config_text/conf_txt.txt'  # 存放执行命令文件，相对路径
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
        ssh_client.run_conf(cmds)
        time.sleep(1)


def main_func(host, licenses):
    cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
    cmds_info = './config_text/cmd_info.txt'
    ssh_client = SSH_Client(host)
    if ssh_client.login_host(host):
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
            ssh_client.upload_file(cmds_info, licenses)
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


def main():
    logging.warning('*' * 20 + ' start ' + '*' * 20)
    print('*' * 20 + ' start ' + '*' * 20)
    start = datetime.now()
    logging.warning(start)
    print(start)
    with open('hosts_list.txt', 'r') as hlp:
        with open('info.csv','w') as fp:
            writer = csv.writer(fp)
            lists = hlp.readlines()
            licenses = getfiledir()
            tasks_list = []
            for host in lists:
                # p = Process(target=Cmd_Conf_Handler, args=(host,))                # 更改配置使用
                # p = Process(target=upload_Handler, args=(host, licenses))           # 上传文件使用
                # p = Process(target=main_func, args=(host, licenses))              # 激活全流程
                # p = Process(target=Cmd_Handler, args=(host,))                       # 直接display使用,用于查看esn号
                p = Process(target=Judge_Handler, args=(host,))                     # 判断license是否激活
                # p = Process(target=Cmd_Handler_2, args=(host,))
                # p = Process(target=License_Active_Handler, args=(host,licenses))  # 当文件已经上传上去，只是需要激活时使用！
                p.start()
                tasks_list.append(p)
            

    for task_list in tasks_list:
        task_list.join()
    # logging.warning('共运行了 %s'%(time.ctime() - start))
    logging.warning('-' * 20 + ' end ' + '-' * 20)
    print('共运行了 %s秒'%(datetime.now() - start).seconds)
    print(time.ctime())
    print('-' * 20 + ' end ' + '-' * 20)

if __name__ == '__main__':
    main()
