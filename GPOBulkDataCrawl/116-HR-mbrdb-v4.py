# Open and read the House membership list for the 116th Congress, and write the House
# member data to a SQLite database as part of PY4E Capstone project.
# /Users/tim/Documents/PY4E/capstone/DataAnalysisProject/GPOBulkDataCrawl/116-HR-mbrdb-v4.py

from urllib.request import Request, urlopen
import urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import ssl
import sqlite3

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('116-HR-net.sqlite')
cur = conn.cursor()

# Create "Representatives", "Party", and "State" tables. Create records for "Party" table.
# Delete and re-build tables every time the program is ran.
cur.execute('''DROP TABLE IF EXISTS Representatives''')
cur.execute('''DROP TABLE IF EXISTS Party''')
cur.execute('''DROP TABLE IF EXISTS State''')

cur.execute('''CREATE TABLE IF NOT EXISTS Representatives
    (id INTEGER PRIMARY KEY, lastname TEXT,firstname TEXT,bioguideID TEXT UNIQUE,
     state_id INTEGER, district TEXT, party_id INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Party
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
     partyname TEXT UNIQUE, partyabbrev TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS State
    (id INTEGER PRIMARY KEY, statename TEXT UNIQUE, stateabbrev TEXT UNIQUE)''')

# Load political party names into Party table
cur.execute('INSERT INTO Party (partyname, partyabbrev) VALUES ("Democrat", "D")')
cur.execute('INSERT INTO Party (partyname, partyabbrev) VALUES ("Republican", "R")')
cur.execute('INSERT INTO Party (partyname, partyabbrev) VALUES ("Independent", "I")')
cur.execute('INSERT INTO Party (partyname, partyabbrev) VALUES ("Open - Vacancy", "O")')

# Open "alpha-states.txt" file and read into "State" table.
fhand = open("alpha-states.txt")
count = 0
print("\n\n*** Program checkpoint 1 ***\nReading alpha-states.txt ...")
for line in fhand:
    count = count + 1
    words = line.strip().split(",")
#    print(words[0],words[1])
    cur.execute('INSERT INTO State (stateabbrev, statename) VALUES (?,?)', (words[0], words[1]))
conn.commit()
print("*** Program checkpoint 2 ***\nNumber of States read into State database table: ", count)

# create dictionary of foriegn keys for state and party_id

STateindx = dict()
cur.execute('''SELECT id, statename, stateabbrev FROM State''')
for state_row in cur:
    id = state_row[0]
    name = state_row[1]
    abbrev = state_row[2]
    STateindx[abbrev] = id, name
print("\n\n*** Program checkpoint 2b *** State Index:\n", STateindx)

partyindx = dict()
cur.execute('SELECT id, partyname, partyabbrev FROM Party')
for party_row in cur:
    id = party_row[0]
    name = party_row[1]
    abbrev = party_row[2]
    partyindx[abbrev] = id, name
print("\n\n*** Program checkpoint 2c *** Party Index:\n", partyindx)

# Open and read XML file: https://clerk.house.gov/xml/lists/MemberData.xml

URLname = "https://clerk.house.gov/xml/lists/MemberData.xml"
print("\n\n*** Program checkpoint 3 ***\nURL: ", URLname, "\n\n")

req = Request(URLname, headers={'User-Agent': 'XYZ/3.0'})
webpage = urlopen(req, timeout=20)
# webpage is Type:  <class 'http.client.HTTPResponse'>

data = webpage.read()
print('*** Program checkpoint 4 ***\nRetrieved', len(data), 'characters of type ', type(data), '\n\n')
# data is Type bytes
# print(data.decode())
data = data.decode()
print('Decoded', len(data), 'characters of type ', type(data), '\n\n')

tree = ET.fromstring(data)
print("*** Program checkpoint 5 ***\nXML tree type: ", type(tree), "\n\n")
print("Tree length: ", len(tree))
print(" tree [0][1]: ", tree[0][1].text, "\n\n")

members = tree.findall("members/member")
print("*** Program checkpoint 6 ***\nMemberData/members list type: ", type(members))
print("Length of MemberData/members list: ", len(members), "\n\n")
# print("MemberData/members contents (list): ")
# print(members, "\n\n")

# Record extracted from XML file:
#  - Last name of congressman = members/member/member-info/lastname
#  - First name of congressman = members/member/member-info/firstname
#  - Biography Guide ID = members/member/member-info/bioguideID
#    -- Unique identifier from the House Clerk
#    -- E.g. Andy Levin = L000592
#  - State/Territory = members/member/statedistrict
#  - District number = members/member/statedistrict
#    -- State/district is concatenated – e.g. “MI09” for Andy Levin
#    -- Will have to split string and leave district as a string (not an integer)
#  - Party affiliation = members/member/member-info/party
#    -- R = Republican, D = Democrat, I = third party, O = Open-Vacancy

print("*** Program checkpoint 7 *** Gathering Membership list....")

count = 0
# use count to commit database after every 50 iterations of record insertions

for member in members:
    count = count + 1
    statedistrict = member.find("statedistrict").text
    stateabbrev = statedistrict[0:2]
    # Skip over non-voting House members who live in territories and are not one of the 50 States
    try:
        state_id = STateindx[stateabbrev][0]
    except:
        print("\n***State code not found: ", stateabbrev, "***\n")
        continue
    district = statedistrict[2:]
    lastname = member.find("member-info").find("lastname").text
    # print("*** Last Name of Member: ", lastname)
    firstname = member.find("member-info").find("firstname").text
    bioguideID = member.find("member-info").find("bioguideID").text
    party = member.find("member-info").find("party").text
    # adjust party_id values for current membership vacancies and for
    # members of third parties (e.g. Libertarian Party)
    if bioguideID is None:
        lastname = "VACANCY"
        party_id = partyindx["O"][0]
    elif party != "D" and party != "R":
        party_id = partyindx["I"][0]
    else:
        party_id = partyindx[party][0]

    cur.execute('''INSERT INTO Representatives (lastname, firstname, bioguideID, state_id, district, party_id)
            VALUES (?,?,?,?,?,?)''', (lastname, firstname, bioguideID, state_id, district, party_id))
    if count % 50 == 0:
        conn.commit()
        # print("\n\n*** Program checkpoint 7 *** Database commit on iteration # ", count)

conn.commit()
cur.close()
print("\n\n*** Program Complete ***\n\n")
