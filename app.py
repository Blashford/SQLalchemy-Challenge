import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measure = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def index():
    print("message recieved")
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start_date <br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    print("/api/v1.0/precipitation")
    session = Session(engine)
    results = session.query(Measure.date, Measure.prcp).order_by(Measure.date).all()
    session.close()
    listy = []
    for date, precipitation in results:
        dicty = {}
        dicty[date] = precipitation
        listy.append(dicty)
    return jsonify(listy)

@app.route("/api/v1.0/stations")
def stats():
    print("/api/v1.0/stations")
    session = Session(engine)
    sel = [
        Station.id,
        Station.station,
        Station.name,
        Station.latitude,
        Station.longitude,
        Station.elevation
    ]
    results = session.query(*sel).all()
    session.close()
    listy = []
    for id, station, name, lat, lng, elev in results:
        dicty = {}
        dicty['id'] = id
        dicty['station'] = station
        dicty['name'] = name
        dicty['lat'] = lat
        dicty['lng'] = lng
        dicty['elevation'] = elev
        listy.append(dicty)
    return jsonify(listy) 

@app.route("/api/v1.0/tobs")
def temps():
    print("/api/v1.0/tobs")
    session = Session(engine)
    active = session.query(Measure.station, func.count(Measure.station)).group_by(Measure.station).\
        order_by(func.count(Measure.station).desc()).first()
    result = session.query(Measure.date, Measure.tobs).filter(Measure.date >= '2016-08-23').filter(Measure.station == active[0]).all()
    session.close()
    listy = []
    for date, temp in result:
        dicty = {}
        dicty[date] = temp
        listy.append(dicty)
    return jsonify(listy)

@app.route("/api/v1.0/<start>")
def starty(start):
    print(f"/api/v1.0/{start}")
    session = Session(engine)
    result = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
        filter(Measure.date >= start).all()
    session.close()
    listy = []
    for minnie, avg, maxy in result:
        dicty = {}
        dicty['min temp'] = minnie
        dicty['avg temp'] = avg
        dicty['max temp'] = maxy
        listy.append(dicty)
    return jsonify(listy)

@app.route("/api/v1.0/<start>/<end>")
def endy(start, end):
    print(f"/api/v1.0/{start}/{end}")
    session = Session(engine)
    result = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
        filter(Measure.date >= start).filter(Measure.date <= end).all()
    session.close()
    listy = []
    for minnie, avg, maxy in result:
        dicty = {}
        dicty['min temp'] = minnie
        dicty['avg temp'] = avg
        dicty['max temp'] = maxy
        listy.append(dicty)
    return jsonify(listy)
    
if __name__ == '__main__':
    app.run(debug = True)