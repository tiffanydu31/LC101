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
import random

def getRandomFortune():
    # list of possible fortunes
    fortunes = [
        "I see much code in your furture",
        "Consider eating more fortune cookies",
        "You have tamed the mighty Python, now you must free it onto the Great Spider's Web!"
    ]

    # randomly select one of the fortunes
    index = random.randint(0, 2)

    return fortunes[index]


class MainHandler(webapp2.RequestHandler):
    def get(self):
        header = "<h1>Fortune Cookie</h1>"

        fortune = getRandomFortune()
        fortune_paragraph = "<p>" + "Your fortune: <strong>" + fortune + "</strong></p>"

        number_sentence = "Your lucky number: <strong>" + str(random.randint(1, 100)) + "</strong>"
        number_paragraph = "<p>" + number_sentence + "</p>"

        cookie_again_button = "<a href='.'><button>Another cookie plz!</button></a>"

        self.response.write(header + fortune_paragraph + number_paragraph + cookie_again_button)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
