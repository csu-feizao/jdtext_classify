# _*_ coding: utf-8 _*_

import os
import requests
import json
import mysql.connector
from tgrocery import Grocery
from sentiment_analysis import split

class reviewer(object):
    def __init__(self,product_id):
        self.flag='0'
        self.score_dict={1:'negative',2:'neutral',3:'positive'}
        self.product_id=product_id
        self.test=[('negative','不想说了，用了几天就坏了'),('positive','小时候的味道'),('negative','物流很快，但是商品很差，根本不能用'),('positive','很满意的一次购物'),('negative','买回来就降价，心塞'),('neutral','包装比较差，其他还可以，一般般'),('positive','非常完美！速度与激情同在，支持京东购物'),('neutral','还行，凑合着用，主要是性价比高'),('negative','质量不好，便宜没好货'),('positive','京东的速度真是我见过的最快的，6666'),('neutral','也就那样吧，一分钱一分货')]


    def connect_mysql(self):
        self.conn=mysql.connector.connect(user='root',password='password',charset='utf8')
        self.cursor=self.conn.cursor()
        self.cursor.execute('create database if not exists jd')
        self.conn.connect(database='jd')
        self.create_table()


    def create_table(self):
        try:
            self.cursor.execute('create table %s (id varchar(200) primary key,nickname varchar(20),content varchar(500),score char(1),classify varchar(20)) default charset=utf8' %('goods_'+self.product_id))
        except mysql.connector.Error as e:
            self.flag=raw_input('您已爬取过该商品的评价，您确定要重新爬取吗？y/n:')
            if self.flag=='y':
                self.cursor.execute('drop table %s' %('goods_'+self.product_id))
                return self.create_table()
            elif self.flag=='n':
                return
            else:
                print '输入错误！'
                return self.create_table()
        except Exception as e:
            print e
            exit(-1)


    def find_review(self,score,max_page=20):
        page=0
        page_data=''
        while True:
            url='https://sclub.jd.com/comment/productPageComments.action?productId={}&score={}&sortType=3&page={}&pageSize=10'.format(self.product_id,score,page)
            r=requests.get(url)
            if page_data==r.text:
                return page
            page_data=r.text
            try:
                data=json.loads(page_data)
                if len(data['comments']) and page<max_page:
                    print '\n\nsore=',self.score_dict[score],'\tpage=',page
                    for review in data['comments']:
                        if review['referenceId']==self.product_id:
                            self.count+=1
                            do='insert into goods_'+self.product_id+' (id,nickname,content,score,classify) values(%s,%s,%s,%s,%s)'
                            try:
                                self.cursor.execute(do,(str(self.count),review['nickname'],review['content'],review['score'],self.score_dict[score]))
                            except Exception as e:
                                print e
                            print self.count,review['nickname'],review['content'],review['score']
                    page+=1
                else:
                    return page
            except ValueError as e:
                print e


    def select(self):
        self.train_data=[]
        self.cursor.execute("select classify,content from %s where classify ='positive'" %('goods_'+self.product_id))
        result_data1=self.cursor.fetchall()
        self.cursor.execute("select classify,content from %s where classify ='neutral'" %('goods_'+self.product_id))
        result_data2=self.cursor.fetchall()
        self.cursor.execute("select classify,content from %s where classify ='negative'" %('goods_'+self.product_id))
        result_data3=self.cursor.fetchall()
        positive,neutral,negative=len(result_data1),len(result_data2),len(result_data3)
        min_num=min(positive,neutral,negative)
        max_num=max(positive,neutral,negative)
        self.train_data=result_data1[:min_num]+result_data2[:min_num]+result_data3[:min_num]
        if self.train_data:
            if os.path.exists('split.txt'):
                os.remove('split.txt')
            for r in self.train_data:
                split.cut(r[0],r[1])
                print r[0],r[1]
        print '\n\n\n好评数：',positive,'中评数：',neutral,'差评数',negative
        if min_num<max_num:
            self.predict_data=result_data1[min_num:]+result_data2[min_num:]+result_data3[min_num:]
            print '使用每类的前{}个作为训练样本，剩下的作为测试样本．'.format(min_num)
        else:
            self.predict_data=self.test
            print '每类{}个训练样本'.format(min_num)
            print '使用以下几个作为测试样本：'
            for data in self.predict_data:
                print data[0],data[1]


    def predict(self):
        if self.predict_data:
            pre=Grocery('classify/{}'.format(self.product_id))
            pre.load()
            print '商品{}分类器准确率：'.format(self.product_id),pre.test(self.predict_data)


    def classify(self,data):
        new_grocery=Grocery('classify/'+self.product_id)
        new_grocery.load()
        print '\n\n分类结果：'
        classify_data=new_grocery.predict(data)
        print classify_data,data
        with open('calssify_data.txt','w') as fwrite:
            fwrite.write(str(classify_data)+' '+data)


    def run_review(self):
        self.connect_mysql()
        if self.flag=='0' or self.flag=='y':
            self.count=0
            self.find_review(score=1)
            self.find_review(score=2)
            self.find_review(score=3)
            self.conn.commit()
            self.select()
            if not self.train_data:
                print '训练样本为空，请检查商品ID是否正确后重新爬取商品评价！'
                return False
            self.conn.close()
            print '\n\n正在训练分类器．．．'
            grocery=Grocery('classify/'+self.product_id)
            grocery.train(self.train_data)
            grocery.save()
            print '训练成功！'
            self.predict()
        return True

