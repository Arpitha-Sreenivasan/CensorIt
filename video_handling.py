from moviepy.editor import *
import json
import os
import subtitles


print("xxx")
IMAGEMAGICK_BINARY = '../ImageMagick-7.0.11-8-portable-Q16-HDRI-x86/magick.exe'

def addSubtitles(vid_duration):
    if os.path.exists("subs.json"): 
        os.remove("subs.json")

    subtitles.createSubsjson(vid_duration)
    list_clip = []

    with open('subs.json') as json_file:
        subs = json.load(json_file)
        for sub in subs['subtitles_details']:
            print(sub['sent'],sub['start_time'],sub['end_time'],sub['dur'])
            clip = VideoFileClip("__temp__.mp4").subclip(sub['start_time'],sub['end_time'])
            txt_clip = TextClip(sub['sent'],fontsize=40,bg_color='white')
            txt_clip = txt_clip.set_pos('bottom').set_duration(sub['dur'])
            clip_comp = CompositeVideoClip([clip,txt_clip])
            list_clip.append(clip_comp)
        fin_clip = concatenate_videoclips(list_clip)
        fin_clip.write_videofile("static/output/fin_clip_withSub.mp4")
