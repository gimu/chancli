#!/usr/bin/env python3
import json
import urllib
import urllib.request

from html.parser import HTMLParser

# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = False
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class ApiError(object):

    @staticmethod
    def get_error(target, error):
        """Could not generate thread list
        """
        string = "\nCould not generate %s\nFull error code: %s" % (target, error)
        return string

class Api(object):

    def parse_comment(self, html):
        """Strip most HTML tags."""
        # Indent comment string
        html = html.replace("<br>", '\n    ')
        html = html.replace("&gt;", '>')
        html = html.replace("&quot;", '"')

        # After preserving some tags, strip all of them
        s = MLStripper()
        s.feed(html)

        return "    " + s.get_data() # Indent first line of comment
    
    def get_threads(self, board, page=1):
        """Return first threads by their first post, board and page."""
        data = None
        result = ""

        try:
            data = urllib.request.urlopen("https://a.4cdn.org/" + board + "/" + str(page) + ".json").read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return ApiError.get_error("threads list", error)
        except urllib.error.URLError as error:
            return ApiError.get_error("threads list", error)

        if data:
            data = json.loads(data)
            for index, post in enumerate(data["threads"], 1): # index starting from 1 to open threads without specifying full id (see: open <index>)
                result += "\n\n [" + str(index) + "] No. " + str(post["posts"][0]["no"]) + " " + post["posts"][0]["now"] + "\n"
                if "com" in post["posts"][0]: # Check for empty comment
                    result += self.parse_comment(post["posts"][0]["com"])
                else:
                    result += "    ---"

        return result

    def get_thread(self, board, thread_id):
        """Get particular thread by id."""
        data = None
        result = ""

        try:
            data = urllib.request.urlopen("https://a.4cdn.org/" + board + "/thread/" + str(thread_id) + ".json").read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return ApiError.get_error("thread list", error)
        except urllib.error.URLError as error:
            return ApiError.get_error("thread list", error)

        if data:
            data = json.loads(data)
            for post in data["posts"]:
                result += "\n\nNo. " + str(post["no"]) + " " + post["now"] + "\n"
                if "com" in post: # Check for empty comment
                    result += self.parse_comment(post["com"])
                else:
                    result += "    ---"

        return result

    def get_archive(self, board):
        data = None
        result = ""

        try:
            data = urllib.request.urlopen("https://a.4cdn.org/" + board + "/archive.json").read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return ApiError.get_error("archive list", error)
        except urllib.error.URLError as error:
            return ApiError.get_error("archive list", error)

        if data:
            data = json.loads(data)
            for index, thread in enumerate(data, 1): # index starting from 1 to open threads without specifying full id (see: open <index>)
                result += "\n[" + str(index) + "] " + str(thread)

        return result
