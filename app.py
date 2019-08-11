import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-01-01<br/>"
        f"/api/v1.0/2016-01-01/2017-01-07"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precip Data"""
    #query all precip data
    results = session.query(Measurement.date, Measurement.prcp).all()
    #close session due to large query size
    session.close()

    # Convert list of tuples into normal list
    all_precip = list(np.ravel(results))

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    station = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_station = list(np.ravel(station))

    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperature observatons"""
    # query most recent date recorded
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    # Create time frame for most recent year
    previous_year=dt.datetime.strptime(max_date, "%Y-%m-%d") - relativedelta(months=12)
    #query recent temperature observations
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= previous_year).all()

    # Convert list of tuples into normal list
    all_tobs = list(tobs)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start=None):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    

    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),       func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)

if __name__ == '__main__':
    app.run(debug=True)