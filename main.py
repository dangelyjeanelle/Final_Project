import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users

jinja_env=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)
class MainPage(webapp2.RequestHandler):
    def get(self):
        # name=self.request.get("name") or "World"
        # mov= Movie.query().fetch()
        # st=Star.query().fetch()
        # sta={
        # }
        # usr=users.get_current_user()
        # signin_link=users.create_login_url("/")
        # for star in st:
        #     sta.update({star.name:star})
        #
        template=jinja_env.get_template("templates/home.html")
        self.response.write(template.render())


class Product(ndb.Model):
    name=ndb.StringProperty(required=True)
    description=ndb.StringProperty(required=True)
    seller=ndb.KeyProperty(required=True)
    category=ndb.StringProperty(required=False)
    
class User(ndb.Model):
    username=ndb.StringProperty(required=True)
    userid=ndb.IntegerProperty(required=True)
    products=ndb.KeyProperty(required=False, repeated=True)
    email=ndb.StringProperty(required=True)

class ProductPage(webapp2.RequestHandler):
    def get(self):
        spiderverse= Movie(title="Spider-Man: Into the Spider-Verse",runtime=117,rating=8.5,star_names=["Shameik Moore", "Jake Johnson", "Hailee Steinfeld"])
        shameik= Star(name="Shameik Moore",dob="05-04-1995",awards=2,worth=1)
        jake= Star(name="Jake Johnson",dob="05-28-1978",awards=1,worth=8)
        hail= Star(name="Hailee Steinfeld",dob="12-11-1996",awards=24,worth=8)
        shameik.put()
        jake.put()
        hail.put()
        spiderverse.put()
        template=jinja_env.get_template("templates/pop.html")
        self.response.write(template.render())
        self.redirect("/")

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        name=self.request.get("name") or "World"
        sta=[]
        for star in Star.query().fetch():
            sta.append(Star(name=star.name,dob=star.dob,worth=star.worth, awards=star.awards))
        template_vars={
        "name":name,
        "stars":sta
        }
        template=jinja_env.get_template("templates/stars.html")
        self.response.write(template.render(template_vars))

class ExchangePage(webapp2.RequestHandler):
    def get(self):
        name=self.request.get("name") or "World"
        sta=[]
        for star in Star.query().fetch():
            sta.append(Star(name=star.name,dob=star.dob,worth=star.worth, awards=star.awards))
        template_vars={
        "name":name,
        "stars":sta
        }
        template=jinja_env.get_template("templates/stars.html")
        self.response.write(template.render(template_vars))
class AddPage(webapp2.RequestHandler):
    def get(self):

        template=jinja_env.get_template("templates/add.html")
        self.response.write(template.render())

class SignUpPage(webapp2.RequestHandler):
    def get(self):

        template=jinja_env.get_template("templates/stars.html")
        self.response.write(template.render())


app=webapp2.WSGIApplication([
    ("/", MainPage),
    ("/product", ProductPage),
    ("/profile", ProfilePage),
    ("/exchange", ExchangePage),
    ("/add", AddPage),
    ("/signup", SignUpPage),
], debug=True)
