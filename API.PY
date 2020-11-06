# DEPENDENCIES
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

################
# DATABASE SETUP
################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# REFLECT AN EXISTING DATABASE INTO A NEW MODEL
Base = automap_base()

# REFLECT THE TABLES
Base.prepare(engine, reflect=True)

# SAVE REFERENCES TO EACH TABLE
Measurement = Base.classes.measurement
Station = Base.classes.station

#############
# Flask Setup
#############
app = Flask(__name__)

##############
# Flask Routes
##############

@app.route("/")
def index():
    print("Server received request for 'Home' page....")
    return(
        f"Wecome to the 'Home' page<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # CREATE OUR SESSION (LINK) FROM PYTHON TO THE DB
    session = Session(engine)

    # QUERY PRECIPITATION
    query = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    # CREATE A DICTIONARY FROM THE ROW DATA AND APPEND TO A LIST OF OBSERVATIONS
    precipitation = []
    for date, prcp in query:
        dict = {}
        dict["date"] = date
        dict["prcp"] = prcp
        precipitation.append(dict)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # CREATE OUR SESSION (LINK) FROM PYTHON TO THE DB
    session = Session(engine)

    # QUERY ALL STATIONS
    query = session.query(Station.name).all()
    session.close()

    # CONVERT LIST OF TUPLES INTO NORMAL LIST
    stations = list(np.ravel(query))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # CREATE OUR SESSION (LINK) FROM PYTHON TO THE DB
    session = Session(engine)

    # FIND DATES
    end_date = dt.datetime.strptime(session.query(Measurement.date)[-1:][0][0],'%Y-%m-%d')
    end_date = dt.date((end_date).year, (end_date).month, (end_date).day)
    start_date = dt.date((end_date).year-1, (end_date).month, (end_date).day)

    # FIND MOST ACTIVE STATION
    query = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc())
    most_active_station = query[0][0]

    # QUERY TEMPERATURES
    query = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= start_date).all()
    session.close()

    # CREATE A DICTIONARY FROM THE ROW DATA AND APPEND TO A LIST OF OBSERVATIONS
    temperature_obs = []
    for date, tobs in query:
        dict = {}
        dict["date"] = date
        dict["tobs"] = tobs
        temperature_obs.append(dict)
    return jsonify(temperature_obs)

@app.route("/api/v1.0/<start>")
def start(start):
    # CREATE OUR SESSION (LINK) FROM PYTHON TO THE DB
    session = Session(engine)
    
    # RETURN A JSON LIST OF THE MINIMUM TEMPERATURE, THE AVERAGE TEMPERATURE, AND THE MAX TEMPERATURE FOR A GIVEN START OR START-END RANGE.
    # WHEN GIVEN THE START ONLY, CALCULATE TMIN, TAVG, AND TMAX FOR ALL DATES GREATER THAN AND EQUAL TO THE START DATE.
    query = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').all()
    session.close()

    # CREATE A DICTIONARY FROM THE ROW DATA AND APPEND TO A LIST OF OBSERVATIONS
    temperature_obs_start = []
    for tmin, tavg, tmax in query:
        dict = {}
        dict["tmin"] = tmin
        dict["tavg"] = tavg
        dict["tmax"] = tmax
        temperature_obs_start.append(dict)
    return jsonify(temperature_obs_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # CREATE OUR SESSION (LINK) FROM PYTHON TO THE DB
    session = Session(engine)
    
    # RETURN A JSON LIST OF THE MINIMUM TEMPERATURE, THE AVERAGE TEMPERATURE, AND THE MAX TEMPERATURE FOR A GIVEN START OR START-END RANGE.
    # WHEN GIVEN THE START AND THE END DATE, CALCULATE TMIN, TAVG, AND TMAX FOR ALL DATES GREATER THAN AND EQUAL TO THE START DATE.
        
    query = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}', Measurement.date <= f'{end}').all()
    session.close()

    # CREATE A DICTIONARY FROM THE ROW DATA AND APPEND TO A LIST OF OBSERVATIONS
    temperature_obs_start_end = []
    for tmin, tavg, tmax in query:
        dict = {}
        dict["tmin"] = tmin
        dict["tavg"] = tavg
        dict["tmax"] = tmax
        temperature_obs_start_end.append(dict)
    return jsonify(temperature_obs_start_end)

if __name__ == '__main__':
    app.run(debug=True)
