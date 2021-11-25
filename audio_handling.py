from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os 
import sys
import time
import speech_recognition as sr
import argparse
import io
import json

OUTPUT_FOLDER = os.path.abspath('../CensorIt_venv/static/output')

def listToString(s): 
    str1 = " , " 
    return (str1.join(s))

my_list = ['1','2','3',"Aro=pithabc","my name is"]
text = listToString(my_list)
print(text)

def main_method(fn,UPLOAD_FOLDER,alt_audio):
    #AUDIO_FILE = fn
    AUDIO_FILE = os.path.join(UPLOAD_FOLDER,fn)
    #audio_path = path(AUDIO_FILE)
    #print("path: "+audio_path)
    init_cred()
    trans = transcribe_file_with_word_time_offsets(AUDIO_FILE)
    #init_audio_segment(AUDIO_FILE)
    #init_csv()
    curse_words = []
    curse_words = find_curse_words(AUDIO_FILE,alt_audio)
    
    trans_words = []
    trans_words.append(trans)
    trans_words.append(curse_words)
    #trans = trans + " --> the number of curse words: "+str(num_of_curse_words)+" \n and they are: "+listToString(curse_words)
    return trans_words

def init_cred():
    os.environ['GOOGLE_CLOUD_SPEECH_CREDENTIALS'] = r"censorit_credentials.json"

    GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
       #enter key
    }
    """
    return GOOGLE_CLOUD_SPEECH_CREDENTIALS

def transcribe_file_with_word_time_offsets(speech_file):
    """Transcribe the given audio file synchronously and output the word time
    offsets."""
    from google.cloud import speech

    # create a client of my google cloud service
    client = speech.SpeechClient.from_service_account_json('censorit_credentials.json')

    # read the audio file
    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    # save the audio into google.cloud.speech_v1.types.cloud_speech.RecognitionAudio type
    audio = speech.RecognitionAudio(content=content)

    # change the configuration accordingly
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        enable_word_time_offsets=True,
        audio_channel_count=2
    )

    # define the respose string
    response = client.recognize(config=config, audio=audio)

    # clean the data from the output file
    if os.path.exists("data.json"): 
        os.remove("data.json")

    # for each result
    for result in response.results:
        alternative = result.alternatives[0]

        # transcribe the audio
        trans = format(alternative.transcript)

        # create an empty dictionary
        data = {}
        word_details = []
        # for each word in the speech find the time interval each work was spoken
        for word_info in alternative.words:
          word = word_info.word
          start_time = word_info.start_time
          end_time = word_info.end_time

         # we don't really need the time offsets to be printed/displayed 
         # print(
         #     f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
         # )
          word_details.append({
              'word': word,
              'start_time': start_time.total_seconds(),
              'end_time': end_time.total_seconds()
          })
        data['word_details'] = word_details
        with open('data.json','a') as outfile:
          json.dump(data, outfile)
        
        return trans

def init_audio_segment(audio_file):
    from pydub import AudioSegment
    my_audio = AudioSegment.from_wav(audio_file)
    my_audio.export('static/output/silenced.wav', format='wav')
    print("xxxx")

def replace_with_silence(word_to_be_removed,alt_audio):
    from pydub import AudioSegment
    with open('data.json') as json_file:
        data = json.load(json_file)
        my_audio = AudioSegment.from_wav('static/output/silenced.wav')
        
        if alt_audio == "beep_alt_audio":
            beep_audio =  AudioSegment.from_wav('beep.wav')
        elif alt_audio == "blank_alt_audio":
            beep_audio = AudioSegment.from_wav('blank.wav')
        else:
            beep_audio = AudioSegment.from_wav('strange.wav')

        for p in data['word_details']:
            if p['word'] == word_to_be_removed:

                # first piece
                first_piece_time = (p['start_time']+0.1) * 1000
                first_piece = my_audio[:first_piece_time]

                # end piece
                end_piece_time = (p['end_time']+0.1) * 1000
                end_piece = my_audio[end_piece_time:]

                #middle piece
                seconds_of_silence = ((p['end_time'] - p['start_time'] - 1) * 1000)
                middle_piece_sil = AudioSegment.silent(duration=seconds_of_silence)
                middle_piece_beep = beep_audio
                middle_piece = middle_piece_beep + middle_piece_sil

                #join them
                word_removed = first_piece + middle_piece + end_piece
                word_removed.export('static/output/silenced.wav', format='wav')

def init_csv():
    import pandas as pd
    df_badwords = pd.read_csv (r'C:\Users\arpit\Desktop\CensorIt_venv\bad-words.csv')
    jigaboo = df_badwords['jigaboo'].tolist()

def find_curse_words(song,alt_audio):
    curse_words = []
    import pandas as pd
    df_badwords = pd.read_csv (r'C:\Users\arpit\Desktop\CensorIt_venv\bad-words.csv')
    jigaboo = df_badwords['jigaboo'].tolist()
    from pydub import AudioSegment
    my_audio = AudioSegment.from_wav(song)

    #extra
    #censored_audio_name = "silenced"+" "+song
    #print(censored_audio_name)
    #my_audio.export(os.path.join(OUTPUT_FOLDER,censored_audio_name),format='wav')
    #extra end

    my_audio.export('static/output/silenced.wav', format='wav')
    with open('data.json') as json_file:
        data = json.load(json_file)
        my_audio = AudioSegment.from_wav(song)
        col = list(df_badwords)
        for p in data['word_details']:
            for i in jigaboo:
                if i == p['word']:
                    print(p['word'])
                    curse_words.append(p['word'])
                    replace_with_silence(p['word'],alt_audio)
    
    return curse_words
