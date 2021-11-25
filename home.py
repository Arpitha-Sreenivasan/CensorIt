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
from moviepy.editor import *
import moviepy.editor as mp
import video_handling

#TEMPLATE_DIR = os.path.abspath('../templates')
#STATIC_DIR = os.path.abspath('../static')

UPLOAD_FOLDER_AUDIO = os.path.abspath('../CensorIt_venv/upload/audio_upload')
UPLOAD_FOLDER_VIDEO = os.path.abspath('../CensorIt_venv/upload/video_upload')
OUTPUT_FOLDER = os.path.abspath('../CensorIt_venv/static/output')
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home_page.html')

@app.route('/upload_audio_file', methods=['GET', 'POST'])
def upload_audio_file():
    #if request.method == 'POST':
    file = request.files['audio_name']
    filename = secure_filename(file.filename)
    print(filename)
    
    timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
    print(filename.split('.'))
    print(type(filename))
    
    fn = filename.split('.')[0] + timestr + "." + filename.split('.')[1]
    file.save(os.path.join(UPLOAD_FOLDER_AUDIO, fn))
    #return redirect(url_for('main_method',fn))
    #trans = main_method(fn,UPLOAD_FOLDER_AUDIO)

    alt_audio = request.form['alternate_audio']
    print(alt_audio)
    trans_words = []
    trans_words = main_method(fn,UPLOAD_FOLDER_AUDIO,alt_audio)
    print(trans_words)
    trans = trans_words[0]
    num_of_curse_words = len(trans_words[1])
    trans_words.remove(trans)
    curse_words = []
    curse_words = trans_words[0]
    curse_words_string = listToString(curse_words)
    print(curse_words_string)
    num_curse = "The total number of curse words in this media: "+ str(num_of_curse_words)
    curse_words_string = "They are: "+curse_words_string
    transcript_opt = request.form['transcript']
    analysis_opt = request.form['audio_analysis']
    if transcript_opt == "yes_trans":
        if analysis_opt == "yes_audio_analysis":
            return render_template('audio_output.html', t="Transcript",transcript=trans, aud_ana="Audio Analysis",num_curse=num_curse,audio_analysis=curse_words_string)
        else:
            return render_template('audio_output.html', t="Transcript",transcript=trans)
    else:
        if analysis_opt == "yes_audio_analysis":
            return render_template('audio_output.html', aud_ana="Audio Analysis",num_curse=num_curse,audio_analysis=curse_words_string)
        else:
            return render_template('audio_output.html')
    #return "<h1>censored Audio is downloaded</h1><h5>Transcript : "+trans+"</h5>"
    

@app.route('/upload_vid_file', methods=['GET', 'POST'])
def upload_vid_file():
    #if request.method == 'POST':
    file = request.files['video_name']
    filename = secure_filename(file.filename)
    print(filename)
    
    timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
    print(filename.split('.'))
    print(type(filename))
    
    fn = filename.split('.')[0] + timestr + "." + filename.split('.')[1]
    file.save(os.path.join(UPLOAD_FOLDER_VIDEO, fn))
        #return redirect(url_for('main_method',fn))
    fn_audio = filename.split('.')[0] + timestr + ".wav"
    clip = mp.VideoFileClip(os.path.join(UPLOAD_FOLDER_VIDEO,fn))
    clip.audio.write_audiofile(os.path.join(UPLOAD_FOLDER_AUDIO,fn_audio))
    alt_audio = request.form['alternate_audio']

    trans_words = []
    trans_words = main_method(fn_audio,UPLOAD_FOLDER_AUDIO,alt_audio)
    print(trans_words)
    trans = trans_words[0]
    num_of_curse_words = len(trans_words[1])
    trans_words.remove(trans)
    curse_words = []
    curse_words = trans_words[0]
    curse_words_string = listToString(curse_words)
    print(curse_words_string)
    num_curse = "The total number of curse words in this media: "+ str(num_of_curse_words)
    curse_words_string = "They are: "+curse_words_string

    audioclip = mp.AudioFileClip(os.path.join(OUTPUT_FOLDER,'silenced.wav'))
    videoclip = clip.set_audio(audioclip)
    videoclip.ipython_display()
    video_duration = int(videoclip.duration)
    option = request.form['options']
    transcript_opt = request.form['transcript']
    analysis_opt = request.form['audio_analysis']
    if analysis_opt == "no_audio_analysis":
        if transcript_opt == "yes_trans":
            if option == "with_sub":
                video_handling.addSubtitles(video_duration)
                return render_template('video_output.html',t= "Transcript", transcript=trans)
            
            else:
                videoclip.write_videofile("static/output/fin_clip_withoutSub.mp4")
                return render_template('video_output_without_sub.html',t= "Transcript", transcript=trans)
                #return "<h1>censored Audio is downloaded</h1><h5>Transcript : "+trans+"</h5>"
        else:
            if option == "with_sub":
                video_handling.addSubtitles(video_duration)
                return render_template('video_output.html')
            
            else:
                videoclip.write_videofile("static/output/fin_clip_withoutSub.mp4")
                return render_template('video_output_without_sub.html')
                #return "<h1>censored Audio is downloaded</h1><h5>Transcript : "+trans+"</h5>"
    else:
        if transcript_opt == "yes_trans":
            if option == "with_sub":
                video_handling.addSubtitles(video_duration)
                return render_template('video_output.html',t= "Transcript", transcript=trans, aud_ana = "Video Analysis", num_curse = num_curse, curse_words = curse_words_string)
            
            else:
                videoclip.write_videofile("static/output/fin_clip_withoutSub.mp4")
                return render_template('video_output_without_sub.html', t= "Transcript", transcript=trans,aud_ana = "Video Analysis", num_curse = num_curse,audio_analysis = curse_words_string)
                #return "<h1>censored Audio is downloaded</h1><h5>Transcript : "+trans+"</h5>"
        else:
            if option == "with_sub":
                video_handling.addSubtitles(video_duration)
                return render_template('video_output.html',aud_ana = "Video Analysis",num_curse = num_curse,audio_analysis = curse_words_string)
            
            else:
                videoclip.write_videofile("static/output/fin_clip_withoutSub.mp4")
                return render_template('video_output_without_sub.html',aud_ana = "Video Analysis",num_curse = num_curse,audio_analysis = curse_words_string)
                #return "<h1>censored Audio is downloaded</h1><h5>Transcript : "+trans+"</h5>"

@app.route('/action_handle_audio')
def action_handle_audio(): 
    return render_template('audio_censoring.html')
    #return render_template('audio_handling.html')

#@app.route('/the_main_method',methods=['GET','POST'])

@app.route('/action_handle_video')
def action_handle_video():
    return render_template('video_censoring.html')

if __name__ == '__main__':
    app.run(host="localhost", port=4562, debug=True)