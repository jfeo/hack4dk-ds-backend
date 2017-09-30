from os import path
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from base64 import decodestring
from face import *
import psycopg2
import urllib
import uuid

################################################################################
# CONFIG
################################################################################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abcdefg@localhost/hack4dk'
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
        location = request.args.get('location')
        latitude, longitude = location.split(',')
        art = urllib.unquote(request.args.get('art'))
        outcome = str(uuid.uuid4())
        # print([k for k in request.files])
        # f = open('outcomes/%s.png' % outcome, 'wb')
        # data = request.data.decode('utf8')
        # _, img64 = data.split('base64,')
        # f.write(decodestring(img64.encode('utf8')))
        # f.close()
        trans = generate_transforms(["inputs/0.png", "inputs/1.png", "inputs/2.png"])
        warped_art(uuid, art, trans)
        outcome_fnames = []
        for i in range(2):
            db.session.add(Graffiti(outcome_img='outcomes/%s_%d.png' % (outcome, i), art_img=art, longitude=longitude, latitude=latitude))
            db.session.commit()
            outcome_fnames.append('outcomes/%s_%d.png' % (outcome, i))
        return jsonify({'outcomes': outcome_fnames, 'art': art})

@app.route('/art', methods=['GET'])
def art():
    return jsonify(["static/" + fname for fname in os.listdir("static")])

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
