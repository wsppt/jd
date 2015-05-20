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

import getCommentsByProduct

import logging
logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)


def connectRedis():
    try:
        rdb = redis.Redis(host='127.0.0.1', port=6379, db=1)
        if rdb.ping() :
            return rdb
    except redis.exceptions.ConnectionError:
        print("can't connect to Redis,strating it...")
        os.system('start c:\\apps\\redis\\redis-server.exe')
        time.sleep(10)
        rdb = redis.Redis(host='127.0.0.1', port=6379, db=1)
        return rdb


def processURLList(rdb):
    fp=open('urllist.txt','r')
    urllist=json.load(fp,encoding='utf8')
    for url in urllist:
        print url['id']
        print url['name'].encode('gbk')
        print str(url['count'])                
        getCommentsByProduct.getCommentsByProduct(url['id'],50,rdb)
        
    fp.close()


if __name__ == "__main__":
    rdb=connectRedis()
    i=0    
    while i < 100:
        try:
            time.sleep(1)
            processURLList(rdb)
            i=i+1
            rdb.save()
        except:
            print 'get a exception with i=%d' %i
            