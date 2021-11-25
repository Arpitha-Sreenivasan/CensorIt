from flask import Flask, render_template, request
from flask import redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os 
import sys
import time
import speech_recognition as sr
import argparse
import io
import json
from audio_handling import *
import math
import pysrt
import moviepy
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing import CompositeVideoClip
from os.path import splitext, isfile

def listToString(s): 
    str1 = " " 
    return (str1.join(s))

def createSubsjson(vid_duration):
    with open('data.json') as json_file:
        data = json.load(json_file)
        n = 0
        et = 0
        sub_list = []
        sr_no = 1
        outfile = open('subtitles_srt.txt','a')
        outfile.truncate(0)
        
        while sr_no < (vid_duration//2):
            sub = {}
            subtitles_det = []
            while n <= vid_duration: #might give incomplete output on a different audio file
                prev_et = et
                for p in data['word_details']:
                    if p['end_time'] <= n:
                        if p['start_time'] >= et:
                            sub_list.append(p['word'])
                            et = p['end_time']
                if len(sub_list) == 0:
                    n = n+2
                else:
                    sub_text = listToString(sub_list)
                    sub_list.clear()
                    print(prev_et," --> ",et)
                    print(sub_text)
                    subtitles_det.append({
                        'sent' : sub_text,
                        'start_time' : prev_et,
                        'end_time' : et,
                        'dur' : (et - prev_et)
                    })
                    n = n+2
                    sr_no = sr_no + 1
            sub['subtitles_details'] = subtitles_det
            with open('subs.json','a') as outfile:
                json.dump(sub, outfile)

#createSrt(video_duration)
