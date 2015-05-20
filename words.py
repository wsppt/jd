# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 15:48:51 2015

@author: u8000889
"""

import codecs
import jieba



fin=codecs.open("out\out.txt",encoding='utf8',mode='r')
fout1=codecs.open("out\words.txt",encoding='utf8',mode='w')

lines=fin.readlines()
for l in lines:
    line=','.join(jieba.cut(l))
    fout1.writelines(line)
        
fout.close()
fout1.close()

        
            
