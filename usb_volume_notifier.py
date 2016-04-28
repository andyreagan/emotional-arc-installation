import sys
import os
import json
import time
import subprocess

print(os.listdir("/Volumes/"))

if "BOOK" in os.listdir("/Volumes/"):
    print(True)
    f = open("/Volumes/BOOK/title.json","r")
    book = json.loads(f.read())
    print(book["title"])
    f.close()
else:
    print("No book found")

book_found = False
book_title = ""
while True:
    time.sleep(.25)
    if "BOOK" in os.listdir("/Volumes/"):
        # print("new USB detected")
        # 
        time.sleep(1)
        if not book_found:
            print(True)
            f = open("/Volumes/BOOK/title.json","r")
            book = json.loads(f.read())
            f.close()
            print(book["title"])
            book_title = book["title"]
            # no reason not to give it some time here
            time.sleep(2)
            subprocess.call("diskutil unmountDisk BOOK",shell=True)
            # or here
            time.sleep(2)
        else:
            print(book_title)
        book_found = True
    else:
        print("No book found")
        book_found = False
