# _*_ coding: utf-8 _*_

import sys

sys.path.append(r'/home/feizao/python代码')

from sentiment_analysis import record,speech_recognition,jd_review

class menu(object):
    def run(self):
        product_id=raw_input('请输入要评价的京东商品ID：')
        j=jd_review.reviewer(product_id)
        result=j.run_review()
        if not result:
            return self.run()
        print '#####################'
        print '#   1. 文字评价     #'
        print '#   2. 语音评价     #'
        print '#   0. 退出　　     #'
        print '#####################'
        choose=input('请选择评价模式：')
        if choose==1:
            data=raw_input('请输入您的评价：')
            j.classify(data)
        elif choose==2:
            r=record.recoder()
            r.save_wave('recoder.wave')
            s=speech_recognition.api()
            s.recog()
            with open('recongition.txt') as f:
                data=f.read()
                j.classify(data)
        elif choose==0:
            return
        else:
            print '输入错误，请重新输入：'
            return self.run

    def start(self):
        flag=raw_input('\n\n是否现在开始评价？y/n:')
        if flag=='y':
            self.run()
            return self.start()
        elif flag=='n':
            return
        else:
           print '输入错误！'
           return self.start()
if __name__=='__main__':
    m=menu()
    m.start()
