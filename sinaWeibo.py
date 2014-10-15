#! /usr/bin/env python
# -*- coding: utf-8 -*-  
import urllib  
import urllib2  
import cookielib
import sys
import random
  
  
class WeiboSpider(object):  
    def __init__(self):   
        self.WEIBO_RAND_URL = 'http://login.weibo.cn/login/?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='  
        self.WEIBO_LOGIN_PREFIX = 'http://login.weibo.cn/login/?'  
        self.WEIBO_LOGIN_POSTFIX = '&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt=4&revalid=2&ns=1'  
        self.cookie = cookielib.CookieJar()  
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.errorMsg = ""
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'}
        self.uidList = []
    
    def get_uidList(self, html):
        beginPos = html.find('uidList" value="')
        tempString = html[beginPos+16:]
        endPos = tempString.find('"')
        tempString = tempString[:endPos]
        uidList = tempString.split(',')
        return uidList
  
    def Login(self):  
        request = urllib2.Request(self.WEIBO_RAND_URL, urllib.urlencode({}), self.headers)
        response = urllib2.urlopen(request)  
        page = response.read()  
  
  
        #get some random string from html  
        beginPos = page.index('rand=')  
        rand = page[beginPos + 5: beginPos + 15] 
        #maybe only 9 digits in rand, so check here   
        if rand.isdigit():  
            pass  
        else:  
            rand = rand[:9]  
        beginPos = page.index('"password" name="')  
        passwordrand = page[beginPos + 17: beginPos + 30]  
        beginPos = page.index('"vk" value="')  
        vk = page[beginPos + 12: beginPos + 32]  
  
  
        if len(vk) != 20 or not rand.isdigit() or len(passwordrand) != 13:  
            self.errorMsg += "Random strings from html were changed by Sina."
        
        login_account = ['hongkongliwen@hotmail.com', 'hongkongliwen@gmail.com', 'hongkongliwen1@gmail.com', 'hongkongliwen2@gmail.com', '503286605@qq.com']
        login_password = ['hklw0812','hklw0812','hklw0812', 'hklw0812', 'hklw0812']
        login_rand = random.randint(0, 3)
        
        postdata = urllib.urlencode({'mobile': login_account[login_rand],
                                     passwordrand: login_password[login_rand],
                                     'remember': 'on',  
                                     'backURL': 'http://weibo.cn/',  
                                     'backTitle': '新浪微博',  
                                     'vk': vk,  
                                     'submit': '登录',  
                                     'encoding': 'utf-8'})  
        try:  
            request = urllib2.Request(url = self.WEIBO_LOGIN_PREFIX + rand + self.WEIBO_LOGIN_POSTFIX,  
                                      data = postdata,  
                                      headers = self.headers)  
            response = self.opener.open(request)
            data = response.read()
        except Exception as e:  
            self.errorMsg += str(e)+"."
          
        #get a important cookie value from cookiejar  
        try:  
            beginPos = str(self.cookie).index('gsid_CTandWM')  
            endPos = str(self.cookie).index('for', beginPos)
            if beginPos >= endPos:
                self.errorMsg += "cookie was changed by sina"
            else:
                cookie_value = str(self.cookie)[beginPos: endPos]
                self.headers2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0','cookie': cookie_value}
        except Exception as e:
            self.errorMsg += str(e)+"."
         
        
                         
    def Fetch(self, url=None):  
        'Give a string of the url of you weibo homepage and return a dict'  
        if url == None:
            self.errorMsg += "No URL Given."
        else:  
            request = urllib2.Request(url=url,  
                                      data=urllib.urlencode({}),
                                      headers=self.headers2)
        
        try:  
            response = urllib2.urlopen(request)  
            data = response.read()  
            if data.find('>登录<') != -1:
                self.errorMsg += "Maybe Cookie changed by sina."
            else:
                beginPos = data.index('st=')
                st = data[beginPos+3:beginPos+7]
                beginPos = data.index('vt=')
                vt = data[beginPos+3:beginPos+4]
                if (len(st) != 0) and (len(vt) != 0):
                    request = urllib2.Request(url=url+'/follow', data=urllib.urlencode({'vt':vt,'st':st}), headers=self.headers2)
                    response = urllib2.urlopen(request)
                    data = response.read()
                    self.uidList += self.get_uidList(data)
                    page = 2
                    nextCheck = nextCheck = data.find('下页')
                    
                    while (nextCheck != -1 and page <= 20):
                        request = urllib2.Request(url=url+'/follow?', data=urllib.urlencode({'page':page,'vt':vt,'st':st}),headers=self.headers2)
                        response = urllib2.urlopen(request)
                        data = response.read()
                        self.uidList += self.get_uidList(data)
                        page += 1
                        nextCheck = data.find('下页')
                        
                    
        except Exception as e:  
            self.errorMsg += str(e)+"."
                    
        print self.errorMsg
        print self.uidList

                
sinaWeibo = WeiboSpider()
sinaWeibo.Login()
sinaWeibo.Fetch('http://weibo.cn/'+str(sys.argv[1]))