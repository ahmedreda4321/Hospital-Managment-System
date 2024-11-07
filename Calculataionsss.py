import librosa,soundfile,os,librosa.display
from flask import Flask,url_for,redirect,render_template,request,send_file ,flash,session,jsonify
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import soundfile

def amplitude_envelope(signal, frame_size, hop_length):
    #Calculate the amplitude envelope of a signal with a given frame size nad hop length.
    amplitude_envelope = []

    # calculate amplitude envelope for each frame
    for i in range(0, len(signal), hop_length): 
        amplitude_envelope_current_frame = max(signal[i:i+frame_size]) 
        amplitude_envelope.append(amplitude_envelope_current_frame)

    return np.array(amplitude_envelope)   

def getAE(y,sr):
    FRAME_SIZE = 256
    HOP_LENGTH = 64
    AE = amplitude_envelope(y, FRAME_SIZE, HOP_LENGTH)
    #Visualizing the calculated AE
    frames = range(len(AE))
    t = librosa.frames_to_time(frames,sr=sr, hop_length=HOP_LENGTH)
    plt.figure(figsize=(8, 4))
    #librosa.display.waveshow(y,sr=sr)
    duration = len(y) / sr
    time = np.linspace(0, duration, len(y))
    plt.plot(time,y)
    plt.plot(t, AE, color="r")
    plt.ylim((-1, 1))
    plt.title("Amplitude Envelope")
    plt.savefig('apps/audio/temp/amplitude_enevelope.png', format='png')
    plt.close()

def getspect(y, sr):
     # Generate the spectrogram using librosa
    spectrogram = librosa.stft(y)

    # Plot the spectrogram
    plt.figure(figsize=(8, 4))
    librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max),sr=sr)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    plt.savefig('apps/audio/temp/spectrogram.png', format='png')
    plt.close()

def getmelspect(y,sr):
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    # Plot the spectrogram
    plt.figure(figsize=(8, 4))
    librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), sr=sr)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectogram')
    plt.tight_layout()
    # Save the plot to a BytesIO object
    plt.savefig('apps/audio/temp/melspectrogram.png', format='png')
    plt.close()
def getmfcc(y,sr):
    spectrogram = librosa.feature.mfcc(y=y,sr=sr)

    # Plot the spectrogram
    plt.figure(figsize=(8, 4))
    librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max),sr=sr)
    plt.colorbar(format='%+2.0f dB')
    plt.title('MFCC')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    plt.savefig('apps/audio/temp/mfcc.png', format='png')
    plt.close()
    
def getrms(y,sr):
    FRAME_SIZE = 256
    HOP_LENGTH = 64
    rms_audio = librosa.feature.rms(y=y, frame_length=FRAME_SIZE, hop_length=HOP_LENGTH)[0]
    #Visualizing the calculated RMS
    frames = range(len(rms_audio))
    t = librosa.frames_to_time(frames,sr=sr, hop_length=HOP_LENGTH)
    plt.figure(figsize=(8, 4))
    duration = len(y) / sr
    time = np.linspace(0, duration, len(y))
    #librosa.display.waveshow(y, alpha=0.5)
    plt.plot(time,y)
    plt.plot(t, rms_audio, color="r")
    
    plt.title("Root Mean Square")
    plt.tight_layout()
    # Save the plot to a BytesIO object
    plt.savefig('apps/audio/temp/RMS.png', format='png')
    plt.close()

def getzcr(y,sr):
    FRAME_SIZE = 256
    HOP_LENGTH = 64
    zcr_audio = librosa.feature.zero_crossing_rate(y=y, frame_length=FRAME_SIZE, hop_length=HOP_LENGTH)[0]
    frames = range(len(zcr_audio))
    t = librosa.frames_to_time(frames,sr=sr, hop_length=HOP_LENGTH)
    plt.figure(figsize=(8, 4))
    duration = len(y) / sr
    time = np.linspace(0, duration, len(y))
    plt.plot(time,y)
    plt.plot(t, zcr_audio, color="r")
    plt.title("Zero Cross Rate")
    plt.savefig('apps/audio/temp/ZCR.png',format='png')
    plt.close()

def savefeatures(file_name):
    matplotlib.use('agg')
    audio_file = f"apps/audio/uploads/{file_name}"
    y, sr = librosa.load(audio_file,sr=None,mono=True)
    getspect(y,sr)
    getmelspect(y,sr)
    getmfcc(y,sr)
    getAE(y,sr)
    getrms(y,sr)
    getzcr(y,sr)
    

   