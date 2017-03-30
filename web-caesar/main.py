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

import webapp2
import cgi
import caesar

page_header = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Web Caesar</title>
        </head>
        <body>
            <h1>Web Caesar</h1>
    """
page_footer = """
        </body>
    </html>
    """

def build_page(textarea_content):
    rot_label = "<label>Rotate by:</label>"
    rotation_input = "<input type='number' name='rotation'/>"

    message_label = "<label>Type a message</label>"
    textarea = "<textarea name='message'>" + textarea_content + "</textarea>"

    submit = "<input type='submit' value='submit'/>"
    form = ("<form method='post' >" +
        rot_label + rotation_input + "</br>" +
        message_label + textarea + "</br>" +
        submit + "</form>")

    return page_header + form + page_footer

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(build_page(""))

    def post(self):
        rotation = self.request.get('rotation')
        message = self.request.get("message")
        encrypted = caesar.encrypt(message, rotation)
        escaped = cgi.escape(encrypted)
        self.response.write(build_page(escaped))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
