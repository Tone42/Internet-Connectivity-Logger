import datetime
import requests
import sqlite3
import time

# Connect to the database or create a new one if it doesn't exist
conn = sqlite3.connect('internet_outage.db')
conn.execute('''
CREATE TABLE IF NOT EXISTS outages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outage_start TIMESTAMP NOT NULL,
    outage_end TIMESTAMP NOT NULL
)
''')

# Continuously check the internet connection status
while True:
    # Send a request to a reliable website to check if the internet is available
    try:
        r = requests.get('https://www.google.com')
        if r.status_code == 200:
            print('Internet is connected')
            # Check if the internet was previously disconnected
            last_outage = conn.execute('SELECT * FROM outages WHERE outage_end > outage_start ORDER BY id DESC LIMIT 1').fetchone()
            if last_outage:
                # Record the end time of the outage in the database
                outage_end = datetime.datetime.now()
                conn.execute('UPDATE outages SET outage_end = ? WHERE id = ?', (outage_end, last_outage[0]))
                conn.commit()
        else:
            print('Internet is disconnected')
            # Check if the internet was previously connected
            last_outage = conn.execute('SELECT * FROM outages WHERE outage_end = outage_start ORDER BY id DESC LIMIT 1').fetchone()
            if not last_outage:
                # Record the start time of the outage in the database
                outage_start = datetime.datetime.now()
                conn.execute('INSERT INTO outages (outage_start, outage_end) VALUES (?, ?)', (outage_start, outage_start))
                conn.commit()
    except requests.exceptions.ConnectionError:
        print('Internet is disconnected')
        # Check if the internet was previously connected
        last_outage = conn.execute('SELECT * FROM outages WHERE outage_end = outage_start ORDER BY id DESC LIMIT 1').fetchone()
        if not last_outage:
            # Record the start time of the outage in the database
            outage_start = datetime.datetime.now()
            conn.execute('INSERT INTO outages (outage_start, outage_end) VALUES (?, ?)', (outage_start, outage_start))
            conn.commit()
    
    # Wait for a few seconds before checking again
    time.sleep(3)
