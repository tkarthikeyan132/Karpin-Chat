from groq import Groq
import pandas as pd
import sqlite3
from datetime import datetime

# Convert the csv path to a dataframe
def csv_to_df(csv_path):
    # Read the CSV file and convert it to a DataFrame
    df = pd.read_csv(csv_path)

    #Preprocess the columns names for the ease of asking sql queries
    df.rename(columns=lambda x: x.replace(' ', '_').replace('\n', '_').replace('.','').replace('(','').replace(')',''), inplace=True)

    # Display the DataFrame
    print(df.columns)

    # Identify columns with "date" or "Date" in their names
    date_columns = [col for col in df.columns if 'date' in col.lower()]

    # Convert identified columns to date format
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format='%d/%b/%Y').dt.strftime('%Y-%m-%d')
        # Convert 'Date_Column' from string to datetime
        # df[col] = pd.to_datetime(df[col])


    # Convert the 'Denominations' column from string with commas to integers
    df['Denominations'] = df['Denominations'].str.replace(',', '')  # Remove commas
    df['Denominations'] = df['Denominations'].astype(int)  # Convert to integer

    return df

## create conversation for llama
def create_conversation_for_llama(Krompt, user_input):
    messages = [
        {"role": "system", "content":Krompt},
        {"role": "user", "content": user_input},
    ] # model will generate the output

    return messages

# Function to run SQL queries on the DataFrame
def run_sql_query(query, conn):
    return pd.read_sql_query(query, conn)

# Executes the conversation on llama
def run_groq_model(messages, model, client, temperature=0.7, top_p=1, max_tokens=16):
    chat_completion = client.chat.completions.create(
        messages=messages, temperature=temperature, top_p=top_p,
        model=model, n=1, max_tokens=max_tokens
    )
    return chat_completion.choices[0].message.content


GROQ_API_KEY = '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'
client = Groq(api_key=GROQ_API_KEY)

### CREATING MERGED DATAFRAME
csv_path1 = 'bonds_polparties.csv'
csv_path2 = 'bonds_individuals.csv'

df1 = csv_to_df(csv_path1)
df2 = csv_to_df(csv_path2) 
merged_df = pd.merge( df1, df2, on=['Prefix', 'Bond_Number'], how='left') #can do other joins
merged_df.drop(columns = ["Denominations_y", "Sr_No_y" ], inplace=True)
merged_df.rename(columns={'Denominations_x': 'Denominations', 'Sr_No_x': 'Sr_No'},inplace=True)
merged_df = merged_df.fillna(0)

### CREATING SQL SCHEMAS AND TABLES
#-------------------------------------
# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Load the DataFrame into the SQLite database
df1.to_sql('TABLE1', conn, index=False, if_exists='replace')
df2.to_sql('TABLE2', conn, index=False, if_exists='replace')

merged_df.to_sql('Merged', conn, index=False, if_exists='replace')
#-------------------------------------

def ask_question(user_input):
    Krompt = """
    You are a sqllite3 generator
    Generate SQLite3 queries for a table with the following schema:

    Table: Merged
    - Sr_No (INTEGER) : Unique serial number of the bond.
    - Date_of_Encashment (TEXT) : Date the bond was encashed.
    - Name_of_the_Political_Party (TEXT): Name of the political party that received the bond.
    - Account_no_of_Political_Party (TEXT): Bank account number of the political party
    - Prefix (TEXT): Prefix used for bond numbering.
    - Bond_Number (INTEGER): Unique number assigned to the bond.
    - Denominations (INTEGER): Value of the bond in monetary terms.
    - Pay_Branch_Code (INTEGER): Code of the branch where the bond was encashed.
    - Pay_Teller (TEXT): Name or ID of the teller who processed the encashment.
    - Reference_No_URN (TEXT): Unique reference number for the transaction.
    - Journal_Date (TEXT): Date the transaction was recorded in the journal.
    - Date_of_Purchase (TEXT): Date the bond was purchased.
    - Date_of_Expiry (TEXT): Expiry date of the bond
    - Name_of_the_Purchaser (TEXT): Name of the person who purchased the bond.
    - Issue_Branch_Code (TEXT): Code of the branch where the bond was issued.
    - Issue_Teller (TEXT): Name or ID of the teller who issued the bond.
    - Status (TEXT): Current status of the bond (e.g., encashed, expired).

    Total Unique Party are 
        'ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM',
        'BHARAT RASHTRA SAMITHI', 'BHARATIYA JANATA PARTY',
        'PRESIDENT, ALL INDIA CONGRESS COMMITTEE', 'SHIVSENA',
        'TELUGU DESAM PARTY',
        'YSR CONGRESS PARTY (YUVAJANA SRAMIKA RYTHU CONGRESS PARTY)',
        'DRAVIDA MUNNETRA KAZHAGAM (DMK)', 'JANATA DAL ( SECULAR )',
        'NATIONALIST CONGRESS PARTY MAHARASHTRA PRADESH',
        'ALL INDIA TRINAMOOL CONGRESS', 'BIHAR PRADESH JANTA DAL(UNITED)',
        'RASHTRIYA JANTA DAL', 'AAM AADMI PARTY',
        'ADYAKSHA SAMAJVADI PARTY', 'SHIROMANI AKALI DAL',
        'JHARKHAND MUKTI MORCHA', 'JAMMU AND KASHMIR NATIONAL CONFERENCE',
        'BIJU JANATA DAL', 'GOA FORWARD PARTY',
        'MAHARASHTRAWADI GOMNTAK PARTY', 'SIKKIM KRANTIKARI MORCHA',
        'JANASENA PARTY', 'SIKKIM DEMOCRATIC FRONT'

    Select the most probable party name when giving query.
    Output only the sql query and nothing else. Dont include ``` in output

    This is the table\n {}

    """.format(merged_df)

    messages = create_conversation_for_llama(Krompt, user_input)

    ret = run_groq_model(messages, "llama3-70b-8192", client, max_tokens=100, temperature=0.01)

    llama3_output =  ret.upper()
    
    try:
        answer = run_sql_query(llama3_output, conn)
        return answer.iloc[0,0]
    except Exception as e:
        return "I am ElectoralBond QA System. Please mention relevant question"

# # Display the result of the SQL query

# Read input file
input_file_path = './questions.txt'
with open(input_file_path, 'r') as file:
    questions = file.readlines()

processed_answers = [ask_question(question.strip()) for question in questions]


output_file_path = './answers.txt'
with open(output_file_path, 'w') as file:
    for answer in processed_answers:
        # print(type(answer))
        # print(answer)
        file.write(str(answer) + '\n')

# Close the SQLite connection
conn.close()

