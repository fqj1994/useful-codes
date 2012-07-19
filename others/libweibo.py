#!/usr/bin/env python
# coding: utf-8

import urllib2
import urllib
import cookielib
import re

class Weibo:
    def __init__(self, gsid, cookie, username, password, nickname):
        """
        构造函数，
        gsid參數爲gsid，字符串，未登錄可以是空串
        cookie参数为一个dict，是key => value
        username参数是一个str，为用户名
        password参数是一个str，为密码
        如果没有登录过，cookie可以为空字典
        """
        self.username = username
        self.password = password
        self.nickname = nickname
        self.gsid = gsid
        self.cookie = self._process_cookie_dict(cookie)


    def _process_cookie_dict(self, cookie):
        """
        将记录了cookie信息的字典化为请求中的字符串
        """
        tcookie = []
        for key in cookie:
            v = cookie[key]
            tcookie.append('%s=%s' % 
                    (urllib.quote_plus(key), 
                        urllib.quote_plus(v)))
        return '; '.join(tcookie)


    def _process_req(self, req):
        """
        处理request，添加cookie、ua等信息
        """
        req.add_header('Cookie', self.cookie)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19') #伪造User-Agent
        return req


    def login(self):
        """
        登录
        """
        req = urllib2.Request('http://weibo.cn/dpool/ttt/login.php')
        req = self._process_req(req)
        data = {'uname' : self.username, 'pwd': self.password,
                'l' : '', 'scookie' : 'on', 'submit' : '登录'}
        data = urllib.urlencode(data)
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        response = opener.open(req, data)
        cooks = {}
        for cook in cookie_jar:
            cooks[cook.name] = cook.value
        final_url = response.geturl()
        self.cookie = self._process_cookie_dict(cooks)
        self.gsid = final_url[final_url.find('=') + 1:]
        return self.isLoggedIn()

    def _get_weibo_homepage(self):
        req = urllib2.Request('http://weibo.cn/?gsid=' + self.gsid)
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        return m


    def isLoggedIn(self):
        try:
            m = self._get_weibo_homepage()
        except:
            return False
        if self.nickname in m:
            return True
        else:
            return False

    def publishTextStatus(self, content):
        try:
            if self.isLoggedIn() or self.login():
                homepage = self._get_weibo_homepage()
                m = re.search('<form action="(/mblog/sendmblog?[^"]*)" accept-charset="UTF-8" method="post">', homepage).group(1)
                data = {'rl' : '0', 'content' : content}
                data = urllib.urlencode(data)
                req = urllib2.Request('http://weibo.cn' + m + '&gsid=' + self.gsid)
                req = self._process_req(req)
                opener = urllib2.build_opener()
                response = opener.open(req, data, timeout = 10)
                t = response.read()
                if '<div class="ps">发布成功' in t:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
