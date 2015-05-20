# -*- coding: utf-8 -*-
#!/usr/bin/env python
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

import time
import os
import json
import codecs
import random
import redis
import sys
import urllib2



import logging
logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)


def connectRedis():
    try:
        rdb = redis.Redis(host='127.0.0.1', port=6379, db=2)
        if rdb.ping() :
            return rdb
    except redis.exceptions.ConnectionError:
        print("can't connect to Redis,strating it...")
        #os.system('c:\\apps\\redis\\redis-server.exe')
        #time.sleep(1)

def processCommentGroup(ele):

    #get comment GUID
    #guid=ele.get_attribute('data-guid')
    guid=get_attribute(ele,'data-guid')
    if (guid is None):
        return None,None
    #get comment text   
    comment=getElementByXPathWithTimeout(ele,".//div[@class='p-comment']").text    
    
    #get star
    hasStar=False
    starNo=0

    
    for i in range(1,6)[::-1]:
        try:
            classFilter=".//div[@class='grade-star g-star%i']" %(i)
            star= ele.find_elements_by_xpath(classFilter)
            if star is not None:
                hasStar=True
                starNo=i
                break

        except NoSuchElementException:
            pass
    if hasStar==False:
        logging.debug("Can't get Star from comment,guid=%s,text=%s" %(guid,comment) )
 

    return guid,{"comment":comment, "star":starNo}

def gotoNextPage(browser):    
    #nextPage=browser.find_element_by_xpath("//a[@class='ui-pager-next']")
    i=0
    while tryGotoNextPage(browser)==False:
        i=i+1
        print 'looks get struck when changing page to the  next, try again'
        if i>20:
            sys.exit(0)
    return True    
    
def tryGotoNextPage(browser):
    try:    
        nextPage=getElementByXPathWithTimeout(browser,"//a[@class='ui-pager-next']")    
        nextPage.send_keys(Keys.ENTER) 
        return True
    except:
        print 'Timeout when change page...'
        time.sleep(1)
        return False

#main 
def get_attribute(ele, attr):
    
    attrText=''    

    try:
        attrText=ele.get_attribute(attr)
    except StaleElementReferenceException:
        logging.debug("Element get staled when fetching its attribute")
        attrText=None
        
    return attrText

def getElementsByXPathWithTimeout(driver,xpath,timeout=60):
     wait=WebDriverWait(driver,timeout)
     wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
     return driver.find_elements_by_xpath(xpath)

def getElementByXPathWithTimeout(driver,xpath,timeout=60):
     wait=WebDriverWait(driver,timeout)
     wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
     return driver.find_element_by_xpath(xpath)


#main 
     
def main1():

    rdb= connectRedis()
    
    if (rdb is None):
        print "Please start Redis first"
        #exit()
    
    url="http://item.jd.com/1217499.html#comment"
    browser=webdriver.Ie()
    #browser=webdriver.Chrome()    
    browser.get(url)
    
    url_lastPage=url+'_lastpage'
    
    lastPage=int(rdb.get(url_lastPage))
    
    
    print 'skip first %d pages....' %lastPage
    
    for i in range(lastPage):
        result=gotoNextPage(browser)     
        waitSec=random.uniform(1,2)
        time.sleep(waitSec)   
    
    print 'resume processing from page %d...' %lastPage
    for i in range(lastPage, lastPage+100):
        
        #comments=browser.find_elements_by_xpath("//div[@class='comments-item']")
        comments=getElementsByXPathWithTimeout(browser,"//div[@class='comments-item']")
        #import IPython;IPython.embed()
        print 'process Page ',i
         
        #allComments.extend(comments)
        
        for c in comments:
            guid,item=processCommentGroup(c)  
            if (guid is not None): 
                text=json.dumps(item, ensure_ascii=False)
                rdb.set(guid, text)
            else:
                print "get a error when processing page ",i
            #goto the next page    
                
        #update update into config 
        rdb.set(url_lastPage,i)
        
        gotoNextPage(browser)
        waitSec=random.uniform(2,5)
        time.sleep(waitSec)   
    
    #with codecs.open("iphone_comments.txt", "w",encoding='utf8') as f:
    #    json.dump(allComments,f,ensure_ascii=False)
    
    #for c in allComments:
    #    print c.encode('gb18030')
def fetch_url(url,ref_url):
    
    
    req=urllib2.Request(url)
    req.add_header('Referer',ref_url)
    req.add_header('Accept','*/*')
    
    resp=urllib2.urlopen(req,'')
    lines=resp.readlines()
    line=''
    for l in lines:
        line=line+l

    #json.loads(lines)    
    return line
    
def processCommentLine(line):
    comments=[]
    uline=unicode(line, encoding='gbk',errors='ignore')
    obj=json.loads(uline)
    if (obj is None) :
        print 'wrong line: %s' %uline
        return None
        
    if (obj['comments'] is None):
        print "can't find comments"
        return None
        
    for c in obj['comments']:
        guid=c['guid']
        content=c['content']
        score=c['score']
        t=c['creationTime']
        comments.append( {'guid':guid,'content':content,'score':score,'ctime':t} )
    
    return comments

def main2():
    rdb= connectRedis()    
    if (rdb is None):
        print "Please start Redis first"
        #exit()
    
    ref_url="http://item.jd.com/1217499.html#comment"
    #browser=webdriver.Ie()
    #browser=webdriver.Chrome()    
    #browser.get(ref_url)
    
    url_lastPage=ref_url+'_lastpage'
    
    lastPage=int(rdb.get(url_lastPage))

    print ('resume processing from page %d') %lastPage
    
    comment_page_url1='http://club.jd.com/productpage/p-1217499-s-0-t-0-p-%d.html'
    
    outf=open('comments.txt','w')
    
    for i in range(lastPage,lastPage+500):
        comment_page_url= comment_page_url1 %(i)
        waitSec=random.uniform(0.3,1)
        time.sleep(waitSec)         
        print 'fetch page %d'%i
        line=fetch_url(comment_page_url,ref_url)
        comments=processCommentLine(line)
        if (comments is not None):
            for c in comments:
                guid=c['guid']            
                text=json.dumps(c, ensure_ascii=False)
                rdb.set(guid, text)
            
        rdb.set(url_lastPage,i)
        #    print '%s,%s'%(c['content'],c['score'])
        #print line
        #outf.writelines(line+'\n')   
        #comments=processCommentLine(text)
        #print comments
    rdb.connection_pool.disconnect()
            

if __name__ == "__main__":
    main2()
