# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

from sqlalchemy.orm import scoped_session, sessionmaker

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# From Dom's in-class example. Keeps things from breaking. 
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

# Reflect the database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Station = Base.classes.station
Measurements = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"A list of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"A list of station numbers and names<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"A list of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/2017-08-15'>/api/v1.0/start</a><br/>"
        f"Given a start date in YYYY-MM-DD format, calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/2017-08-15/2017-08-23'>/api/v1.0/start/end</a><br/>"
        f"Given a start date and end date in YYYY-MM-DD format, calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )

    
#####################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
    precip_last_date = session.query(func.max(Measurements.date).label("precip_max_date")).scalar()
    precip_year_ago = dt.datetime.strptime(precip_last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    last_12m_precip = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= precip_year_ago).filter(Measurements.date <= precip_last_date).order_by(Measurements.date).all()

    rain_totals = []
    for result in last_12m_precip:
        row = {}
        row["date"] = last_12m_precip[0]
        row["prcp"] = last_12m_precip[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#####################################################

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())


#####################################################

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.

    #last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    tobs_last_date = session.query(func.max(Measurements.date).label("tobs_max_date")).scalar()
    tobs_last_year = dt.datetime.strptime(tobs_last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    temperature = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > tobs_last_year).\
        order_by(Measurements.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)


#####################################################

@app.route("/api/v1.0/<start>")
def startdate(start):

 # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.  
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    date_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start_date).all()
    return jsonify(date_data)

#####################################################

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    date_range_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    return jsonify(date_range_data)


#####################################################

if __name__ == "__main__":
    app.run(debug=True)