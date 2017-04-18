import webapp2, cgi, jinja2, os, re
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# a list of movies that nobody should be allowed to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives"
]

allowed_routes = [
    '/login',
    '/register'
]

class User(db.Model):
    """ Represents a user on our site """
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)


class Movie(db.Model):
    """ Represents a movie that a user wants to watch or has watched """
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    watched = db.BooleanProperty(required = True, default = False)
    rating = db.StringProperty()


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def read_cookie(self, name):
        val = self.request.cookie.get(name)
        return val

    def set_cookie(self, name, val):
        self.response.headers.add('Set-Cookie', '{0}={1}; Path=/'.format(name, val))

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

    def get_user_by_name(self, username):
        """ Given a username, try to fetch the user from the database """
        user = db.GqlQuery("SELECT * from User WHERE username = '%s'" % username)
        if user:
            return user.get()

    def login_user(self, user):
        user_id = user.key().id()
        self.set_cookie('user_id', user_id)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = self.request.cookies.get('user_id')
        if user_id:
            user = User.get_by_id(int(user_id))
            self.user = user
        elif self.request.path not in allowed_routes:
                self.redirect('/login')

    def logout_user(self):
        self.set_cookie('user_id', '')


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):
        """ Display the homepage (the list of unwatched movies) """

        # query for all the movies that have not yet been watched
        unwatched_movies = db.GqlQuery("SELECT * FROM Movie WHERE watched = False")

        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        movies = unwatched_movies,
                        error = self.request.get("error"),
                        message = self.request.get("message"))
        self.response.write(content)


class AddMovie(Handler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        """ User wants to add a new movie to their list """

        new_movie_title = self.request.get("new-movie")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_movie_title) or (new_movie_title.strip() == ""):
            error = "Please specify the movie you want to add."
            self.redirect("/?error=" + cgi.escape(error))
            return

        # if the user wants to add a terrible movie, redirect and yell at them
        if new_movie_title in terrible_movies:
            error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie_title)
            self.redirect("/?error=" + cgi.escape(error, quote=True))
            return

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_movie_title_escaped = cgi.escape(new_movie_title, quote=True)

        # construct a movie object for the new movie
        movie = Movie(title = new_movie_title_escaped)
        movie.put()

        # render the confirmation message
        t = jinja_env.get_template("add-confirmation.html")
        content = t.render(movie = movie)
        self.response.write(content)


class WatchedMovie(Handler):
    """ Handles requests coming in to '/watched-it'
        e.g. www.flicklist.com/watched-it
    """

    def post(self):
        """ User has watched a movie. """
        watched_movie_id = self.request.get("watched-movie")
        watched_movie = Movie.get_by_id( int(watched_movie_id) )

        # if we can't find the movie, reject.
        if not watched_movie:
            self.renderError(400)
            return

        # update the movie object to say the user watched it at this date in time
        watched_movie.watched = True
        watched_movie.put()

        # render confirmation page
        t = jinja_env.get_template("watched-it-confirmation.html")
        content = t.render(movie = watched_movie)
        self.response.write(content)


class MovieRatings(Handler):
    """ Handles requests coming in to '/ratings'
    """

    def get(self):
        """ Show a list of the movies the user has already watched """

        # query for movies that have already been watched
        watched_movies = db.GqlQuery("SELECT * FROM Movie WHERE watched = True")

        t = jinja_env.get_template("ratings.html")
        content = t.render(movies = watched_movies)
        self.response.write(content)

    def post(self):
        """ User wants to rate a movie """

        rating = self.request.get("rating")
        movie_id = self.request.get("movie")

        movie = Movie.get_by_id( int(movie_id) )

        if movie and rating:
            # update the rating of the movie object
            movie.rating = rating
            movie.put()

            # render confirmation
            t = jinja_env.get_template("rating-confirmation.html")
            content = t.render(movie = movie)
            self.response.write(content)
        else:
            self.renderError(400)


class Login(Handler):

    def render_login_form(self, error=""):
        t = jinja_env.get_template("login.html")
        content = t.render(error=error)
        self.response.write(content)

    def get(self):
        """ Display the login page """
        self.render_login_form()

    def post(self):
        """ User is trying to log in """
        submitted_username = self.request.get("username")
        submitted_password = self.request.get("password")

        user = self.get_user_by_name(submitted_username)
        if not user:
            self.render_login_form(error = "Invalid username")
            return
        elif submitted_password != user.password:
            self.render_login_form(error = "Invalid password")
            return
        else:
            self.redirect("/?message=Welcome " + user.username + "!")
            self.login_user(user)
            return




class Register(Handler):

    def validate_username(self, username):
        """ Returns the username string untouched if it is valid,
            otherwise returns an empty string
        """
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(username):
            return username
        else:
            return ""

    def validate_password(self, password):
        """ Returns the password string untouched if it is valid,
            otherwise returns an empty string
        """
        PWD_RE = re.compile(r"^.{3,20}$")
        if PWD_RE.match(password):
            return password
        else:
            return ""

    def validate_verify(self, password, verify):
        """ Returns the password verification string untouched if it matches
            the password, otherwise returns an empty string
        """
        if password == verify:
            return verify

    def get(self):
        """ Display the registration page """
        t = jinja_env.get_template("register.html")
        content = t.render(errors={})
        self.response.out.write(content)

    def post(self):
        """ User is trying to register """
        submitted_username = self.request.get("username")
        submitted_password = self.request.get("password")
        submitted_verify = self.request.get("verify")

        username = self.validate_username(submitted_username)
        password = self.validate_password(submitted_password)
        verify = self.validate_verify(submitted_password, submitted_verify)

        errors = {}
        existing_user = self.get_user_by_name(username)
        has_error = False

        if existing_user:
            errors['username_error'] = "A user with that username already exists"
            has_error = True
        elif (username and password and verify):
            # create new user object
            user = User(username=username, password=password)
            user.put()
        else:
            has_error = True

            if not username:
                errors['username_error'] = "That's not a valid username"

            if not password:
                errors['password_error'] = "That's not a valid password"

            if not verify:
                errors['verify_error'] = "Passwords don't match"

        if has_error:
            t = jinja_env.get_template("register.html")
            content = t.render(username=username, errors=errors)
            self.response.out.write(content)
        else:
            self.redirect('/')
            return

class Logout(Handler):
    def get(self):
        self.logout_user()
        self.redirect('/login')


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/watched-it', WatchedMovie),
    ('/ratings', MovieRatings),
    ('/login', Login),
    ('/register', Register),
    ('/logout', Logout)
], debug=True)
