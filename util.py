from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import NetMikoAuthenticationException
import time
import logging
import re
import csv
import os
from multiprocessing import Process
# from v1.my_devices import device_list as devices





# '定义类'
class SSH_Client():

    def __init__(self, host):
        self.host = host.strip('\n').strip()
        self.sign = 0

    def __enter__(self):
        try:
            if self.login_host(self.host):
                return self
        except ValueError:
            print(self.host + ' Secret 密码错误')
        except NetMikoTimeoutException:
            print(self.host + ' 连接不上设备,请检查网络是否正常通信')
        except NetMikoAuthenticationException:
            print(self.host + ' 登陆失败，用户名或密码错误')




        # if self.login_host(self.host):
        #     return self
        # else:
        #     raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_val)
            return
        if self.sign:
            self.ssh.disconnect()



    #'定义login_host函数，用于登陆设备'
    def login_host(self, host):
        try:
            # self.ssh = ConnectHandler(host=host, device_type='huawei', username='dhccadmin', password='Dhcc123!@#', port=36100)
            self.ssh = ConnectHandler(host=host, device_type='huawei', username='huawei', password='Jnjt@2020#')
            self.ssh.enable()
            self.sign = 1
            # reply = self.ssh.find_prompt()
            # print('>' * 10 + '成功登陆结果如下:' + '>' * 10 + '\n' + reply)
            return True
        except ValueError:
            logging.warning(host + ' Secret 密码错误')
            print(host + ' Secret 密码错误')
        except NetMikoTimeoutException:
            print(host + ' 连接不上设备,请检查网络是否正常通信')
            logging.warning(host + ' 连接不上设备,请检查网络是否正常通信')
        except NetMikoAuthenticationException:
            print(host + ' 登陆失败，用户名或密码错误')
            logging.warning(host + ' 登陆失败，用户名或密码错误')
        except IndexError:
            print(host + ' 登陆失败，出现未知索引异常，您可以登陆设备查看是否正常，或者重新执行！')
            logging.warning(host + ' 登陆失败，出现未知索引异常，您可以登陆设备查看是否正常，或者重新执行！')
        except Exception as e:
            print(host + ' 登陆失败，出现未知异常!!!')
            logging.warning(host + ' 登陆失败，出现未知异常！！！')

    def isNotActive(self):
        reply = ''.join(self.ssh.send_command('disp license').split('\n')[-2]).split(';')[0].split(':')[-1].strip()
        if reply == 'Disabled':
            return True
        elif reply == 'Enabled':
            logging.warning(self.host + 'license 以前就激活了')
            return False

    def judge_license(self):
        if self.isNotActive():
            print(self.host + '  license Not Active')
            logging.info(self.host + '  license Not Active')
        else:
            logging.info(self.host + '  license is Active')
            print(self.host + '  license is Active')

    def do_upload_file(self,cmds, licenses, info):
        reply_list = []
        result = {}
        # '读取文件，for语句循环执行命令'
        # with open(cmds) as cmd_obj:
        #     for cmd in cmd_obj:
        for license in licenses:
            # print('info:', info['sysname'], 'license:',license['sysname'])
            if info['sysname'] == license['sysname']:
                cmd = 'tftp 192.168.200.250 get {}/{}'.format(license['sysname'],license['filename'])
                reply = self.ssh.send_command(cmd)
                reply_list.append(reply)
                logging.warning('>' * 10 + cmd.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)
        # print(result)


    # '定义do_cmd函数,用于执行命令'
    def do_cmd_info(self,cmds):
        reply_list = []
        result = {}
        # '读取文件，for语句循环执行命令'
        with open(cmds) as cmd_obj:
            for cmd in cmd_obj:
                reply = self.ssh.send_command(cmd)
                # self.ssh.config_mode()
                # reply = self.ssh.send_config_set(cmd)
                reply_list.append(reply)
                time.sleep(2)
                logging.warning('>' * 10 + cmd.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)
            # print(reply_list[-1])
        sysname = re.findall(r'JN[-0-9a-zA-z]*',reply_list[0])[0]
        esn = reply_list[1][-12:]
        if len(sysname.split('-')) == 6:
            ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',reply_list[2])[0]
        else:
            ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',reply_list[3])[0]
        result['sysname'] = sysname
        result['esn'] = esn
        result['ip'] = ip
        with open('info.csv','a',newline='') as fp:
            writer = csv.writer(fp)
            writer.writerow([result['sysname'],result['esn'],result['ip']])
        print(result)
        return result


    # '定义do_cmd函数,用于执行命令'
    def do_cmd(self,cmds):
        # '读取文件，for语句循环执行命令'
        with open(cmds) as cmd_obj:
            results = []
            for cmd in cmd_obj:
                result = {}
                reply = self.ssh.send_command(cmd)
                time.sleep(2)
                result['command'] = cmd.rstrip()
                result['command_result'] = reply
                results.append(result)
                logging.warning('>' * 10 + cmd.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)
                print('>' * 10+self.host.strip()+'  ' + cmd.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)
            return self.host.strip(), results


    # '定义logout_host函数，关闭程序'
    def logout_host(self):
        self.ssh.disconnect()


    def upload_file(self, cmds, licenses):
        info = self.do_cmd_info(cmds)
        self.do_upload_file(cmds,licenses,info)



    def do_conf_cmd(self,cmds):
        reply_list = []
        with open(cmds) as cmd_obj:
            for cmd in cmd_obj:
                finally_cmd = cmd.split(',')
                # print(finally_cmd)
                reply = self.ssh.send_config_set(finally_cmd)
                reply_list.append(reply)
                time.sleep(2)
                logging.warning('>' * 10+self.host.strip()+'  ' + cmd.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)


    def run_2(self, cmds):
        result = self.do_cmd(cmds)
        self.logout_host()
        return result

    def run(self, cmds):
        self.do_cmd_info(cmds)
        self.logout_host()

    def run_conf(self,cmds):
        self.do_conf_cmd(cmds)
        self.logout_host()


    def license_active(self,licenses):
        sysname = re.findall(r'JN[-0-9a-zA-z]*', self.ssh.send_command('disp cu | include sysname'))[0]
        # print('我的名字是',sysname)
        for license in licenses:
            # print('license_name:',license['sysname'],'\n sysname:',sysname)
            if license['sysname'] == sysname:
                try:
                    # print('%'* 30,'我在这','%'* 30)
                    self.ssh.send_config_set('license active {}'.format(license['filename']))
                    if not self.isNotActive():
                        return True
                except:
                    logging.warning('激活过程出现问题，请登录设备', self.host, '查看状态！')
                    continue

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
    
        
    def __init__(self,host,num):
        super().__init__()
        self.host = host.strip('\n').strip()
        self.logger = logging.basicConfig(filename='logging.txt',level=logging.INFO)
        self.num = num


    def run(self):
        self.licenses = self.getfiledir()
        if self.num == 1:
            self.Cmd_Conf_Handler()            # 更改配置使用,在config_text/conf_txt.txt中，写入命令，执行连贯的动作要写在同一行，用                                                # ','分隔，不需连贯的写在不同行
        elif self.num == 2:
            self.upload_Handler()           # 上传文件使用
        elif self.num == 3:
            self.main_func()       # 激活全流程
        elif self.num == 4:
            self.Cmd_Handler()        # 直接display使用,用于查看esn号
        elif self.num == 5:
            self.Judge_Handler()        # 判断license是否激活
        elif self.num == 6:
            self.License_Active_Handler()  # 当文件已经上传上去，只是需要激活时使用！
        elif self.num == 7:
            self.Cmd_Handler_2()            # 可以查看防火墙的配置，在cmd.txt文件中写入需要批量执行的命令
        elif self.num == 8:
            self.Save_File()
        else:
            print('您输入的功能还未开发！') 
            
            

    def Display(self):
        ssh_client = SSH_Client(self.host)
        if ssh_client.login_host(self.host):
            command = input('请输入您的命令(仅限于查看)：')
            reply = ssh_client.ssh.send_command(command)
            logging.warning('>' * 10+self.host+'  ' + command.rstrip() + ' 命令执行结果如下:' + '>' * 10 + '\n' + reply)
            
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
                result = ssh_client.run_2(cmds)
                time.sleep(1)
                return result

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
            try:
                ssh_client.run_conf(cmds)
            except Exception as e:
                print(self.host,'出现错误！ ',e)
            time.sleep(1)

    def Save_File(self):
        result = self.Cmd_Handler_2()
        if result:
            file_path = '/wei/save_files/'
            date_now = time.strftime('%Y%m%d', time.localtime())
            file_path += date_now
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            file_path = os.path.join(file_path,result[0])
            # file_path += result[0]
            with open(file_path,'w') as fw:
                for i in result[-1]:
                    command = '>'* 20 + i['command'] + '>'* 20 +'\n'
                    fw.write(command)
                    fw.write(i['command_result']+'\n')
                #fw.write(result[-1])
                #print('+'* 70)
                #print('result:',result[-1])
                #print('type of result[-1]:',type(result[-1]))
                #print('+'* 70)




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

