import webapp2
import jinja2
import json
import os
import urllib
import base64
from google.appengine.api import app_identity
from google.appengine.api import mail
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
    url="https://up-trade.appspot.com/review?e="+str(exchange_key.urlsafe())
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
    url="https://up-trade.appspot.com/"
    body1 = """Dear %s:\n %s has accepted your trade request on UpTrade, so the product you traded is no longer available on the UpTrade page. You can now contact (%s) to finalize the trade and choose the most convenient shipping methods for you and your traded products. Visit %s to continue trading with us.\n\nThe UpTrade Team""" % (product2.get().seller.get().name, product1.get().seller.get().name,product1.get().seller.get().email, url)
    html1 = """Dear %s:<br> &nbsp; %s has accepted your trade request on UpTrade, so the product you traded is no longer available on the UpTrade page. You can now contact (%s) to finalize the trade and choose the most convenient shipping methods for you and your traded products. Visit <a href="%s">UpTrade</a> to continue trading with us.<br><br>The UpTrade Team""" % (product2.get().seller.get().name, product1.get().seller.get().name,product1.get().seller.get().email, url)
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product2.get().seller.get().email,
                   subject="Your trading offer was accepted!",
                   body=body1,html=html1)
    body2 = """Dear %s:\n You have accepted a trade request from %s on UpTrade, so the product you traded is no longer available on the UpTrade page. You can now contact (%s) to finalize the trade and choose the most convenient shipping methods for you and your traded products. Visit %s to continue trading with us.\n\nThe UpTrade Team""" % (product1.get().seller.get().name, product2.get().seller.get().name,product2.get().seller.get().email, url)
    html2 = """Dear %s:<br> &nbsp; You have accepted a trade request from %s on UpTrade, so the product you traded is no longer available on the UpTrade page. You can now contact (%s) to finalize the trade and choose the most convenient shipping methods for you and your traded products. Visit <a href="%s">UpTrade</a> to continue trading with us.<br><br>The UpTrade Team""" % (product1.get().seller.get().name, product2.get().seller.get().name,product2.get().seller.get().email, url)
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product1.get().seller.get().email,
                   subject="You accepted a trading offer!",
                   body=body2,html=html2)

def send_declined_mail(exchange_key):
    product1=exchange_key.get().product1
    product2=exchange_key.get().product2
    url="https://up-trade.appspot.com/"
    body1 = """Dear %s:\n Unfortunately, %s has declined your trade request on UpTrade, but there are many more products and traders waiting for you in our page. Visit %s to continue trading with us.\n\nThe UpTrade Team""" % (product2.get().seller.get().name, product1.get().seller.get().name, url)
    html1 = """Dear %s:<br> &nbsp; Unfortunately, %s has declined your trade request on UpTrade, but there are many more products and traders waiting for you in our page Visit <a href="%s">UpTrade</a> to continue trading with us.<br><br>The UpTrade Team""" % (product2.get().seller.get().name, product1.get().seller.get().name, url)
    mail.send_mail(sender='UpTrade@up-trade.appspotmail.com'.format(
        app_identity.get_application_id()),
                   to=product2.get().seller.get().email,
                   subject="Your trading offer was declined",
                   body=body1,html=html1)

class Product(ndb.Model):
    name=ndb.StringProperty(required=True)
    description=ndb.StringProperty(required=True)
    seller=ndb.KeyProperty(kind="UptradeUser", required=True)
    category=ndb.StringProperty(required=True)
    photo=ndb.BlobProperty(required=True)

class UptradeUser(ndb.Model):
    name=ndb.StringProperty(required=True)
    # id=ndb.IntegerProperty(required=True)
    products=ndb.KeyProperty(kind=Product, required=False, repeated=True)
    email=ndb.StringProperty(required=True)
    avatar=ndb.BlobProperty(required=True)

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
        important=""
        sec=""
        if user:
            uptrade_user=UptradeUser.get_by_id(user.user_id())
            signout_link=users.create_logout_url("/")
            if uptrade_user:
                important=signout_link
                sec="out"
            else:
                self.redirect("/signup")
        else:
            important=users.create_login_url("/")
            sec="in"
        template_vars={
            "current_user":user,
            "important":important,
            "products":pro,
            "title": category,
            "sec":sec
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
            important=users.create_logout_url("/")
            urlsafe_key=self.request.get("id")
            current_user=UptradeUser.get_by_id(users.get_current_user().user_id())
            key=ndb.Key(urlsafe=urlsafe_key)
            product=Product.query().filter(Product.key==key).get()
            template_vars={
            "product":product,
            "current_user":current_user,
            "important":important
            }
            template=jinja_env.get_template("templates/product.html")
            self.response.write(template.render(template_vars))
        else:
            self.redirect("/")

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        email_address=user.email()
        important=users.create_logout_url("/")
        uptrade_user=UptradeUser.get_by_id(user.user_id())
        encoded_string = base64.b64encode(uptrade_user.avatar).strip('\n')
        template_vars = {
            "user": uptrade_user.name,
            "image": encoded_string,
            "email_address": email_address,
            "title": "Profile",
            "active_page": "Profile",
            "important":important
        }
        template=jinja_env.get_template("templates/profile.html")
        self.response.write(template.render(template_vars))

class ExchangePage(webapp2.RequestHandler):
    def get(self):
        if self.request.get("p"):
            important=users.create_logout_url("/")
            urlsafe_p=self.request.get("p")
            p=ndb.Key(urlsafe=urlsafe_p)
            user=UptradeUser.get_by_id(users.get_current_user().user_id())
            exchange=Exchange()
            template_vars={
            "product1":p,
            "current_user":user,
            "important":important
            }
            template=jinja_env.get_template("templates/exchange.html")
            self.response.write(template.render(template_vars))
        else:
            self.redirect("/")

class AddPage(webapp2.RequestHandler):
    def get(self):
        important=users.create_logout_url("/")
        template_vars={
        "important":important
        }
        template=jinja_env.get_template("templates/add.html")
        self.response.write(template.render(template_vars))
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
        self.redirect("/")

class SignUpPage(webapp2.RequestHandler):
    def get(self):
        important=users.create_logout_url("/")
        template_vars={
        "important":important
        }
        template=jinja_env.get_template("templates/signup.html")
        self.response.write(template.render(template_vars))

class SentPage(webapp2.RequestHandler):
    def get(self):
        important=users.create_logout_url("/")
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
        "important":important
        }
        template=jinja_env.get_template("templates/sent.html")
        self.response.write(template.render(template_vars))

class ReviewPage(webapp2.RequestHandler):
    def get(self):
        if self.request.get("e"):
            important=users.create_logout_url("/")
            urlsafe_exchange=self.request.get("e")
            e_key=ndb.Key(urlsafe=urlsafe_exchange)
            exchange=e_key.get()
            template_vars={
            "exchange":exchange,
            "important":important
            }
            template=jinja_env.get_template("templates/review.html")
            self.response.write(template.render(template_vars))
        else:
            self.redirect("/")
    def post(self):
        if self.request.get("offer")=="yes":
            urlsafe_exchange=self.request.get("e")
            e_key=ndb.Key(urlsafe=urlsafe_exchange)
            exchange=e_key.get()
            send_accepted_mail(e_key)
            del exchange.product1.get().seller.get().products[exchange.product1.get().seller.get().products.index(exchange.product1)]
            del exchange.product2.get().seller.get().products[exchange.product2.get().seller.get().products.index(exchange.product2)]
            exchange.product1.get().put()
            exchange.product2.get().put()
            exchange.product1.delete()
            exchange.product2.delete()
        elif self.request.get("offer")=="no":
            send_declined_mail(ndb.Key(urlsafe=self.request.get("e")))
        self.redirect("/")

class DeleteProfile(webapp2.RequestHandler):
    def get(self):
        uptrade_user=UptradeUser.get_by_id(users.get_current_user().user_id())
        for product in uptrade_user.products:
            product.delete()
        uptrade_user.key.delete()
        self.redirect("/")


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
    ("/deleteProfile", DeleteProfile),
], debug=True)
