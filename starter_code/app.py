#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# import datetime
from datetime import datetime
import json
import dateutil.parser
import babel
import sys
import re
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for
)
from flask_moment import Moment
from flask_migrate import Migrate
from forms import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Get current date.
current_date = babel.dates.format_datetime(datetime.now(), "medium", locale='en')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data_list = Venue.query.all()
  categories = []
  for item in data_list:
    venue = {
      'id': item.id,
      'name': item.name,
    }
    findCurrent = next((c for c in categories if c['city'] == item.city and c['state'] == item.state), None)
    if findCurrent:
      findCurrent['venues'].append(venue)
    else:
      city = {
        'city': item.city,
        'state': item.state,
        'venues': [venue]
      }
      categories.append(city)

  return render_template('pages/venues.html', areas=categories)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  venue_list = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  response = {
    "count": len(venue_list),
    "data": [],
    "num_upcoming_shows": 0
  }

  for venue in venue_list:
    response["data"].append({
      'id': venue.id,
      'name': venue.name
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  venue = Venue.query.get_or_404(venue_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  for show in venue.shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': Artist.query.get_or_404(show.artist_id).name,
        'artist_image_link': Artist.query.get_or_404(show.artist_id).image_link,
        'start_time': dateutil.parser.parse(show.start_time).strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= current_date:
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # Set the FlaskForm
  form = VenueForm(request.form, meta={'csrf': False})
  # Validate all fields
  if form.validate():
    # Prepare for transaction
    try:
      data = Venue(
        name = form.name.data, city = form.city.data, state = form.state.data, address = form.address.data,
        phone = form.phone.data, genres = '', image_link = form.image_link.data, facebook_link = form.facebook_link.data,
        website = form.website_link.data, seeking_description = form.seeking_description.data, seeking_talent = form.seeking_talent.data
      )
      for item in enumerate(form.genres.data):
        if item[0] != (len(form.genres.data) - 1):
          data.genres += item[1] + ', '
        else:
          data.genres += item[1]
      db.session.add(data)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    finally:
      db.session.close()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # If there is any invalid field
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE','POST','GET'])
def delete_venue(venue_id):
  print("venue_id", venue_id)
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      data_delete_id = venue_id
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.query(Show).filter_by(venue_id = data_delete_id).delete()
      db.session.commit()
      flash('Venue ' + str(venue_id) + ' was successfully removed!')
  except():
    print(sys.exc_info())
    db.session.rollback()
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect('/')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data_list = Artist.query.order_by(db.asc(Artist.id)).all()
  data = []
  for item in data_list:
    data.append({
      'id': item.id,
      'name': item.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artist_list = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  response = {
    "count": len(artist_list),
    "data": [],
    "num_upcoming_shows": 0
  }

  for artist in artist_list:
    response["data"].append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  past_shows = []
  upcoming_shows = []
  artist = Artist.query.get_or_404(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  for show in artist.shows:
    temp_show = {
        'venue_id': show.venue_id,
        'venue_name': Venue.query.get_or_404(show.venue_id).name,
        'venue_image_link': Venue.query.get_or_404(show.venue_id).image_link,
        'start_time': dateutil.parser.parse(show.start_time).strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= current_date:
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist = Artist.query.filter_by(id = artist_id).all()[0]
  artist={
    "id": edit_artist.id,
    "name": edit_artist.name,
    "genres": edit_artist.genres.split(", "),
    "city": edit_artist.city,
    "state": edit_artist.state,
    "phone": edit_artist.phone,
    "website": edit_artist.website,
    "facebook_link": edit_artist.facebook_link,
    "seeking_venue": edit_artist.seeking_venue,
    "seeking_description":  edit_artist.seeking_description,
    "image_link": edit_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm(
    name = artist["name"], genres = artist["genres"], city = artist["city"],
    state = artist["state"], phone = artist["phone"], website_link = artist["website"],
    facebook_link = artist["facebook_link"], seeking_venue = artist["seeking_venue"],
    seeking_description = artist["seeking_description"], image_link = artist["image_link"]
  )
  return render_template('forms/edit_artist.html', form=form, artist=artist)

#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    submit_form = ArtistForm(request.form)
    edit_data = Artist.query.get(artist_id)
    edit_data.name = submit_form.name.data
    edit_data.genres = str(", ").join(submit_form.genres.data)
    edit_data.city = submit_form.city.data
    edit_data.state = submit_form.state.data
    edit_data.phone = submit_form.phone.data
    edit_data.website = submit_form.website_link.data
    edit_data.facebook_link = submit_form.facebook_link.data
    edit_data.seeking_venue = submit_form.seeking_venue.data
    edit_data.seeking_description = submit_form.seeking_description.data
    edit_data.image_link = submit_form.image_link.data
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = Venue.query.filter_by(id = venue_id).all()[0]
  venue={
    "id": edit_venue.id,
    "name": edit_venue.name,
    "genres": edit_venue.genres.split(", "),
    "address": edit_venue.address,
    "city": edit_venue.city,
    "state": edit_venue.state,
    "phone": edit_venue.phone,
    "website": edit_venue.website,
    "facebook_link": edit_venue.facebook_link,
    "seeking_talent": edit_venue.seeking_talent,
    "seeking_description":  edit_venue.seeking_description,
    "image_link": edit_venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm(
    name = venue["name"], genres = venue["genres"], address = venue["address"], city = venue["city"],
    state = venue["state"], phone = venue["phone"], website_link = venue["website"],
    facebook_link = venue["facebook_link"], seeking_talent = venue["seeking_talent"], 
    seeking_description = venue["seeking_description"], image_link = venue["image_link"]
  )
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    submit_form = VenueForm(request.form)
    edit_data = Venue.query.get(venue_id)
    edit_data.name = submit_form.name.data
    edit_data.genres = str(", ").join(submit_form.genres.data)
    edit_data.address = submit_form.address.data
    edit_data.city = submit_form.city.data
    edit_data.state = submit_form.state.data
    edit_data.phone = submit_form.phone.data
    edit_data.website = submit_form.website_link.data
    edit_data.facebook_link = submit_form.facebook_link.data
    edit_data.seeking_talent = submit_form.seeking_talent.data
    edit_data.seeking_description = submit_form.seeking_description.data
    edit_data.image_link = submit_form.image_link.data
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Artist record in the db, instead
  # Set the FlaskForm
  form = ArtistForm(request.form, meta={'csrf': False})
  # Validate all fields
  if form.validate():
    # Prepare for transaction
    try:
      data = Artist(
        name = form.name.data, city = form.city.data, state = form.state.data, phone = form.phone.data, genres = '',
        image_link = form.image_link.data, facebook_link = form.facebook_link.data, website = form.website_link.data,
        seeking_description = form.seeking_description.data, seeking_venue = form.seeking_venue.data
      )
      for item in enumerate(form.genres.data):
        if item[0] != (len(form.genres.data) - 1):
          data.genres += item[1] + ', '
        else:
          data.genres += item[1]
      db.session.add(data)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # If there is any invalid field
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_list = Show.query.all()
  # Process the shows_list and construct the data
  data = []
  for show in shows_list:
    venue = Venue.query.get_or_404(show.venue_id)
    artist = Artist.query.get_or_404(show.artist_id)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name if venue else None,
      "artist_id": show.artist_id,
      "artist_name": artist.name if artist else None,
      "artist_image_link": artist.image_link if artist else None,
      "start_time": show.start_time
    }) 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # TODO: insert form data as a new Show record in the db, instead
  # Set the FlaskForm
  form = ShowForm(request.form, meta={'csrf': False})
  # Validate all fields
  if form.validate():
    # Prepare for transaction
    try:
      data = Show(
        artist_id = form.artist_id.data, venue_id = form.venue_id.data, start_time = form.start_time.data
      )
      db.session.add(data)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()

    flash('Show was successfully listed!')
    return render_template('pages/home.html')

  # If there is any invalid field
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

# Function to errorhandler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
