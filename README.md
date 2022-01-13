# US-GPO-BulkData-BillCrawl
### US GPO XML data crawl of US House of Representatives legislation.
----

#### Background

I have been interested interested in analyzing and visualizing the social network of US representatives and senators as manifested by their sponsorship and co-sponsorship on bills and resolutions. A bill or resolution is typically introduced by one or two congressional members as originating sponsors, and several other members will “sign on” to co-sponsor. The US Governement Publications Office provides an archive of XML files that neatly capture Congressional bill and resolution numbers (identifiers) as well as sponsors and co-sponsors.

#### Future

I have written code to create a table of members of Congress that captures the state they represent and their party affiliation. The code "crawls" through the GPO XML files of the most recent 116th Congressional Session. I focus on the House of Representatives and the House-introduced bills. However, with some minor tweaks, the code could be easily expanded to consider bills introduced in the US Seante. The code could also be further developed so that resolutions and joint resolutions are also included in the analysis of social networks. Finally, while this code was written for the 116th Congress, it can easily be adapted to the current 117th Congress as well as previous and future sessions of Congress.  

Where would I like to go with this code? I will attempt to determine if there are “social networks” of members based on the region of the country they represent and, if found, visualize the regional alliances that transcend the US House Representative’s political party affiliations. My next steps are to become more familiar with the D3 libraries so that I can visualize the "sponsorship" relationships that my code captures.


#### Code unit summary

The following code units were written in Python.

1. 116-HR-mbrdb-v4.py. Creates a SQLite database with three normalized tables in which to store the current House of Representatives membership of the 116th Congress. The program opens and reads an XML file located on the House Clerk’s website. A subset of the membership data (name of representative, state, district, party) is copied to the SQLite database.
2. 116-HR-billcrawl-vN.py. Adds four normalized tables to the SQLite database in which to store House of Representative bills that have been introduced by the members of the current (116th) Congress. Sequentially reads all House bills beginning with HR1 to the most current. A subset of the information is copied to the SQLite database “HRBills” table (bill number, title, originating chamber). It also converts the sponsor and co-sponsor XML element data into a string which is stored as an attribute in the “HRBills” table. The program also creates a many-to-many table (“Sponsors”) which will store the mapping of the sponsor(s) of each bill with the co-sponsors who support the bill.
3. 116-HR-sponmap-vN.py. Accesses the “HRBills “table, converts the sponsor and co-sponsor string attributes into their original XML element format, and loads the sponsor-co-sponsor relationships for each bill into the previously-defined many-to-many “Sponsors” table.


