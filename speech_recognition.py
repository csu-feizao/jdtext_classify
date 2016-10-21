# _*_ coding: utf-8 _*_

import requests,json
import sys,re
import base64
from io import open

class api(object):
    def update_token(self):
        api_key,secret_key=sys.stdin.readline().strip().split()
        url="https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}".format(api_key,secret_key)
        r=requests.get(url)
        self.access_token=json.loads(r.text)['access_token']
        with open('token.txt','w') as fp:
            fp.write(self.access_token)

    def set_post_data(self):
        file_url='recoder.wave'
        with open(file_url,'rb') as f:
            self.speech=f.read()
        self.speech_base64=base64.b64encode(self.speech).decode('utf-8')
        self.file_size=len(self.speech)
        with open('token.txt','r') as fr:
            self.access_token=fr.read()
        self.post_data={
            'format':'wav',
            'channel':1,
            'rate':8000,
            'cuid':'肥皂',
            'token':self.access_token,
            'speech':self.speech_base64,
            'len':self.file_size
        }

    def recog(self):
        self.set_post_data()
        srv_url = 'http://vop.baidu.com/server_api'
        r=requests.post(srv_url,data=json.dumps(self.post_data).encode('utf-8')).text
        #print(r)
        result=json.loads(r)
        if result['err_msg']=='success.':
            recognition=result['result'][0]
            if recognition:
                print '语音识别结果：',recognition
                with open('recongition.txt','w') as fw:
                    fw.write(recognition)
            else:
                print '未识别到文字'
        elif result['err_msg']=='authentication failed.':
            print 'token失效，正在重新获取token...'
            self.update_token()
            return self.recog()
        elif result['err_msg']=='recognition error.':
            print '识别错误'
        else:
            print '识别失败'
