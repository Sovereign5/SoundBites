# Author: Christopher Garcia
# 12/15/2019
# Course Name: CST205
# Final code. Creates .mp3 files from a dropdown users select from, and 
#   allows for the user to download the file and listen to it themselves.

# Imports
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_bootstrap import Bootstrap
import numpy as np
import os

# Set the sample to CD standard at 16 bits per sample
SAMPLES_S = 44_110
BITS_SAMPLE = 16

# Wave header constants
CHUNK_ID = b'RIFF'
FORMAT = b'WAVE'
SUBCHUNK_1_ID = b'fmt '
SUBCHUNK_2_ID = b'data'

# PCM constants
SUBCHUNK_1_SIZE = (16).to_bytes(4, byteorder='little')
AUDIO_FORMAT = (1).to_bytes(2, byteorder='little')

# Creates the app for Flask
app = Flask(__name__)
FREQ_DICT = {
    "C0": 16.35,
    "D0": 18.35,
    "E0": 20.60,
    "F0": 21.83,
    "G0": 24.50,
    "A0": 27.50,
    "B0": 30.87,
    "C1": 32.70,
    "D1": 36.71,
    "E1": 41.20,
    "F1": 43.65,
    "G1": 49.00,
    "A1": 55.00,
    "B1": 61.74,
    "C2": 65.41,
    "D2": 73.42,
    "E2": 82.41,
    "F2": 87.31,
    "G2": 98.00,
    "A2": 110.00,
    "B2": 123.47,
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "B3": 246.94,
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.00,
    "B5": 987.77,
    "C6": 1046.50,
    "D6": 1174.66,
    "E6": 1318.51,
    "F6": 1396.91,
    "G6": 1567.98,
    "A6": 1760.00,
    "B6": 1975.53,
    "C7": 2093.00,
    "D7": 2349.32,
    "E7": 2637.02,
    "F7": 2793.83,
    "G7": 3135.96,
    "A7": 3520.00,
    "B7": 3951.07,
    "C8": 4186.01,
    "D8": 4698.63,
    "E8": 5274.04,
    "F8": 5587.65,
    "G8": 6271.93,
    "A8": 7040.00,
    "B8": 7902.13,
}

# Global Variables that refresh with every page refresh
all_bits_list = []
bach = []
threads = 0

# Home Page
@app.route("/", methods=['GET', 'POST'])
def home():
    # List for /home options
    option_list = ['option1', 'option2', 'option3', 'option4']
    option=""
    if request.method == "POST":
        option = request.form['option']
        home_option = []
        home_option.append(option)
    return render_template("home.html", option_list=FREQ_DICT)


# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Endpoint page for returning HTML->Ajax->Python
# AJAX/JS gives value to Python, value is added to list and notes are
#   added to bach[] list. The new list is sent back to JavaScript, where it
#   will update the hmtl WITHOUT reloading the page
@app.route("/submit_data", methods=['GET', 'POST'])
def submit_data():
    submitValue=None
    submitValue=request.get_data()
    submitValueNew = submitValue.decode()
    submitValueNew = str(submitValueNew)
    submitValueNew = submitValueNew.replace("submitValue=", "")
    bach.append(((submitValueNew, submitValueNew, submitValueNew), 4))
    threads = len(bach)
    new_wav(threads, "song", bach)
    os.remove("static/song.mp3")
    os.rename("song.mp3", "static/song.mp3")
    all_bits_list.append(submitValueNew)
    display = ', '.join(all_bits_list)
    print(submitValueNew)
    return display

# App Route for getting the .mp3 file for download
@app.route("/static/<path:filename>", methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory('static/', filename)

# create PCM waveform
# expects a tuple representing (chord, duration)
# each chord is itself a tuple of note letters that form a chord
# This code is from this class, lab17.
def create_pcm(notes):
    (chord, duration) = notes
    y_vals = 0
    # create an array of x valuess
    x_vals = np.arange(SAMPLES_S * duration)
    for note in chord:
        freq = FREQ_DICT[note]
        if not freq:
            freq = 0
        # convert frequency to angular frequency
        ang_freq1 = 2*np.pi*freq
        # numpy arithmetic to get y values from x values
        y_vals += 32767 * .3 * np.sin(ang_freq1 * x_vals / SAMPLES_S)
    y_vals = y_vals / len(chord)
    return np.int16(y_vals)

# This code is from this class, lab17.
def new_wav(channels, filename, song):

    length = 0
    my_pcm = []

    for notes in song:
        length += notes[1]
        my_pcm.append(create_pcm(notes))

    mat = np.array(my_pcm)

    seconds = length

    chunk_size = (int(36 + (seconds * SAMPLES_S * BITS_SAMPLE/8))).to_bytes(4, 'little')
    num_channels = (channels).to_bytes(2, byteorder='little')
    sample_rate = (SAMPLES_S).to_bytes(4, byteorder='little')
    byte_rate = (int(SAMPLES_S * channels * BITS_SAMPLE/8)).to_bytes(4, byteorder='little')
    block_align = (int(channels * BITS_SAMPLE/8)).to_bytes(2, byteorder='little')
    bits_per_sample = (BITS_SAMPLE).to_bytes(2, byteorder='little')
    subchunk_2_size = (int(seconds * SAMPLES_S * BITS_SAMPLE/8)).to_bytes(4, byteorder='little')

    
    with open(f'{filename}.mp3', 'wb') as fo:
        fo.write(
            CHUNK_ID +
            chunk_size +
            FORMAT +
            SUBCHUNK_1_ID +
            SUBCHUNK_1_SIZE +
            AUDIO_FORMAT +
            num_channels +
            sample_rate +
            byte_rate +
            block_align +
            bits_per_sample +
            SUBCHUNK_2_ID +
            subchunk_2_size +
            mat.tobytes()
        )


# RUNS THE APP!
if __name__ == "__main__":
    app.run(debug=True)

Bootstrap = Bootstrap(app)