from stegano import lsb
from flask import Blueprint, render_template, current_app, url_for, redirect, request, flash
from werkzeug.utils import secure_filename
import cv2
import os
import math
import shutil
from subprocess import run, CalledProcessError
import uuid
import traceback
import sys

video = Blueprint("video", __name__, static_folder="static",
                  template_folder="templates")


@video.route("/encode")
def video_encode():
    return render_template("encode-video.html")


@video.route("/encode-result", methods=['POST', 'GET'])
def video_encode_result():
    if request.method == 'POST':
        message = request.form['message']

        if 'video' not in request.files:
            flash('No video found')
            return redirect(url_for("video.video_encode"))

        file = request.files['video']
        if file.filename == '':
            flash('No selected video')
            return redirect(url_for("video.video_encode"))

        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_VIDEO_FOLDER'], exist_ok=True)
        file.save(save_path)

        try:
            encrypt(save_path, message)
            encryption = True
        except Exception as e:
            print(f"Encryption error: {e}")
            traceback.print_exc()
            encryption = False

        return render_template("encode-video-result.html",
                               message=message,
                               file=filename,
                               encryption=encryption)

    return redirect(url_for("video.video_encode"))


@video.route("/decode")
def video_decode():
    return render_template("decode-video.html")


@video.route("/decode-result", methods=['POST', 'GET'])
def video_decode_result():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No video found')
            return redirect(url_for("video.video_decode"))

        file = request.files['video']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for("video.video_decode"))

        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_VIDEO_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_VIDEO_FOLDER'], exist_ok=True)
        file.save(save_path)

        try:
            decrypted_text = decrypt(save_path)
            decryption = True
        except Exception as e:
            print(f"Decryption error: {e}")
            traceback.print_exc()
            decrypted_text = ""
            decryption = False

        return render_template("decode-video-result.html",
                               decrypytedText=decrypted_text,
                               file=filename,
                               decryption=decryption)

    return redirect(url_for("video.video_decode"))


def get_ffmpeg_path():
    # Check system path first
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    # Check bundled path (mainly for Windows)
    bundled_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        "ffmpeg-4.3.1-2020-10-01-full_build", "bin", "ffmpeg.exe"
    ))
    if os.path.exists(bundled_path):
        return bundled_path
        
    return None


def encrypt(f_name, input_string):
    temp_dir = frame_extraction(f_name)
    try:
        encode_string(input_string, root=temp_dir)

        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            raise FileNotFoundError("ffmpeg not found. Please install ffmpeg or ensure it is in the project structure.")

        os.makedirs("modes/Video/static", exist_ok=True)
        out_file = "modes/Video/static/enc-video.mp4"

        cmd = [
            ffmpeg_path, "-y",
            "-framerate", "24",
            "-i", os.path.join(temp_dir, "%d.png"),
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            out_file
        ]

        run(cmd, check=True)
    finally:
        clean_tmp(temp_dir)


def split_string(s_str, count=10):
    if not s_str:
        return []
    per_c = math.ceil(len(s_str) / count)
    out_str = ''
    split_list = []
    c = 0
    for s in s_str:
        out_str += s
        c += 1
        if c == per_c:
            split_list.append(out_str)
            out_str = ''
            c = 0
    if out_str:
        split_list.append(out_str)
    return split_list


def frame_extraction(video):
    temp_dir = os.path.join("tmp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    vidcap = cv2.VideoCapture(video)
    if not vidcap.isOpened():
        shutil.rmtree(temp_dir)
        raise IOError(f"Cannot open video file {video}")

    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_dir, f"{count}.png"), image)
        count += 1
    
    vidcap.release()
    return temp_dir


def encode_string(input_string, root):
    split_list = split_string(input_string)

    frame_files = sorted(
        [f for f in os.listdir(root) if f.endswith(".png")],
        key=lambda x: int(x.split(".")[0])
    )

    if not frame_files:
        raise RuntimeError("No frames extracted")

    for i, chunk in enumerate(split_list):
        frame_index = i % len(frame_files)
        f_name = os.path.join(root, frame_files[frame_index])
        secret_enc = lsb.hide(f_name, chunk)
        secret_enc.save(f_name)


def decrypt(video):
    temp_dir = frame_extraction(video)
    try:
        files = sorted(
            [f for f in os.listdir(temp_dir) if f.endswith(".png")],
            key=lambda x: int(x.split(".")[0])
        )

        secret = []
        for f in files:
            f_name = os.path.join(temp_dir, f)
            try:
                revealed = lsb.reveal(f_name)
                if revealed:
                    secret.append(revealed)
            except:
                pass
        
        return ''.join(secret)
    finally:
        clean_tmp(temp_dir)


def clean_tmp(path):
    if os.path.exists(path):
        shutil.rmtree(path)
