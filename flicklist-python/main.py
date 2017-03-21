import webapp2
import random

class Index(webapp2.RequestHandler):

    def getRandomMovie(self):

        # TODO: make a list with at least 5 movie titles
        movies = [
            "Usual Suspects", "Titanic", "Inception", "Dr. Strange", "Tangled"
        ]

        # TODO: randomly choose one of the movies, and return it
        return movies[random.randint(0, 4)]

    def get(self):
        # choose a movie by invoking our new function
        movieToday = self.getRandomMovie()
        movieTomorrow = self.getRandomMovie()

        # build the response string
        content = "<h1>Movie of the Day</h1>"
        content += "<p>" + movieToday + "</p>"
        content += "<h1>Tomorrow's Showing</h1>"
        content += "<p>" + movieTomorrow + "</p>"

        # TODO: pick a different random movie, and display it under
        # the heading "<h1>Tommorrow's Movie</h1>"

        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index)
], debug=True)
