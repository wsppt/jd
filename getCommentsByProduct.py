# -*- coding: utf-8 -*-
#!/usr/bin/env python
import time
import os
import json
import codecs
import random
import redis
import sys
import urllib2
import redis

def fetch_url(url,ref_url):
    
    
    req=urllib2.Request(url)
    req.add_header('Referer',ref_url)
    req.add_header('Accept','*/*')
    
    print 'start urlopen, page=%s' %url
    resp=urllib2.urlopen(req,'',timeout=5)
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

def getCommentsByProduct(pID,pageCount, rdb):
    
    ref_url="http://item.jd.com/%s.html#comment" %pID
    
    url_lastPage=ref_url+'_lastpage'
    
    lastPage=0
    if(rdb is not None):
        pageNo=rdb.hget(pID, 'lastPage')
        if( pageNo is not None):
            lastPage=int(pageNo)
       

    print 'resume processing from page %d' %lastPage
    
    comment_page_url1='http://club.jd.com/productpage/p-'+pID+'-s-0-t-0-p-%d.html'
    
    #for i in range(lastPage,lastPage+pageCount):
    i=lastPage
    while i< lastPage+pageCount:    
        try:
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
                    if (rdb is not None):                
                        rdb.hset(pID, guid, text)
                    else:
                        print 'guid=' + guid
                        print 'context=' + text.encode('gbk')
                
            if (rdb is not None):
                rdb.hset(pID,'lastPage',i)
            i=i+1
        except:
            print 'exception raised when process page %s' %comment_page_url 
            

if __name__ == "__main__":
    #'UT case    
    rdb=redis.Redis(db=1)
    getCommentsByProduct('981821',2, rdb)
