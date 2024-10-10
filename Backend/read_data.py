from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import mysql.connector

# Setup the service account
SERVICE_ACCOUNT_FILE = "C:/Users/rsingh16/Desktop/competency project/Backend/competency-project-8988bf4fad14.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

SPREADSHEET_ID = '1Q6Sa1vQjLFLeLaMVpJkrovtSOa-rPXwLSCLZ5NCYDck'
sheet_names = ['Fall 2024', 'Spring 2025', 'Summer 2025', 'Fall 2025', 'Spring 2026', 'Summer 2026', 'Fall 2026', 'Spring 2027', 'Summer 2027']

# Database connection
cnx = mysql.connector.connect(user='rimjhim', password='DeckerCompetency2024',
                              host='localhost', database='competencydata')
cursor = cnx.cursor()

# Complete mapping of all columns based on your provided schema
column_mappings = {
    'student_id': 'student_id',
    'student_name': 'student_name',
    'cohort': 'cohort',
    '1.1_mid': 'competency_1_1_mid',
    '1.1_end': 'competency_1_1_end',
    '1.2_mid': 'competency_1_2_mid',
    '1.2_end': 'competency_1_2_end',
    '1.3_mid': 'competency_1_3_mid',
    '1.3_end': 'competency_1_3_end',
    '1.4_mid': 'competency_1_4_mid',
    '1.4_end': 'competency_1_4_end',
    '1.5_mid': 'competency_1_5_mid',
    '1.5_end': 'competency_1_5_end',
    '1.6_mid': 'competency_1_6_mid',
    '1.6_end': 'competency_1_6_end',
    '1.7_mid': 'competency_1_7_mid',
    '1.7_end': 'competency_1_7_end',
    'feedback_1': 'feedback_1',
    '2.1_mid': 'competency_2_1_mid',
    '2.1_end': 'competency_2_1_end',
    '2.2_mid': 'competency_2_2_mid',
    '2.2_end': 'competency_2_2_end',
    '2.3_mid': 'competency_2_3_mid',
    '2.3_end': 'competency_2_3_end',
    '2.4_mid': 'competency_2_4_mid',
    '2.4_end': 'competency_2_4_end',
    'feedback_2': 'feedback_2',
    '3.1_mid': 'competency_3_1_mid',
    '3.1_end': 'competency_3_1_end',
    '3.2_mid': 'competency_3_2_mid',
    '3.2_end': 'competency_3_2_end',
    '3.3_mid': 'competency_3_3_mid',
    '3.3_end': 'competency_3_3_end',
    'feedback_3': 'feedback_3',
    '4.1_mid': 'competency_4_1_mid',
    '4.1_end': 'competency_4_1_end',
    '4.2_mid': 'competency_4_2_mid',
    '4.2_end': 'competency_4_2_end',
    '4.3_mid': 'competency_4_3_mid',
    '4.3_end': 'competency_4_3_end',
    '4.4_mid': 'competency_4_4_mid',
    '4.4_end': 'competency_4_4_end',
    '4.5_mid': 'competency_4_5_mid',
    '4.5_end': 'competency_4_5_end',
    'feedback_4': 'feedback_4',
    '5.1_mid': 'competency_5_1_mid',
    '5.1_end': 'competency_5_1_end',
    '5.2_mid': 'competency_5_2_mid',
    '5.2_end': 'competency_5_2_end',
    '5.3_mid': 'competency_5_3_mid',
    '5.3_end': 'competency_5_3_end',
    '5.4_mid': 'competency_5_4_mid',
    '5.4_end': 'competency_5_4_end',
    'feedback_5': 'feedback_5'
}

for sheet_name in sheet_names:
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    properties = sheet_metadata.get('sheets')
    for item in properties:
        if item['properties']['title'] == sheet_name:
            rowCount = item['properties']['gridProperties']['rowCount']
            columnCount = item['properties']['gridProperties']['columnCount']

    RANGE_NAME = f'{sheet_name}!A1:BB72'
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=RANGE_NAME, 
        valueRenderOption='FORMULA'
    ).execute()

    values = result.get('values', [])

    if values:
        df = pd.DataFrame(values[1:], columns=values[0])
        df.rename(columns={col: column_mappings.get(col.replace(' ', '_').lower(), col.replace(' ', '_').lower()) for col in df.columns}, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        df['semester_id'] = sheet_name

        placeholders = ', '.join(['%s'] * len(df.columns))
        columns = ', '.join([f"`{column}`" for column in df.columns])
        updates = ', '.join([f"{column}=VALUES({column})" for column in df.columns if column not in ['student_id', 'semester_id']])
        sql = f"INSERT INTO StudentCompetencies ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"

        for index, row in df.iterrows():
            cursor.execute(sql, tuple(row))
        cnx.commit()
        
    else:
        print(f"No data found in {sheet_name}, skipping...")
print("Code has run sucessfully, your database has been updated")
# cursor.close()
# cnx.close()

# Function to get a student's data for a particular competency across all semesters
def get_student_competency_data(student_id, competency_id):
    # Use the globally defined column_mappings
    competency_column = column_mappings.get(competency_id)
    
    # Validate competency_id
    if not competency_column:
        raise ValueError(f"Invalid competency ID: {competency_id}")

    # SQL query to fetch the student's data for the specified competency across all semesters
    query = f"""
    SELECT
        student_id,
        student_name,
        cohort,
        semester_id,
        {competency_column}
    FROM
        StudentCompetencies
    WHERE
        student_id = %s;
    """

    # Execute the query
    cursor = cnx.cursor()
    cursor.execute(query, (student_id,))

    # Fetch the data and convert it to a pandas DataFrame
    data = cursor.fetchall()
    columns = ['student_id', 'student_name', 'cohort', 'semester_id', competency_column]
    df = pd.DataFrame(data, columns=columns)

    # Close the cursor
    cursor.close()

    return df
student_id = 'B00768785'
competency_id = '1.1_mid'  # Make sure to pass the competency ID as it is in the mappings
result_df = get_student_competency_data(student_id, competency_id)
#print(result_df)

# Function to get all competency scores for a student for a specific semester
def get_student_scores_for_semester(student_id, semester_id):
    # Query to fetch all columns for the specific student and semester
    query = """
    SELECT *
    FROM StudentCompetencies
    WHERE student_id = %s AND semester_id = %s;
    """

    # Execute the query
    cursor = cnx.cursor()
    cursor.execute(query, (student_id, semester_id))

    # Fetch column names and data
    columns = cursor.column_names
    data = cursor.fetchall()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Close the cursor
    cursor.close()

    return df

student_id = 'B00768785'
semester_id = 'Fall 2024'
result_df = get_student_scores_for_semester(student_id, semester_id)
print(result_df)
# Print each row on a new line
for index, row in result_df.iterrows():
    print(row)


# Close the database connection after the entire process is done
cnx.close()