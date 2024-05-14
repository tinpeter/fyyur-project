from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity, PrimaryKeyConstraint
from forms import *
#----------------------------------------------------------------------------#
# db SQLAlchemy Config.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.

class Show(db.Model):
    __tablename__ = 'show'
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.String(120), primary_key=True)
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(
      db.Integer,Identity(start=1, increment=1,minvalue=1,nomaxvalue=True ,cycle=True) ,primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref='Venue', lazy='joined', cascade="all, delete")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(
      db.Integer, Identity(start=1, increment=1,minvalue=1,nomaxvalue=True ,cycle=True) ,primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default = True)
    shows = db.relationship('Show', backref='Artist', lazy='joined', cascade="all, delete")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# app.app_context().push()
# db.create_all()