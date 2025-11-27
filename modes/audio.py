import os
import shutil
import wave
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from datetime import timedelta

from werkzeug.utils import secure_filename

audio = Blueprint("audio", __name__, static_folder="static",
                  template_folder="templates")


@audio.route("/encode")
def audio_encode():
    return render_template("encode-audio.html")


@audio.route("/encode-result", methods=['POST', 'GET'])
def audio_encode_result():
    if request.method == 'POST':
        message = request.form['message']
        if 'file' not in request.files:
            flash('No audio found')
        file = request.files['audio']

        if file.filename == '':
            flash('No audio selected')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_AUDIO_FOLDER'], filename))
            audio_encryption = True
            encrypt_audio(os.path.join(
                current_app.config['UPLOAD_AUDIO_FOLDER'], filename), message)
        else:
            audio_encryption = False
        result = request.form

        return render_template("encode-audio-result.html", result=result, file=file, audio_encryption=audio_encryption, message=message)


@audio.route("/decode")
def audio_decode():
    return render_template("decode-audio.html")


@audio.route("/decode-result", methods=['POST', 'GET'])
def audio_decode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No audio found')
        file = request.files['audio']
        if file.filename == '':
            flash('No audio selected')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_AUDIO_FOLDER'], filename))
            audio_decryption = True
            message = decrypt_audio(os.path.join(
                current_app.config['UPLOAD_AUDIO_FOLDER'], filename))
        else:
            audio_decryption = False
        result = request.form
        return render_template("decode-audio-result.html", result=result, file=file, audio_decryption=audio_decryption, message=message)


def encrypt_audio(audio, message):
    song = wave.open(audio, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    string = str(message)
    string = string + int((len(frame_bytes)-(len(string)*8*8))/8) * '#'
    bits = list(
        map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in string])))

    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)

    with wave.open(os.path.join(current_app.config['UPLOAD_AUDIO_FOLDER'], "song_embedded.wav"), 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    song.close()


def decrypt_audio(audio):
    song = wave.open(audio, mode='rb')
 
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]

    string = "".join(chr(
        int("".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))
    decoded = string.split("###")[0]

    song.close()
    return decoded
