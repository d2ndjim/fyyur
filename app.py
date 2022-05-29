#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120),nullable=False)
  address = db.Column(db.String(120),nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(300), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120), nullable=False)
  shows = db.relationship('Show', backref='venue', lazy=True)
  
  def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website} {self.shows}>'
  

class Artist(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(300), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  shows = db.relationship('Show', backref='artist', lazy=True)

  def __repr__(self):
    return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.shows}>'

class Show(db.Model):
  _tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.date} {self.artist_id} {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.order_by('city', 'state', 'name').all()
  for venue in venues:
    item = {}
    index = -1
    if len(data) == 0:
      index = 0
      item = {
        "city": venue.city,
        "state": venue.state,
        "venues": []
      }
      data.append(item)
    else:
      for i, item in enumerate(data):
        if item['city'] == venue.city and item['state'] == venue.state:
          index = i
          break
      if index < 0:
        item = {
          "city": venue.city,
          "state": venue.state,
          "venues": []
        }
        data.append(item)
        index = len(data) - 1
      else:
        item = data[index]
    v = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 5
      }
    item['venues'].append(v)
    data[index] = item

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  search = "%{}%".format(search_term.replace(" ", "\ "))
  data = Venue.query.filter(Venue.name.match(search)).order_by('name').all()
  items = []
  for d in data:
    new_item = {
      "id": d.id,
      "name": d.name,
      "num_upcoming_shows": len(d.shows)
    }
    items.append(new_item)

  response={
    "count": len(items),
    "data": items
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).first()
  data.genres = json.loads(data.genres)

  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.date > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  body = {}
  
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    address = request.get_json()['address']
    genres = json.dumps(request.get_json()['genres'])
    facebook_link = request.get_json()['facebook_link']
    image_link = request.get_json()['image_link']
    website = request.get_json()['website']
    
    venue = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'Could not post venue'
  else:
    body['msg'] = 'Venue Posted Successfully'
    body['success'] = True
     
  return jsonify(body)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search = "%{}%".format(search_term.replace(" ", "\ "))
  data = Artist.query.filter(Artist.name.match(search)).order_by('name').all()
  items = []
  for d in data:
    new_item = {
      "id": d.id,
      "name": d.name,
      "num_upcoming_shows": len(d.shows)
    }
    items.append(new_item)
  response={
    "count": len(items),
    "data": items
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first()
  data.genres = json.loads(data.genres)

  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.date > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.image_link.data = artist.image_link
  form.genres.data = json.loads(artist.genres)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  body = {}
  request.get_json()
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = request.get_json()['name']
    artist.city = request.get_json()['city']
    artist.state = request.get_json()['state']
    artist.phone = request.get_json()['phone']
    artist.genres = json.dumps(request.get_json()['genres'])
    artist.facebook_link = request.get_json()['facebook_link']
    artist.website = request.get_json()['website']
    artist.image_link = request.get_json()['image_link']
    
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    # print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'Could not post artist info '
  else:
    body['msg'] = 'Artist Posted Successfully'
    body['success'] = True

  return jsonify(body)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.image_link.data = venue.image_link
  form.genres.data = json.loads(venue.genres)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  body = {}

  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = request.get_json()['name']
    venue.city = request.get_json()['city']
    venue.state = request.get_json()['state']
    venue.phone = request.get_json()['phone']
    venue.address = request.get_json()['address']
    venue.genres = json.dumps(request.get_json()['genres'])
    venue.facebook_link = request.get_json()['facebook_link']
    venue.website = request.get_json()['website']
    venue.image_link = request.get_json()['image_link']

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    # print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'An error occurred '
  else:
    body['msg'] = 'Venue created Successfully'
    body['success'] = True
  
  return jsonify(body)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  body = {}
  
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    genres = json.dumps(request.get_json()['genres'])
    facebook_link = request.get_json()['facebook_link']
    website = request.get_json()['website']
    image_link = request.get_json()['image_link']
    
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website)
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    # print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'An error Occurred '
  else:
    body['msg'] = 'Artist Posted Successfully'
    body['success'] = True

  return jsonify(body)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  rows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter(Show.date > datetime.now()).order_by('date').all()
  data = []
  for row in rows:
    item = {
      'venue_id': row.Venue.id,
      'artist_id': row.Artist.id,
      'venue_name': row.Venue.name,
      'artist_name': row.Artist.name,
      'artist_image_link': row.Artist.image_link,
      'start_time': row.Show.date.strftime('%Y-%m-%d %H:%I')
    }
    data.append(item)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  body = {}

  try:
    artist_id = request.get_json()['artist_id']
    venue_id = request.get_json()['venue_id']
    start_time = request.get_json()['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, date=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    # print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'An error Occurred '
  else:
    body['msg'] = 'Show Posted Successfully'
    body['success'] = True

  return jsonify(body)

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

# # Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
