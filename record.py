# _*_ coding=utf-8 _*_

from pyaudio import PyAudio,paInt16
import numpy
import wave

class recoder(object):
    def __init__(self):
        self.NUM_SAMPLES=2000    #pyaudio内置缓冲大小
        self.SAMPLES_RATE=8000   #取样频率
        self.LEVEL=500           #声音保存的阈值
        self.COUNT_NUM=20        #NUM_SAMPLES个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
        self.SAVE_LENGTH=8       #声音记录的最小长度：SAVE_LENGTH * NUM_SAMPLES个取样
        self.TIME_COUNT=60       #录音时间，单位s

        self.Voice_String=[]

    def save_wave(self,filename):
        self.recode()
        wf=wave.open(filename,'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.SAMPLES_RATE)
        write_data=b''
        for i in self.Voice_String:
            write_data+=i
        wf.writeframes(write_data)
        wf.close()

    def recode(self):
        pa=PyAudio()
        stream=pa.open(format=paInt16,channels=1,rate=self.SAMPLES_RATE,input=True,frames_per_buffer=self.NUM_SAMPLES)
        save_count=0
        save_buffer=[]
        time_count=self.TIME_COUNT
        print '\n\n\n正在录音中，请说出您的评价：'
        while True:
            time_count-=1
            string_audio_data=stream.read(self.NUM_SAMPLES)
            audio_data=numpy.fromstring(string_audio_data,dtype=numpy.short)
            large_sample_count=numpy.sum(audio_data>self.LEVEL)
            print(numpy.max(audio_data))
            if large_sample_count>self.COUNT_NUM:
                save_count=self.SAVE_LENGTH
            else:
                save_count-=1
            if save_count<0:
                save_count=0
            if save_count>0:
                save_buffer.append(string_audio_data)
            else:
                if len(save_buffer):
                    self.Voice_String=save_buffer
                    save_buffer=[]
                    print '记录一段语音成功'
                    return True
            if not time_count:
                if len(save_buffer):
                    self.Voice_String=save_buffer
                    save_buffer=[]
                    print '记录一段语音成功'
                    return True
                else:
                    return False
