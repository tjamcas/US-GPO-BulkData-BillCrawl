# Open and read the abbreviated states list and capture the state names
# and abbreviatons.
# /Users/tim/Documents/PY4E/capstone/DataAnalysisProject/GPOBulkDataCrawl/state_read.py

# Open "alpha-states.txt" file and read into "State" table.
fhand = open("alpha-states.txt")
count = 0
print("\n\n*** Program checkpoint 1 ***\nReading alpha-states.txt ...")
for line in fhand:
    count = count + 1
    words = line.strip().split(",")
    print(words[0],words[1])

print("*** Program checkpoint 2 ***\nNumber of States read into State database table: ", count)
