import webapp2
import jinja2
import json
import os
import urllib
from google.appengine.api import app_identity
from google.appengine.api import mail
import base64
from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import urlfetch

jinja_env=jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

def send_request_mail(product1_key, product2_key):
    # pr1=seller   pr2=buyer
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product1_key.get().seller.get().nickname,
                   subject="Your have a trade request!",
                   body="Dear "+product1_key.get().seller.get().name+""":
    You got a trade request from"""+product2_key.get().seller.get().name+""" on UpTrade. You can now visit
https://up-trade.appspot.com/exchange? and sign in using your Google Account to access new features.
Please let us know if you have any questions.
The example.com Team
""")

class Product(ndb.Model):
    name=ndb.StringProperty(required=True)
    description=ndb.StringProperty(required=True)
    seller=ndb.KeyProperty(required=False)
    category=ndb.StringProperty(required=False)
    photo=ndb.BlobProperty(required=True)

class UptradeUser(ndb.Model):
    name=ndb.StringProperty(required=True)
    # userid=ndb.IntegerProperty(required=True)
    products=ndb.KeyProperty(kind=Product, required=False, repeated=True)
    # email=ndb.StringProperty(required=True)
    avatar=ndb.BlobProperty(required=False)

class Exchange(ndb.Model):
    product1=ndb.KeyProperty(required=True)
    product2=ndb.KeyProperty(required=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        # Read the "category" URL parameter
        category=self.request.get("category")

        # Based on the category, filter the Product query
        if category:
            pro=Product.query().filter(ndb.StringProperty("category")==category).fetch()
        else:
            pro=Product.query().fetch()

        user=users.get_current_user()
        if user:
            email_address=user.nickname()
            uptrade_user=UptradeUser.get_by_id(user.user_id())
            signout_link_html='<a href="%s">Sign out</a>' % (users.create_logout_url("/"))
            if uptrade_user:
                self.response.write('''Welcome %s! <br> %s <br>''' % (
              uptrade_user.name,
              signout_link_html))
            else:
                self.redirect("/signup")
        else:
            self.response.write('''
        Please log in! <br>
        <a href="%s">Sign in</a>''' % (
          users.create_login_url('/')))
        signin_link=users.create_login_url("/")
        template_vars={
            "current_user":user,
            "signin_link":signin_link,
            "products":pro,
            "title": category,
        }
        template=jinja_env.get_template("templates/home.html")
        self.response.write(template.render(template_vars))
    def post(self):
        user=users.get_current_user()
        if not user:
            self.error(500)
            return
        uptrade_user=UptradeUser(name=self.request.get("name"),avatar=images.resize(self.request.get("pic"),100,100),id=user.user_id())
        uptrade_user.put()
        self.redirect("/")
        # self.response.write("Thanks for signing up, %s!" % uptrade_user.name)


class Image(webapp2.RequestHandler):
    def get(self):
        product=ndb.Key(urlsafe=self.request.get("img_id")).get()
        if product.photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(product.photo)
        else:
            self.response.out.write('No image')


class ProductPage(webapp2.RequestHandler):
    def get(self):
        if self.request.get("id"):
            urlsafe_key=self.request.get("id")
            key=ndb.Key(urlsafe=urlsafe_key)
            product=Product.query().filter(Product.key==key).get()
            template_vars={
            "product":product
            }
            template=jinja_env.get_template("templates/product.html")
            self.response.write(template.render(template_vars))
        else:
            self.redirect("/")

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        email_address=user.nickname()
        uptrade_user=UptradeUser.get_by_id(user.user_id())
        encoded_string = base64.b64encode(uptrade_user.avatar).strip('\n')
        template_vars = {
            "user": uptrade_user.name,
            "image": encoded_string,
            "email_address": email_address,
            "title": "Profile",
            "active_page": "Profile",
        }
        template=jinja_env.get_template("templates/profile.html")
        # self.response.out.write('<div><img src="/img?img_id=%s"></img>' %
        #                 uptrade_user.avatar.urlsafe())
        self.response.write(template.render(template_vars))

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
        Product(
        name=self.request.get("nam"),
        description=self.request.get("desc"),
        photo=images.resize(self.request.get("pic"),250,250),
        category=self.request.get("cat"),
        seller=UptradeUser.get_by_id(users.get_current_user().user_id()).put()).put()
        template=jinja_env.get_template("templates/added.html")
        self.response.write(template.render())
        self.redirect("/")

class SignUpPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/signup.html")
        self.response.write(template.render())
    def post(self):
        UptradeUser(name=self.request.get("name"),avatar=images.resize(self.request.get("pic"),250,250)).put()
        template=jinja_env.get_template("templates/added.html")
        self.response.write(template.render())
        self.redirect("/profile")

class TestPage(webapp2.RequestHandler):
    def get(self):
        send_approved_mail()
        self.response.content_type = 'text/plain'
        self.response.write('Sent an email.')

app=webapp2.WSGIApplication([
    ("/", MainPage),
    ("/product", ProductPage),
    ("/profile", ProfilePage),
    ("/exchange", ExchangePage),
    ("/add", AddPage),
    ("/signup", SignUpPage),
    ("/img", Image),
    ("/test", TestPage),
], debug=True)
