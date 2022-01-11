# Collect sponsors and cosponsors string variable from database and convert to XML
# element. Write sponsor/cosponsor and bill data into Sponsors database table.
# This can be a standalone program or copied as a function into another program.
# /Users/tim/Documents/PY4E/capstone/DataAnalysisProject/GPOBulkDataCrawl/116-HR-sponmap-vN.py

import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('116-HR-net.sqlite')
cur = conn.cursor()

# Create dictionary of membership. We will use the representative's bioguideID as the key,
# and the database record id as the value.
memberindx = dict()
cur.execute('SELECT id, bioguideID FROM Representatives')
for rep in cur:
    id = rep[0]
    bioguideID = rep[1]
    memberindx[bioguideID] = id
# print("memberindx:\n", memberindx, "\n\n")

# Create dictionary of HR Bills. We will use the database record id as the key,
# and the legislation number (HR Bill #) as the value.
hrbillindx = dict()
cur.execute('SELECT id, legNo FROM HRBills')
for bill in cur:
    id = bill[0]
    billNum = bill[1]
    hrbillindx[id] = billNum

# Initialize variables
many = 0

while True:
    if many <= 1:
        i = input("How many Bills would you like to parse for sponsorship? ")
        if (len(i) < 1): break
        many = int(i)
    else:
        many = many - 1
    # cur.execute('SELECT id, Sponsors, CoSponsors FROM HRBills WHERE id = 1')
    # ????? is this correct SQL syntax?????
    cur.execute('''SELECT MIN(id), Sponsors, CoSponsors from HRBills
        WHERE attemptParse is Null ORDER BY RANDOM() LIMIT 1''')
    q_results = cur.fetchone()
    curBillId = q_results[0]
    try:
        # This block of code will fail if we have exhausted the list of "crawled" bills.
        # Specifically, q_results and spon_str will be None, and the fromstring function will fail.
        spon_str = q_results[1]
        spon_xml = ET.fromstring(spon_str)
        cospon_str = q_results[2]
        cospon_xml = ET.fromstring(cospon_str)
    except:
        print("\n\n***** All known bills have been parsed for sponsorship *****\n\n")
        break

    # Set attemptParse flag so that we know bill has been parsed for sponsorship relationships
    cur.execute('UPDATE HRBills SET attemptParse = 1 WHERE id = ?', (curBillId, ) )

    # Parse bill's Sponsors attribute and write relationships in Sponsors table
    # (many to many junction table)
    print("\n\n*** Checkpoint #1 - parsing HR Bill Number ", hrbillindx[curBillId], "***\n\n")
    sponsors = spon_xml.findall("item")
    for item in sponsors:
        try:
            sp_bio = item.find("bioguideId").text
            sp_id = memberindx[sp_bio]
            # Remember that a sponsor has role_id = 1
            cur.execute('''INSERT OR IGNORE INTO Sponsors
                (hrbill_id, representative_id,role_id)
                VALUES (?,?,1)''', (curBillId, sp_id) )
            # print("item type: ", type(item))
            print("Sponsor: ", item.find("fullName").text)
        except:
            print("\n\n *** Member ", item.find("lastName").text, " not found. *** \n\n")
    cur.execute('''UPDATE HRBills SET parseSpon = 1 WHERE id = ?''', (curBillId, ) )

    cosponsors = cospon_xml.findall("item")
    for item in cosponsors:
        try:
            co_bio = item.find("bioguideId").text
            co_id = memberindx[co_bio]
            cur.execute('''INSERT OR IGNORE INTO Sponsors
                (hrbill_id, representative_id, role_id)
                VALUES (?,?,2)''', (curBillId, co_id) )
            print("Co-Sponsor: ", item.find("fullName").text)
        except:
            print("\n\n *** Member ", item.find("lastName").text, " not found. *** \n\n")

    # cur.execute('''UPDATE HRBills SET parseSpon = ? WHERE id = ?''', (var1, 1))
    cur.execute('''UPDATE HRBills SET parseCoSpon = 1 WHERE id = ?''', (curBillId, ) )

    conn.commit()

conn.commit()
conn.close()
print("\n\n*** Program Complete ***\n\n")
