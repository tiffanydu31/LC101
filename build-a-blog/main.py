import webapp2
import os
import jinja2

from google.appengine.ext import db

# global variables: number of blogs displayed on each page
blogsPageLimit = 5

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(template_dir),
    autoescape=True
)

# retrieve blogs from database
def get_post(limit, offset):
    blogs = db.GqlQuery("SELECT * from Blog ORDER BY created desc LIMIT {} OFFSET {}".format(limit, offset))
    return blogs

# rendering, content handling
class Handler(webapp2.RequestHandler):
    def render_page(self, template, **kw):
        t = jinja_env.get_template(template)
        content = t.render(kw)
        self.response.write(content)

# define blog database
class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

# main page - list of blogs
class Main(Handler):
    def get(self):

        # get page number
        page = 1
        if self.request.get("page").isdigit():
            page = int(self.request.get("page"))

        # get offset and blogs for current page
        offset = (page - 1) * blogsPageLimit
        blogs = get_post(blogsPageLimit, offset)

        # get previous link url, hide link if no previous page
        previousLink = "/blog?page={}".format(page - 1)
        previousPage = "Previous Page"
        if page == 1:
            previousPage = ""
            previousLink = "/blog"

        # get next page url, hide if no next page
        nextLink = "/blog?page={}".format(page + 1)
        nextPage = "Next Page"
        if blogs.count(offset = offset + 1, limit = blogsPageLimit) < blogsPageLimit:
            nextPage = ""
            nextLink = "/blog?page={}".format(page)

        # set space between previous and next page links, hide if not needed
        space = "&nbsp;&nbsp; | &nbsp;&nbsp;"
        if previousPage == "" or nextPage == "":
            space = ""

        self.render_page("front.html", blogs=blogs, previousLink = previousLink,
            previousPage = previousPage, space = space,
            nextLink = nextLink, nextPage = nextPage)

# new post - empty post form
class NewPost(Handler):
    def get(self):
        self.render_page("newpost.html", title = "", body = "", error="")

    def post(self):
        title = self.request.get('title')
        body = self.request.get('body')

        if title and body:
            a = Blog(title = title, body = body)
            a.put()
            id = a.key().id()
            self.redirect("/blog/{}".format(id))
        else:
            error = ("you need both a title and body!")
            self.render_page("newpost.html", title = title, body = body, error = error)

# existing blog display handler
class BlogPost(Handler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("This blog cannot be found in the database...")

    def get(self, id):
        blog = Blog.get_by_id(long(id))
        if blog:
            self.render_page("blog.html", blog=blog)
        else:
            self.renderError(400)

class Base(Handler):
    def get(self):
        self.render_page("base.html")

app = webapp2.WSGIApplication([
    ('/', Base),
    ('/blog', Main),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', BlogPost)
], debug=True)
