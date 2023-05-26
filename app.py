import json
import os
import time
from flask import Flask, abort, jsonify, redirect, request, url_for
import ffmpeg
from sqlalchemy import create_engine, select
from models import Mark, Video, Img, Base
import cv2
from sqlalchemy.orm import Session

ALLOWED_EXTENSIONS = {'mp4'}
app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{app.config['USERNAME']}:{app.config['PWD']}@{app.config['HOST']}:{app.config['PORT']}/{app.config['DATABASE']}?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(bind=engine)


@app.route("/api/extract", methods=['POST'])
def extract():
    data = request.get_json()
    video_id = data['video_id']
    with Session(engine) as session:
        video = session.scalars(
            select(Video).where(Video.id == video_id)).first()
        path = os.path.join(app.config['VIDEO_FOLDER'], video.src)
        current_time = data['current_time']
        probe = ffmpeg.probe(path)
        video_info = next(
            s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        r_frame_rate = probe['streams'][0]['r_frame_rate'].split('/')
        frame_rate = int(r_frame_rate[0])/int(r_frame_rate[1])
        frame_num = int(current_time*frame_rate)
        output = "%d.jpg" % time.time()
        (
            ffmpeg
            .input(path)
            .filter('select', 'gte(n,{})'.format(frame_num))
            .output(os.path.join(app.config['IMG_FOLDER'], output), vframes=1, format='image2', vcodec='mjpeg')
            .run()
        )
        img = Img(output, video_id, width=width, height=height)
        session.add(img)
        session.commit()
        return jsonify(img.to_dict())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename and allowed_file(file.filename):
            filename = '%d.mp4' % time.time()
            save_path = os.path.join(app.config['VIDEO_FOLDER'], filename)
            file.save(save_path)
            video = Video(src=filename)
            with Session(engine) as session:
                session.add(video)
                session.commit()
                return jsonify(video.to_dict())
    abort(400)


@app.route("/api/mark", methods=['POST'])
def mark_post():
    data = request.get_json()
    src = data['src']
    flaw = data['flaw']
    level = data['level']
    x = data['x']
    y = data['y']
    width = data['width']
    height = data['height']
    img_id = data['img_id']

    with Session(engine) as session:
        imgObj = session.scalars(select(Img).where(Img.id == img_id)).first()
        img = cv2.imread(os.path.join(app.config['IMG_FOLDER'], imgObj.src))
        pt1 = (x, y)
        pt2 = (x+width, y+height)
        cv2.rectangle(img, pt1, pt2, (0, 0, 255), 1)
        name = "%d.jpg" % time.time()
        cv2.imwrite(os.path.join(app.config['MARK_FOLDER'], name), img)
        mark = Mark(name, flaw, level, x, y, width, height, img_id)
        session.add(mark)
        session.commit()
        return jsonify(mark.to_dict())
