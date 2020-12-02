# Import Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

# Create the engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Set up to reflect
Base = automap_base()

# Reflect the database
Base.prepare(engine, reflect = True)

# Save the tables to variables(classes)
Measure = Base.classes.measurement
Station = Base.classes.station

# set up the app
app = Flask(__name__)

# Setting up the routes!
# Got the home/index here
@app.route("/")
def index():
    # This prints to the terminal so we know that this function is being called properly
    print("message recieved")

    # We're gonna return each path that we have set up
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start_date <br/>"
        f"/api/v1.0/start_date/end_date"
    )

# got the precipitation route here
@app.route("/api/v1.0/precipitation")
def precip():
    # printing this to terminal so we know it's being called
    print("/api/v1.0/precipitation")

    # Making the session
    session = Session(engine)
    # This query returns the date and prcp columns and orders them by the date
    results = session.query(Measure.date, Measure.prcp).order_by(Measure.date).all()
    session.close()

    # Make an empty list to add stuff too
    listy = []
    # Start a for loop to loop through the results
    for date, precipitation in results:
        # Make an empty dictionary to add stuff to
        dicty = {}
        # Put the date and prcp into the dictionary with date as the key and prcp as the value
        dicty[date] = precipitation
        # Then add the dictionary to the list
        listy.append(dicty)
    # Then return the jsonified list
    return jsonify(listy)

# Then we have the stations route
@app.route("/api/v1.0/stations")
def stats():
    print("/api/v1.0/stations")
    session = Session(engine)

    # Only thing different about this one is this sel variable, which has all of the columns we want to call 
    # so we don't have to put them all into the query
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

# Then we have the tobs route
@app.route("/api/v1.0/tobs")
def temps():
    print("/api/v1.0/tobs")
    session = Session(engine)
    # We use this query to find the most active station
    active = session.query(Measure.station, func.count(Measure.station)).group_by(Measure.station).\
        order_by(func.count(Measure.station).desc()).first()
    # Then we grab all the tobs data from the last year at the most active station
    result = session.query(Measure.date, Measure.tobs).filter(Measure.date >= '2016-08-23').filter(Measure.station == active[0]).all()
    session.close()
    listy = []
    for date, temp in result:
        dicty = {}
        dicty[date] = temp
        listy.append(dicty)
    return jsonify(listy)

# Here we have our first dynamic route, the <> indicates that its going to be a variable, so we put "start" inside the function
@app.route("/api/v1.0/<start>")
def starty(start):
    print(f"/api/v1.0/{start}")
    session = Session(engine)
    result = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
        filter(Measure.date >= start).all()
    # Here we grab the first and last dates in the dataset so we have edges
    min_date = session.query(Measure.date).order_by(Measure.date).first()
    max_date = session.query(Measure.date).order_by(Measure.date.desc()).first()
    session.close()
    
    # We use this if statement to make sure that the start date is within the dataset
    # if it's not then we return the valid dates to choose from
    if (start > max_date[0]) or (start < min_date[0]):
        return f"The start date you have input is not in the database, the earliest date is {min_date[0]} and the latest date is {max_date[0]}"
    
    listy = []
    for minnie, avg, maxy in result:
        dicty = {}
        dicty['min temp'] = minnie
        dicty['avg temp'] = avg
        dicty['max temp'] = maxy
        listy.append(dicty)
    return jsonify(listy)

# Then we have our second dynamic route
@app.route("/api/v1.0/<start>/<end>")
def endy(start, end):
    print(f"/api/v1.0/{start}/{end}")
    session = Session(engine)
    result = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
        filter(Measure.date >= start).filter(Measure.date <= end).all()
    min_date = session.query(Measure.date).order_by(Measure.date).first()
    max_date = session.query(Measure.date).order_by(Measure.date.desc()).first()
    session.close()

    if (start > max_date[0]) or (start < min_date[0]) or (end > max_date[0]) or (end < min_date[0]):
        return f"The start or end date you have input is not in the database, the earliest date is {min_date[0]} and the latest date is {max_date[0]}"

    listy = []
    for minnie, avg, maxy in result:
        dicty = {}
        dicty['min temp'] = minnie
        dicty['avg temp'] = avg
        dicty['max temp'] = maxy
        listy.append(dicty)
    return jsonify(listy)

# Finally we run the app 
if __name__ == '__main__':
    app.run(debug = True)