#!/wei/python3
import time
import logging
from multiprocessing import Process
from datetime import datetime
from util import RunMethod
import sys


logging.basicConfig(filename='logging.txt',level=logging.INFO)


def main_1(choose):
    logging.warning('*' * 20 + ' start ' + '*' * 20)
    print('*' * 20 + ' start ' + '*' * 20)
    start = datetime.now()
    logging.warning(start)
    print(start)
    with open('hosts_list.txt', 'r') as hlp:
        lists = hlp.readlines()
        tasks_list = []
        for host in lists:    
            '''
                1、更改配置使用,在config_text/conf_txt.txt中，写入命令，执行连贯的动作要写在同一行，用','分隔，不需连贯的写在不同行
                2、上传文件使用
                3、激活全流程
                4、直接display使用,用于查看esn号
                5、判断license是否激活
                6、当文件已经上传上去，只是需要激活时使用！
                7、可以查看防火墙的配置，在cmd.txt文件中写入需要批量执行的命令
                8、把cmd.txt中的命令执行后保存到 /wei/save_files 下

            '''
            if host:
                host = host.strip().split('#')[0].strip()
                if host:
                    p = RunMethod(host,choose)
                    p.start()
                    tasks_list.append(p)
    for task in tasks_list:
        task.join()


    # logging.warning('共运行了 %s'%(time.ctime() - start))
    logging.warning('-' * 20 + ' end ' + '-' * 20)
    print('共运行了 %s秒'%(datetime.now() - start).seconds)
    print(time.ctime())
    print('-' * 20 + ' end ' + '-' * 20)




def main():
    a = '''
======================================================================
1、更改配置使用,在config_text/conf_txt.txt中，写入命令，执行连贯的动作要写在同一行，用','分隔，不需连贯的写在不同行
2、上传文件使用
3、激活全流程
4、直接display使用,用于查看esn号
5、判断license是否激活
6、当文件已经上传上去，只是需要激活时使用！
7、可以查看防火墙的配置，在cmd.txt文件中写入需要批量执行的命令
8、把cmd.txt中的命令执行后保存到 /wei/save_files 下
quit、退出
======================================================================

    '''
    while True:
        print(a)
        choose = input('请输入您的选择:')
        if choose == 'quit':
            break
        try:
            choose = int(choose)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print('您输入的有误，请重新输入！')
            continue
        main_1(choose)




if __name__ == '__main__':
    main()










