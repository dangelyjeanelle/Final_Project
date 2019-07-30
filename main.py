import webapp2
import jinja2
import json
import os
import urllib
from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import urlfetch

jinja_env=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)
class MainPage(webapp2.RequestHandler):
    def get(self):
        pro=Product.query().fetch()

        usr=users.get_current_user()
        signin_link=users.create_login_url("/")
        template_vars={
        "current_user":usr,
        "signin_link":signin_link,
        "products":pro
        }
        template=jinja_env.get_template("templates/home.html")
        self.response.write(template.render(template_vars))

class Image(webapp2.RequestHandler):
    def get(self):
        product=ndb.Key(urlsafe=self.request.get("img_id")).get()
        if product.photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(product.photo)
        else:
            self.response.out.write('No image')

class Product(ndb.Model):
    name=ndb.StringProperty(required=True)
    description=ndb.StringProperty(required=True)
    seller=ndb.StringProperty(required=False)
    category=ndb.StringProperty(required=False)
    photo=ndb.BlobProperty(required=True)

class User(ndb.Model):
    name=ndb.StringProperty(required=True)
    userid=ndb.IntegerProperty(required=True)
    products=ndb.KeyProperty(kind=Product, required=False, repeated=True)
    email=ndb.StringProperty(required=True)
    avatar=ndb.BlobProperty(required=False)

class ProductPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/product.html")
        self.response.write(template.render())

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/profile.html")
        self.response.write(template.render())

class ExchangePage(webapp2.RequestHandler):
    def get(self):
        # Set up key and url
        api_key="AIzaSyBLIoqzNWJjQ0o_BSnVJ9JoKp34Xas26q0"
        base_url="https://www.googleapis.com/books/v1/volumes"
        params={"q":"Harry Potter",
        "api_key":api_key,}
        full_url=base_url+"?"+urllib.urlencode(params)

        # Fetch url
        books_response=urlfetch.fetch(full_url).content
        # Get JSON response and convert to a python dictionary
        books_dictionary=json.loads(books_response)
        template_vars={
        "books":books_dictionary["items"]
        }
        template=jinja_env.get_template("templates/exchange.html")
        self.response.write(template.render(template_vars))
class AddPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/add.html")
        self.response.write(template.render())
    def post(self):
        Product(name=self.request.get("nam"),description=self.request.get("desc"),photo=images.resize(self.request.get("pic"),250,250), category=self.request.get("cat"),seller=users.get_current_user().nickname()).put()
        template=jinja_env.get_template("templates/added.html")
        self.response.write(template.render())
        self.redirect("/profile")

class SignUpPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/signup.html")
        self.response.write(template.render())
    def post(self):
        User(name=self.request.get("nam"),description=self.request.get("desc"),photo=images.resize(self.request.get("pic"),250,250), category=self.request.get("cat"),seller=users.get_current_user().nickname()).put()
        template=jinja_env.get_template("templates/added.html")
        self.response.write(template.render())
        self.redirect("/profile")

app=webapp2.WSGIApplication([
    ("/", MainPage),
    ("/product", ProductPage),
    ("/profile", ProfilePage),
    ("/exchange", ExchangePage),
    ("/add", AddPage),
    ("/signup", SignUpPage),
    ("/img", Image)
], debug=True)
