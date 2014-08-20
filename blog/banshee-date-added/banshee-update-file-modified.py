#/usr/bin/env python3

DB_PATH = "~/.config/banshee-1/banshee.db"

import sqlite3
import os.path as path
import os, urllib.parse
conn = sqlite3.connect(path.expanduser(DB_PATH))
c = conn.cursor()
for row in c.execute("SELECT Uri, DateAddedStamp FROM CoreTracks"):
	name, timestamp = urllib.parse.unquote(row[0].replace("file://", "", 1)), int(row[1])
	os.utime(name, (timestamp, timestamp))
