#!/usr/bin/env python

DB_PATH = "~/.config/banshee-1/banshee.db"

import sqlite3
import os.path as path
conn = sqlite3.connect(path.expanduser(DB_PATH))
c = conn.cursor()
c.execute("""UPDATE CoreTracks SET
	DateAddedStamp = FileModifiedStamp,
	DateUpdatedStamp = FileModifiedStamp""")
conn.commit()
c.close()
