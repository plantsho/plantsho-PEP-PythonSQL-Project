import csv
import os
import sqlite3

# Resolve the resources folder relative to this file, so paths work
# no matter what directory the script is run from.
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources')

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users(os.path.join(_RESOURCES_DIR, 'users.csv'))
    load_and_clean_call_logs(os.path.join(_RESOURCES_DIR, 'callLogs.csv'))
    write_user_analytics(os.path.join(_RESOURCES_DIR, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(_RESOURCES_DIR, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    clean_users = []
    with open(file_path,"r") as file:
        reader = csv.DictReader(file)

        headers_len = len(reader.fieldnames)
        for row in reader:
            if len(row) !=2:
                continue
            first_name = row.get("firstName").strip()
            last_name = row.get("lastName").strip()

            #missing values
            if not first_name or not last_name:
                continue

            #extra fields
            if len(row) > headers_len:
                continue

            clean_users.append((first_name,last_name))

    cursor.executemany(
        "INSERT INTO users (firstName, lastName) VALUES (?,?)",
        clean_users
    )                                              

# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    clean_logs = []
    with open(file_path,"r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            phone = row.get("phoneNumber").strip()
            start_time = row.get("startTime").strip()
            end_time = row.get("endTime").strip()
            direction = row.get("direction").strip()
            user_id = row.get("userId").strip()

            if not all([phone,start_time,end_time,direction,user_id]):
                continue

            try:
                start = int(start_time)
                end = int(end_time)
                userId = int(user_id)
            except ValueError:
                continue

            #make sure start and end times valid
            if start < 0 or end < start:
                continue

            # #validate phone number format
            # if not re.fullmatch(r'\d{3}-\d{3}-\d{4}',phone):
            #     continue

            clean_logs.append((phone,start,end,direction,userId))

    cursor.executemany(
        """
        INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId) VALUES (?,?,?,?,?);
        """,
        clean_logs
    )

# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    cursor.execute("""
        SELECT 
        userId, 
        AVG(endTime-startTime) AS avgDuration, 
        COUNT(*) AS numCalls 
        FROM callLogs
        GROUP BY userId
        ORDER BY userId
    """)
        
    rows = cursor.fetchall()

    with open(csv_file_path,"w") as file:
        writer = csv.writer(file)
        #write header
        writer.writerow(["userId", "avgDuration", "numCalls"]) 
        writer.writerows(rows)

# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    cursor.execute(" SELECT * FROM callLogs ORDER BY userId ASC, startTime ASC")

    rows = cursor.fetchall()

    with open(csv_file_path,"w") as file:
        writer = csv.writer(file)
        writer.writerow(["callId","phoneNumber","startTime","endTime","direction","userId"])
        writer.writerows(rows)

# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()