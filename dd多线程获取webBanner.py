#coding=utf-8
#获取状态码、响应头部、页面标题
#获取banner信息，并写入txt

import requests
from bs4 import BeautifulSoup
import sys
import threading
import Queue

#获取banner，返回获取到的banner字符串
def banner(myurl='http://127.0.0.1'):
    result = ""
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}
    r = requests.get(myurl, headers=headers, timeout=3)
    r.encoding = 'utf-8'    #解决编码问题
    result = str(r.status_code) + ','     #状态码
    if 'X-Powered-By' in r.headers:     #头部banner
        result += str(r.headers['X-Powered-By']) + ','
    if 'Server' in r.headers:       #头部banner
        result += str(r.headers['Server']) + ','
    #获取页面标题，获取不到标题的话或报错，所以用try
    try:
        soup = BeautifulSoup(r.text, 'lxml')    #获取title
        title = soup.title.text + ','
        result += title
    except:
        result += 'NULL'
    return result

#加入子域名参数，请求80,443端口，返回80,443的banner信息
def toRst(subdomain='127.0.0.1'):
    response = ''
    try:
        result = banner('http://' + subdomain)
    except:
        result = 'down'
    try:
        result1 = banner('https://' +subdomain)
    except:
        result1 = 'down'

    response = '80,' + result
    response += '\t443,' + result1
    return response

#q队列参数，线程id，线程获取锁，从队列中拿出子域名去请求，放回bannner信息，写入f2文件，并输出显示
def process_run(q, threadID):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            subd = q.get()
            info = toRst(subdomain=subd)
            queueLock.release()
            f2.write(subd + '\t' + info + '\n')
            print 'Thread-' + str(threadID) + ':  ' + subd + '\t' + info
        else:
            queueLock.release()

#线程函数，开启线程，主要为了执行 process_run()函数
class myThread(threading.Thread):
    def __init__(self, threadID, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.q = q

    def run(self):
        print "Starting Thread-%s" % self.threadID
        process_run(self.q, self.threadID)
        print "Exiting Thread-%s" % self.threadID

#主函数
if __name__ == '__main__':
    reload(sys)     #解决页面编码问题
    sys.setdefaultencoding( "utf-8" )   #解决页面编码问题
    f = open('test.txt', 'r')           #要跑的子域名txt
    f2 = open('result.txt', 'w')        #结果txt
    d = f.readlines()
    queueLock = threading.Lock()
    workQueue = Queue.Queue()
    exitFlag = 0
    threadNum = 10  #启用的线程数
    threads = []

    #填充子域名队列
    for i in d:
        res1 = i.strip('\n')
        workQueue.put(res1)
    #创建线程
    for i in range(threadNum):
        thread = myThread(i, workQueue)
        thread.start()
        threads.append(thread)

    #等待线程跑完队列
    while not workQueue.empty():
        pass

    exitFlag = 1

    #等待所有线程的完成
    for t in threads:
        t.join()

    print "Exiting Main Thread"
