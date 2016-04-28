#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
from jinja2 import Template
import os
import subprocess
import time
import json

from tornado import gen

from tornado.options import define, options

define("port", default=8890, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            autoreload=True,
            compiled_template_cache=False,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("book.html", messages=ChatSocketHandler.cache)

class DemoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)        

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info("opening a new connection")
        ChatSocketHandler.waiters.add(self)
        if len(ChatSocketHandler.waiters) == 1:
            logging.info("first connection. spawn process?")
            
        book = {"book_id": "2",
                "title": "Harry Potter and the Sorcerer's Stone",
                "author": "J.K. Rowling",
                "ignorewords": ""}
        
        ChatSocketHandler.update_cache(book)
        ChatSocketHandler.send_updates(book)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        if parsed["body"] == "spawn":
            logging.info("spawn process")
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))

        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)
        
@gen.coroutine
def dummy():
    # logging.info("every 5")
    logging.info("checking for a new book")

    
    
    chat = {
        "id": str(uuid.uuid4()),
        "body": "Harry Potter",
        }
        
    chat["html"] = Template("""<div class="message" id="{{ id }}">{{ body }}</div>""").render(chat)
        
    # chat["html"] = tornado.escape.to_basestring(
    #     MainHandler.render_string("message.html", message=chat))
    ChatSocketHandler.update_cache(chat)
    ChatSocketHandler.send_updates(chat)
    return True

# book_found = False
# book_title = ""

@gen.coroutine
def check_USB():
    # time.sleep(.25)
    if "BOOK" in os.listdir("/Volumes/"):
        logging.info("new USB detected")
        # give it a second to fully mount
        time.sleep(1)
        # print(True)
        f = open("/Volumes/BOOK/metadata.json","r")
        book_metadata = json.loads(f.read())
        f.close()
        logging.info(book_metadata["title"])
        book_title = book_metadata["title"]

        ChatSocketHandler.update_cache(book_metadata)
        ChatSocketHandler.send_updates(book_metadata)
        
        # no reason not to give it some time here
        # to finish touching the drive
        # (don't want the unmount to fail!)
        time.sleep(.5)
        subprocess.call("diskutil unmountDisk BOOK",shell=True)
        # now give it a good while to unmount
        time.sleep(1)
        # book_found = True
    else:
        logging.info("No book found")

        logging.info("Sending data for testing anyway")

        # book = {"book_id": "2",
        #          "title": "Harry Potter and the Sorcerer's Stone",
        #          "author": "J.K. Rowling",
        #          "ignorewords": ""}
        
        # ChatSocketHandler.update_cache(book)
        # ChatSocketHandler.send_updates(book)

@gen.coroutine
def minute_loop():
    while True:
        # yield dummy()
        yield check_USB()
        yield gen.sleep(30)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)

    # Coroutines that loop forever are generally started with
    # spawn_callback().
    tornado.ioloop.IOLoop.current().spawn_callback(minute_loop)

    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()

