# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 15:48:51 2015

@author: u8000889
"""
import redis
import codecs
import json
import jieba

rdb = redis.Redis(db=1)
keys=rdb.keys()

fout=codecs.open("out.txt",encoding='utf8',mode='w')
#fout=open('out.txt',mode='w')
#fout1=open('words.txt',mode='w')
fout1=codecs.open("words.txt",encoding='utf8',mode='w')
for k in keys:
    print 'processing product %s' %k
    pKeys=rdb.hkeys(k)
    for pk in pKeys:
        if pk == 'lastPage':
            print 'skip control page'
            continue
        jtext=rdb.hget(k,pk)
        o=json.loads(jtext)

        text=o['content']
        
        fout.writelines(str(o['score'])+',')
        fout.write(text +'\n')
        
        line=','.join(jieba.cut(text))
        fout1.write(line)
        
fout.close()
fout1.close()

        
            
