import os
import time
from flask import Flask, abort, redirect, request, url_for
import ffmpeg

UPLOAD_FOLDER = '/Users/xzjs/Code/Html/pipe/public'
ALLOWED_EXTENSIONS = {'mp4'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/extract", methods=['POST'])
def extract():
    data = request.get_json()
    path = os.path.join(UPLOAD_FOLDER, data['path'])
    current_time = data['current_time']
    probe = ffmpeg.probe(path)
    r_frame_rate = probe['streams'][0]['r_frame_rate'].split('/')
    frame_rate = int(r_frame_rate[0])/int(r_frame_rate[1])
    frame_num = int(current_time*frame_rate)
    output = "%d.jpg" % time.time()
    (
        ffmpeg
        .input(path)
        .filter('select', 'gte(n,{})'.format(frame_num))
        .output(os.path.join(UPLOAD_FOLDER, output), vframes=1, format='image2', vcodec='mjpeg')
        .run()
    )
    return {"img_path": output}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename and allowed_file(file.filename):
            filename = '%d.mp4' % time.time()
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            return {"path": filename}
    abort(400)
