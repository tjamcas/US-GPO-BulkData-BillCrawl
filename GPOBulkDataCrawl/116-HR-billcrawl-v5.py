# Initialize databases and counters, and go to US GPO bulk data repository site.
# Open and read a 116th Congress House Bill XML file as part of PY4E Capstone project
# Crawl through legislation and insert bill data into databases for eventual visualization.
# /Users/tim/Documents/PY4E/capstone/DataAnalysisProject/GPOBulkDataCrawl/116-HR-billcrawl-v1.py

from urllib.request import Request, urlopen
import urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import ssl
import sqlite3

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Create ”HRBills", “Origin”, "LegislationType", “Sponsors” (many to many
# mapping), and ”Roles" tables.
# SQL: Create tables if they do not already exist.
conn = sqlite3.connect('116-HR-net.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Origin')
cur.execute('DROP TABLE IF EXISTS Roles')
cur.execute('DROP TABLE IF EXISTS LegislationType')

# for primary keys update SQL command to:
# id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE
cur.execute('''CREATE TABLE IF NOT EXISTS HRBills
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    legislationtype_id INTEGER, origin_id INTEGER,
    legNo TEXT, congressNo TEXT, legTitle TEXT, Sponsors TEXT,
    CoSponsors TEXT, attemptParse INTEGER, parseSpon INTEGER, parseCoSpon INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Origin
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    chamber TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS LegislationType
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    legType TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Sponsors
    (hrbill_id INTEGER, representative_id INTEGER, role_id INTEGER,
    PRIMARY KEY (hrbill_id, representative_id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS Roles
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, role TEXT)''')

cur.execute('INSERT INTO Origin (chamber) VALUES ("Senate")')
cur.execute('INSERT INTO Origin (chamber) VALUES ("House")')
cur.execute('INSERT INTO Origin (chamber) VALUES ("Joint")')

cur.execute('INSERT INTO Roles (role) VALUES ("sponsor")')
cur.execute('INSERT INTO Roles (role) VALUES ("co-sponsor")')

# Legislation type: HR (House Bill), S (Senate Bill), HJRES (House Joint Resolution),
# SJRES (Senate Joint Resolution), HCONRES (House Concurrent Resolution), SCONRES
# (Senate Concurrent Resolution), HRES (House Simple Resolution), SRES (Senate Simple Resolution)
cur.execute('INSERT INTO LegislationType (legType) VALUES ("HR")')
cur.execute('INSERT INTO LegislationType (legType) VALUES ("S")')
cur.execute('INSERT INTO LegislationType (legType) VALUES ("HJRES")')
cur.execute('INSERT INTO LegislationType (legType) VALUES ("SJRES")')
cur.execute('INSERT INTO LegislationType (legType) VALUES ("HCONRES")')
cur.execute('INSERT INTO LegislationType (legType) VALUES ("SCONRES")')

conn.commit()

# Initialize variables. If there are records in HRBills, then NNNN = the max id in table
errCount = 0
# recordInsert = 0
# commitflag = False
many = 0
cur.execute('SELECT max(id), legNo FROM HRBills')
try:
    row = cur.fetchone()
    # When there are no records in the HRBills table, fetchone returns a tuple.
    # Will have to check whether a tuple is returned when there is a record in the table
    if row[0] is None :
        NNNN = 0
    else:
        NNNN = int(row[1])
except:
    NNNN = 0

# Create dictionary of members, origin and legislation type indexes:
# memberindx(bioguideID) = {id}
# originindx[chamber] = {id}
# legistypeindx[legtype] = {id}
memberindx = dict()
cur.execute('SELECT id, bioguideID FROM Representatives')
for rep in cur:
    id = rep[0]
    bioguideID = rep[1]
    memberindx[bioguideID] = id
# print("memberindx:\n", memberindx, "\n\n")

originindx = dict()
cur.execute('SELECT id, chamber from Origin')
for body in cur:
    id = body[0]
    chamber = body[1]
    originindx[chamber] = id
# print("originindx:\n", originindx, "\n\n")

legistypeindx = dict()
cur.execute('SELECT id, legtype FROM LegislationType')
for leg in cur:
    id = leg[0]
    legtype = leg[1]
    legistypeindx[legtype] = id
# print("legistypeindx:\n", legistypeindx, "\n\n")

# Set prefix for the XML URL that we will open:
# https://www.govinfo.gov/bulkdata/BILLSTATUS/116/hr/BILLSTATUS-116hrNNNN.xml
# Broke the URL into multiple parts, in case we want ot latr modify the program to
# analyze Senate and Joint bills and resolutions from other Congressional sessions.
Base_URL = "https://www.govinfo.gov/bulkdata/BILLSTATUS/116/hr/"
StatusType = "BILLSTATUS-"
CongressNo = "116"
Chamber = "hr"

while True:
    if (many <= 1):
        i = input("How many Congressional House Bills do you want to parse? ")
        if (len(i) < 1): break
        many = int(i)
    else:
        many = many - 1

    # Open and read XML file: https://www.govinfo.gov/bulkdata/BILLSTATUS/116/hr/BILLSTATUS-116hrNNNN.xml
    NNNN = NNNN + 1
    Article = str(NNNN)
    filename = StatusType + CongressNo + Chamber + Article + ".xml"
    URLname = Base_URL + filename
    print("\n\n\*** Program checkpoint 1 ***\nOpening URL: ", URLname, "\n\n")


    try:
        req = Request(URLname, headers={'User-Agent': 'XYZ/3.0'})
        webpage = urlopen(req, timeout=20)
        # webpage is Type:  <class 'http.client.HTTPResponse'>
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except Exception as e:
        print("***** Unable to retrieve or parse XML page", URLname)
        print("***** Error", e, "\n\n")
        errCount = errCount + 1
        if errCount > 10 : break
        continue


    errCount = 0
    data = webpage.read()
    print('\n\n*** Program checkpoint 2 ***\nRetrieved', len(data), 'characters of type ', type(data))
    # data is Type bytes
    # print(data.decode())
    data = data.decode()
    print('Decoded', len(data), 'characters of type ', type(data), '\n\n')

    tree = ET.fromstring(data)
    # print("\n\n*** Program checkpoint 3 ***\nXML tree type: ", type(tree))
    # print("Tree length: ", len(tree))
    # print(" Bill Number: ", tree[0][0].text, "\n\n")

    # findall() returns a list. The variable "bill" will be a list of length 1.
    # The list contains a single element object.
    bill = tree.findall("bill")
    # print("Bill list type: ", type(bill))
    # print("Length of bill list: ", len(bill))
    # print("Bill contents (list): ")
    # print(bill, "\n\n")
    billinfo = bill[0]

    # Legislation type: bill, resolution = billStatus/bill/billType
    # Originating chamber: Senate, House, Joint = billStatus/bill/originChamber
    # Legislative Number = billStatus/bill/billNumber
    # Congressional Session = billStatus/bill/congress
    # Legislation Title = billStatus/bill/title
    legitype = billinfo.find("billType").text
    legitypeid = legistypeindx[legitype]
    chamber = billinfo.find("originChamber").text
    chamberid = originindx[chamber]
    billNumber = billinfo.find("billNumber").text
    session = billinfo.find("congress").text
    title = billinfo.find("title").text
    print("\n\n*** Program checkpoint 4 ***")
    print("Bill information: ", legitypeid, chamberid, billNumber, session, title, "\n\n")

    # Sponsor(s) = billStatus/bill/sponsors/item/bioguideId
    # Co-sponsor(s) = billStatus/bill/cosponsors/item/bioguideId
    # Note: there may be more than one sponsor and co-sponsor
    sponsorstree = billinfo.find("sponsors")
    sponsorstr = ET.tostring(sponsorstree)
    # print("sponsors node type: ", type(sponsorstree))
    # print("sponsors node content: \n", sponsorstree, "\n\n")
    sponsors = sponsorstree.findall("item")
    print("The number of sponsors found: ", len(sponsors), "\n")
    for item in sponsors:
        print("Sponsor: ", item.find("fullName").text)
    print("\n\n")

    cosponsorstree = billinfo.find("cosponsors")
    cosponsorstr = ET.tostring(cosponsorstree)
    # print("cosponsors node type: ", type(cosponsorstree))
    # print("cosponsors node content: \n", cosponsorstree, "\n\n")
    cosponsors = cosponsorstree.findall("item")
    print("The number of co-sponsors found: ", len(cosponsors), "\n")
    for item in cosponsors:
        print("CoSponsor: ", item.find("fullName").text)
    print("\n\n")

    cur.execute('''INSERT INTO HRBills (legislationtype_id, origin_id, legNo, congressNo, legTitle, Sponsors, CoSponsors)
        VALUES (?,?,?,?,?,?,?)''', (legitypeid, chamberid, billNumber, session, title, sponsorstr, cosponsorstr))
    conn.commit()

conn.commit()
conn.close()
print("\n\n*** Program Complete ***\n\n")
