from os import path, listdir
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from base64 import decodestring
from face import FaceWarp
import psycopg2
import urllib
import uuid

################################################################################
# CONFIG
################################################################################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abcdefg@37.139.31.245/hack4dk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

################################################################################
# DATABASE MODEL
################################################################################

class Graffiti(db.Model):
    __tablename__ = "graffiti"
    id = db.Column(db.Integer, primary_key=True)
    outcome_img = db.Column(db.String(256))
    art_img = db.Column(db.String(256))
    longitude = db.Column(db.Numeric(18,12))
    latitude = db.Column(db.Numeric(18,12))

    def to_dict(self):
        return { 'id': self.id, 'outcome_img': "/outcomes/%s.png" % self.outcome_img, 'art_img': self.art_img, 'longitude': str(self.longitude), 'latitude': str(self.latitude) }

################################################################################
# ROUTES
################################################################################

@app.route('/graffiti', methods=['GET', 'POST'])
def grafitti():
    if request.method == 'GET':
        location = request.args.get('location')
        latitude, longitude = location.split(',')
        return jsonify([g.to_dict() for g in Graffiti.query.limit(5).all()])
    elif request.method == 'POST':
        latitude, longitude = request.args.get('location').split(',')
        art = urllib.unquote(request.args.get('art'))
        outcome_id = str(uuid.uuid4())
        warp = FaceWarp(art, "inputs/0.png", ["inputs/1.png", "inputs/2.png"])
        for i, warped in warp.get_warps():
            outcome_path = 'outcomes/%s_%d.png' % (outcome_id, i)
            warped.save(outcome_path)
            db.session.add(Graffiti(outcome_img=outcome_path, art_img=art, longitude=longitude, latitude=latitude))
            db.session.commit()
            outcome_fnames.append(outcome_path)
        return jsonify({'outcomes': outcome_fnames, 'art': art})

@app.route('/outcomes', methods=['GET'])
def outcomes():
    return jsonify(["outcomes/" + fname for fname in listdir("outcomes")])

@app.route('/art', methods=['GET'])
def art():
    return jsonify(["static/" + fname for fname in listdir("static")])

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/outcomes/<path:path>')
def serve_outcomes(path):
    return send_from_directory('outcomes', path)

@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
