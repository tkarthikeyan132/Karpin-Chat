import streamlit as st
import random
import time

# Set page configuration
st.set_page_config(page_title="Chat Application", page_icon=":speech_balloon:", layout="centered")

# Load the logo image
logo_image = "logo.jpg"  # Replace with the path to your logo image

# Create columns for logo and title
col1, col2 = st.columns([1, 3])

with col1:
    st.image(logo_image, width=100)  # Adjust width as needed

with col2:
    st.title("Karpin Chat")
    st.write("Hey, I am an Electoral bont [bot which can act as Bond]! Feel free to ask me anything about Electoral bonds!")

# Content area
st.markdown('<div class="content">', unsafe_allow_html=True)

st.write("Ask your questions and get responses.")

#----------------------------------------
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
    print("groq output:", llama3_output)
    answer = run_sql_query(llama3_output, conn)
    # return answer.iloc[0,0]

# # Display the result of the SQL query
# user_input = "What is the maximum bond_no YSR CONGRESS PARTY?"
# print("Answer:",ask_question(user_input))
    
    yield answer.iloc[0,0]
    time.sleep(0.05)


def else_response():
    yield "Sorry, I am TableQA expert and the question provided is not making use of abilities. Please try again :) "




#----------------------------------------


# Streamed response emulator
# def response_generator():
#     response = random.choice(
#         [
#             "Hello there! How can I assist you today?",
#             "Hi, human! Is there anything I can help you with?",
#             "Do you need help?",
#         ]
#     )
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)


# st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # response = st.write_stream(response_generator())
        try:
            response = st.write_stream(ask_question(prompt))
        except Exception as e:
            response = st.write_stream(else_response())
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Close the SQLite connection
conn.close()