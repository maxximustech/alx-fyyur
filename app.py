# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(250), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(250), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venues = Venue.query.with_entities(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    current_time = datetime.now()
    for venue in venues:
        venues_in_city = Venue.query.with_entities(Venue.id, Venue.name).filter_by(city=venue[0]).filter_by(
            state=venue[1])
        v_dic = []
        for v in venues_in_city:
            sc = Show.query.filter_by(venue_id=v.id).filter(Show.start_time > current_time).count()
            v_dic.append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": sc
            })
        data.append({"city": venue[0], "state": venue[1], "venues": v_dic})
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    key = request.form.get('search_term', '')

    query = Venue.query.filter(Venue.name.ilike("%" + key + "%")).all()
    count = Venue.query.filter(Venue.name.ilike("%" + key + "%")).count()
    current_time = datetime.now()
    vs = []
    for v in query:
        vs.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": Show.query.filter_by(venue_id=v.id).filter(Show.start_time > current_time).count()
        })

    response = {
        "count": count,
        "data": vs
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).one()
    all_shows = venue.shows
    current_time = datetime.now()
    past_shows = []
    upcoming_shows = []
    for show in all_shows:
        arr = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(arr)
        else:
            past_shows.append(arr)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
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
    # TODO: modify data to be the data object returned from db insertion
    error = False
    seeking_talent = False
    if request.form.get('seeking_talent', 'n') == 'y':
        seeking_talent = True
    try:
        venue = Venue(
            name=request.form.get('name', ''),
            city=request.form.get('city', ''),
            state=request.form.get('state', ''),
            address=request.form.get('address', ''),
            phone=request.form.get('phone', ''),
            image_link=request.form.get('image_link', ''),
            genres=request.form.get('genres', ''),
            facebook_link=request.form.get('facebook_link', ''),
            website=request.form.get('website_link', ''),
            seeking_talent=seeking_talent,
            description=request.form.get('seeking_description', ''),
        )

        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    error = False
    name = venue_id
    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        name = venue.name
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
    else:
        flash('Venue ' + name + ' was successfully deleted!')

    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artist_all = Artist.query.all()
    for artist in artist_all:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    keyword = request.form.get('search_term', '')

    query = Artist.query.filter(Artist.name.ilike("%" + keyword + "%")).all()
    count = Artist.query.filter(Artist.name.ilike("%" + keyword + "%")).count()
    current_time = datetime.now()
    arts = []
    for a in query:
        arts.append({
            "id": a.id,
            "name": a.name,
            "num_upcoming_shows": Show.query.filter_by(artist_id=a.id).filter(Show.start_time > current_time).count()
        })

    response = {
        "count": count,
        "data": arts
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id=artist_id).one()
    all_shows = artist.shows
    current_time = datetime.now()
    past_shows = []
    upcoming_shows = []
    for show in all_shows:
        arr = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(arr)
        else:
            past_shows.append(arr)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    data = Artist.query.filter_by(id=artist_id).one()
    artist = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres,
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website": data.website,
        "facebook_link": data.facebook_link,
        "seeking_venue": data.seeking_venue,
        "seeking_description": data.description,
        "image_link": data.image_link
    }
    form = ArtistForm()
    form.name.data = data.name
    form.genres.data = data.genres
    form.city.data = data.city
    form.state.data = data.state
    form.phone.data = data.phone
    form.website_link.data = data.website
    form.facebook_link.data = data.facebook_link
    form.seeking_venue.data = data.seeking_venue
    form.seeking_description.data = data.description
    form.image_link.data = data.image_link
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False
    seeking_venue = False
    if request.form.get('seeking_venue', 'n') == 'y':
        seeking_venue = True
    try:
        artist = Artist.query.filter_by(id=artist_id).one()
        artist.name = request.form.get('name', '')
        artist.genres = request.form.get('genres', '')
        artist.city = request.form.get('city', '')
        artist.state = request.form.get('state', '')
        artist.phone = request.form.get('phone', '')
        artist.website = request.form.get('website_link', '')
        artist.facebook_link = request.form.get('facebook_link', '')
        artist.seeking_venue = seeking_venue
        artist.description = request.form.get('seeking_description', '')
        artist.image_link = request.form.get('image_link', '')
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.filter_by(id=venue_id).one()
    venue = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres,
        "address": data.address,
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website_link": data.website,
        "facebook_link": data.facebook_link,
        "seeking_talent": data.seeking_talent,
        "seeking_description": data.description,
        "image_link": data.image_link
    }
    form.name.data = data.name
    form.genres.data = data.genres
    form.address.data = data.address
    form.city.data = data.city
    form.state.data = data.state
    form.phone.data = data.phone
    form.website_link.data = data.website
    form.facebook_link.data = data.facebook_link
    form.seeking_talent.data = data.seeking_talent
    form.seeking_description.data = data.description
    form.image_link.data = data.image_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    seeking_talent = False
    if request.form.get('seeking_talent', 'n') == 'y':
        seeking_talent = True
    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        venue.name = request.form.get('name', '')
        venue.genres = request.form.get('genres', '')
        venue.address = request.form.get('address', '')
        venue.city = request.form.get('city', '')
        venue.state = request.form.get('state', '')
        venue.phone = request.form.get('phone', '')
        venue.website = request.form.get('website_link', '')
        venue.facebook_link = request.form.get('facebook_link', '')
        venue.seeking_talent = seeking_talent
        venue.description = request.form.get('seeking_description', '')
        venue.image_link = request.form.get('image_link', '')
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    seeking_venue = False
    if request.form.get('seeking_venue', 'n') == 'y':
        seeking_venue = True
    try:
        artist = Artist(
            name=request.form.get('name', ''),
            city=request.form.get('city', ''),
            state=request.form.get('state', ''),
            phone=request.form.get('phone', ''),
            image_link=request.form.get('image_link', ''),
            genres=request.form.get('genres', ''),
            facebook_link=request.form.get('facebook_link', ''),
            website=request.form.get('website_link', ''),
            seeking_venue=seeking_venue,
            description=request.form.get('seeking_description', ''),
        )

        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    show_all = Show.query.order_by(Show.start_time.asc()).all()
    data = []
    for show in show_all:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    error = False
    try:
        show = Show(start_time=request.form.get('start_time', datetime.now()))
        artist = Artist.query.filter_by(id=request.form.get('artist_id', '')).one()
        venue = Venue.query.filter_by(id=request.form.get('venue_id', '')).one()
        show.artist = artist
        show.venue = venue
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    # on successful db insert, flash success
    #flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

db.create_all()

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
