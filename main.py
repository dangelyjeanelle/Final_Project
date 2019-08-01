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

def send_request_mail(exchange_key):
    product1=exchange_key.get().product1
    product2=exchange_key.get().product2
    url="https://up-trade.appspot.com/review?"+str(exchange_key.urlsafe())
    body = """Dear %s:\n You got a trade request from %s on UpTrade. You can now visit %s to accept or decline the trading offer.\n\nThe UpTrade Team""" % (product1.get().seller.get().name, product2.get().seller.get().name, url)
    html= """Dear %s:<br> &nbsp; You got a trade request from %s on UpTrade. You can now visit <a href="%s">UpTrade</a> to accept or decline the trading offer.<br><br>The UpTrade Team""" % (product1.get().seller.get().name, product2.get().seller.get().name, url)
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product1.get().seller.get().email,
                   subject="Your have a trade request!",
                   body=body,html=html)

def send_accepted_mail(exchange_key):
    product1=exchange_key.get().product1
    product2=exchange_key.get().product2
    url="https://up-trade.appspot.com/exchange?"+str(exchange_key.urlsafe())
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product1.get().seller.get().email,
                   subject="Your have a trade request!",
                   body="Dear "+product1.get().seller.get().name+""":
    You got a trade request from"""+product2.get().seller.get().name+""" on UpTrade. You can now visit """+url+""" to accept or decline the trading offer.
The UpTrade Team
""")

def send_declined_mail(exchange_key):
    product1=exchange_key.get().product1
    product2=exchange_key.get().product2
    url="https://up-trade.appspot.com/exchange?"+str(exchange_key.urlsafe())
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product1.get().seller.get().email,
                   subject="Your have a trade request!",
                   body="Dear "+product1.get().seller.get().name+""":
    You got a trade request from"""+product2.get().seller.get().name+""" on UpTrade. You can now visit """+url+""" to accept or decline the trading offer.
The UpTrade Team
""")

class Product(ndb.Model):
    name=ndb.StringProperty(required=True)
    description=ndb.StringProperty(required=True)
    seller=ndb.KeyProperty(kind="UptradeUser", required=True)
    category=ndb.StringProperty(required=False)
    photo=ndb.BlobProperty(required=True)

class UptradeUser(ndb.Model):
    name=ndb.StringProperty(required=True)
    # id=ndb.IntegerProperty(required=True)
    products=ndb.KeyProperty(kind=Product, required=False, repeated=True)
    email=ndb.StringProperty(required=True)
    avatar=ndb.BlobProperty(required=False)

class Exchange(ndb.Model):
    product1=ndb.KeyProperty(kind=Product,required=True)
    product2=ndb.KeyProperty(kind=Product,required=True)

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
            email_address=user.email()
            print "user id is:", user.user_id()
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
        else:
            uptrade_user=UptradeUser(id=users.get_current_user().user_id(),name=self.request.get("name"),avatar=images.resize(self.request.get("pic"),100,100),email=users.get_current_user().email())
            uptrade_user.put()
            self.redirect("/")


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
            current_user=UptradeUser.get_by_id(users.get_current_user().user_id())
            key=ndb.Key(urlsafe=urlsafe_key)
            product=Product.query().filter(Product.key==key).get()
            template_vars={
            "product":product,
            "current_user":current_user
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
        self.response.write(template.render(template_vars))

class ExchangePage(webapp2.RequestHandler):
    def get(self):
        if self.request.get("p"):
            urlsafe_p=self.request.get("p")
            p=ndb.Key(urlsafe=urlsafe_p)
            user=UptradeUser.get_by_id(users.get_current_user().user_id())
            exchange=Exchange()
            template_vars={
            "product1":p,
            "current_user":user
            }
            template=jinja_env.get_template("templates/exchange.html")
            self.response.write(template.render(template_vars))
        else:
            self.redirect("/")

class AddPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/add.html")
        self.response.write(template.render())
    def post(self):
        user=UptradeUser.get_by_id(users.get_current_user().user_id())
        new=Product(
        name=self.request.get("nam"),
        description=self.request.get("desc"),
        photo=images.resize(self.request.get("pic"),350,350),
        category=self.request.get("cat"),
        seller=user.put()).put()
        user.products.append(new)
        user.put()
        template=jinja_env.get_template("templates/added.html")
        self.response.write(template.render())
        self.redirect("/")

class SignUpPage(webapp2.RequestHandler):
    def get(self):
        template=jinja_env.get_template("templates/signup.html")
        self.response.write(template.render())

class SentPage(webapp2.RequestHandler):
    def get(self):
        product1=self.request.get("p1")
        product2=self.request.get("p2")
        p1=ndb.Key(urlsafe=product1)
        p2=ndb.Key(urlsafe=product2)
        new=Exchange(product1=p1,product2=p2)
        new_key=new.put()
        send_request_mail(new_key)
        template_vars={
        "p1":p1,
        "p2":p2,
        }
        template=jinja_env.get_template("templates/sent.html")
        self.response.write(template.render(template_vars))

class ReviewPage(webapp2.RequestHandler):
    def get(self):
        urlsafe_exchange=self.request.get("e")
        e_key=ndb.Key(urlsafe=urlsafe_exchange)
        exchange=e_key.get()
        template_vars={
        "exchange":exchange
        }
        template=jinja_env.get_template("templates/sent.html")
        self.response.write(template.render(template_vars))

app=webapp2.WSGIApplication([
    ("/", MainPage),
    ("/product", ProductPage),
    ("/profile", ProfilePage),
    ("/exchange", ExchangePage),
    ("/add", AddPage),
    ("/signup", SignUpPage),
    ("/img", Image),
    ("/sent", SentPage),
    ("/review", ReviewPage),
], debug=True)
