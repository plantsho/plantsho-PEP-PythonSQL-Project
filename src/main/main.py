import csv
import os
import sqlite3
import pandas as pd

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
    # Create DF from csv
    # Skip lines with too many fields
    df = pd.read_csv(
            file_path,
            dtype ={"firstName": "string", "lastName": "string"},
            on_bad_lines="warn"
    ) 

    # print(df.info())
    # print(f"shape = {df.shape}\n")
    # print(f"datatypes = {df.dtypes}\n")
    # print(f"column types = {df.columns}\n")
    # print(f"index = {df.index}\n")

    cols = ['firstName', 'lastName']

    #Standardize Text Column Values 
    for col in cols:
        df[col] = df[col].str.title().str.strip()
    #Replace Empty Strings
        df[col] = df[col].replace("",pd.NA)

    #Drop rows with any missing data
    df = df.dropna(subset=['firstName','lastName'])
    df.to_sql('users', conn, if_exists="replace")
                                                                                

# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    df = pd.read_csv(
        file_path,
        on_bad_lines="warn"
    )

    df = df.apply(lambda x: x.str.strip() if x.dtype == "string" else x)
    pattern = r"\d{3}-\d{3}-\d{4}"
    phone_mask = df['phoneNumber'].str.fullmatch(pattern)
    df = df[phone_mask]

    numeric_cols = ["startTime", "endTime", "userId"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col],errors="coerce")    

    # Clean Missing Values
    df = df.dropna()

    #Load to table
    df.to_sql('callLogs',conn, if_exists="replace", index=False) 

# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    df = pd.read_sql('SELECT * FROM callLogs;', conn)
    df["duration"] = df["endTime"]-df["startTime"]
    user_analytics_df = df.groupby("userId").agg(
        avgDuration = ("duration", "mean"),
        numCalls = ("userId", "count")
    ).reset_index()

    user_analytics_df.to_csv(csv_file_path,index=False)


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    df = pd.read_sql("SELECT * FROM callLogs;",conn)
    df = df.sort_values(by=['userId', 'startTime'])
    df.to_csv(csv_file_path,index=False)



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