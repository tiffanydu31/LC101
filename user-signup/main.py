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
import re

def buildPage(usernameError='', passwordError='', verificationError='', emailError='', username='', email=''):
    page_header = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>User Signup</title>
            </head>
            <body>
                <h1>User Signup</h1>
        """
    page_footer = """
            </body>
        </html>
        """

    form = """
        <form method='post'>
            <table><tbody>
                <tr>
                    <td><label>Username</label></td>
                    <td><input type='text' name='username' value='%(username)s'></td>
                    <td style='color:red'>%(usernameError)s</td>
                </tr>
                <tr>
                    <td><label>Password</label></td>
                    <td><input type='text' name='password'></td>
                    <td style='color:red'>%(passwordError)s</td>
                </tr>
                <tr>
                    <td><label>Verify Password</label></td>
                    <td><input type='text' name='verify'></td>
                    <td style='color:red'>%(verificationError)s</td>
                </tr>
                <tr>
                    <td><label>Email (optional)</label></td>
                    <td><input type='text' name='email' value='%(email)s'></td>
                    <td style='color:red'>%(emailError)s</td>
                </tr>
                <tr>
                    <td><input type='submit'></td>
                </tr>
            </tbody></table>
        </form>
        """%{'usernameError':usernameError, 'passwordError':passwordError, 'verificationError':verificationError, 'emailError':emailError, 'username':username, 'email':email}

    return page_header + form + page_footer

def checkUsername(username):
    return re.compile("^[a-zA-Z0-9_-]{3,20}$").match(username)

def checkPassword(password):
    return re.compile("^.{3,20}$").match(password)

def checkMatch(password, verify):
        if password == verify:
            return True

def checkEmail(email):
    if email:
        return re.compile("^[\S]+@[\S]+.[\S]+$").match(email)
    else:
        return True

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(buildPage())

    def post(self):

        usernameError = ""
        passwordError = ""
        verificationError =""
        emailError =""

        verifyUsername = checkUsername(self.request.get('username'))
        verifyPassword = checkPassword(self.request.get('password'))
        verifyMatch = checkMatch(self.request.get('password'), self.request.get('verify'))
        verifyEmail = checkEmail(self.request.get('email'))

        if verifyUsername and verifyPassword and verifyMatch and verifyEmail:
            self.redirect('/welcome?username='+self.request.get('username'))

        if not verifyUsername:
            usernameError = "That's not a valid username."
        if not verifyPassword:
            passwordError = "That's not a valid password."
        if not verifyMatch:
            verificationError = "Passwords do not match."
        if not verifyEmail:
            emailError = "That's not a valid email."

        self.response.write(buildPage(usernameError, passwordError, verificationError, emailError, self.request.get('username'), self.request.get('email')))

class Welcome(webapp2.RequestHandler):
    def get(self):
        self.response.write("<b>Welcome, " + self.request.get('username') + "!</b>")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome', Welcome)
], debug=True)
