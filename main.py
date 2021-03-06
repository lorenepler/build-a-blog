#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Posting(db.Model):
    title = db.StringProperty(required = True)
    posting = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", posting=""):
        postings = db.GqlQuery("SELECT * FROM Posting ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, posting=posting, postings=postings)

    def get(self):
        self.render_front()

class NewPostPage(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        posting = self.request.get("posting")

        if title and posting:
            a = Posting(title = title, posting = posting)
            a.put()

            #blog_post_page = posting.key().id()
            #self.redirect("/blog/" + str(posting.key().id()) )
            blog_post_page = a.key().id()
            self.redirect("/blog/" + str(blog_post_page))
        else:
            error = "Please enter a title and a body to your blog post."
            ##self.render_front(title, posting, error)
            self.render("newpost.html", title=title, posting=posting, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
    #    self.response.write(id)

#    def post(self):
        blog_post = Posting.get_by_id( int(id))
        title = blog_post.title
        posting = blog_post.posting

        self.render("single-posting.html", title=title, posting=posting)
        #self.response.write("<h2>" + blog_post.title + "</h2>" + "<br>" + blog_post.posting)
        #self.response.write(<p>3Test</p>)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPostPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
