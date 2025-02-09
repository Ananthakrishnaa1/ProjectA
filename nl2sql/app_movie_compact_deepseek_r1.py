import streamlit as st
import pandas as pd
import sqlite3
import speech_recognition as sr
from langchain.prompts import PromptTemplate
from langchain.globals import set_verbose
import re
from langchain_ollama import OllamaLLM

# Initialize DeepSeek R1
llm = OllamaLLM(model="deepseek-r1:1.5b")

# Define Your Prompt
template = """
You are an expert in converting English questions to SQL queries!
The SQL database is named MOVIE and has the following columns:
- Name
- Revenue
- Year
- Universe

Ensure the SQL query's WHERE clause only includes columns present in the database.
Wrap the SQL query in <sql> tags. Example: <sql>SELECT * FROM MOVIE WHERE Universe="Marvel"</sql>.
Always wrap the SQL query in <sql> tags and never miss the </sql> at the end of the query.
Do not include three single quotes at the beginning or end of the query.

Convert the following natural language query into an optimized SQL query and return the SQL query.

Natural Language Query:
{question}
"""

# Function to retrieve query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    conn.commit()
    conn.close()

    # Add column names as the first row
    rows.insert(0, column_names)

    for row in rows:
        print(row)

    return rows

# Function to validate the question
def validate_question(question):
    keywords = ["movie", "movies", "film", "films", "cinema", "revenue", "year", "universe", "Marvel", "DC"]
    if any(keyword.lower() in question.lower() for keyword in keywords):
        return True
    return False

# Function to validate the SQL query
def is_valid_sql(query):
    # Regular expression to match basic SQL commands
    sql_regex = re.compile(r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+', re.IGNORECASE)
    return bool(sql_regex.match(query))

# Function to extract SQL query from the response
def extract_sql_query(response):
    # Regular expression to match SQL query wrapped in <sql> tags
    sql_matches = re.findall(r'<sql>(.*?)</sql>', response, re.IGNORECASE | re.DOTALL)
    if sql_matches:
        return sql_matches[0].strip()
    else:
        raise ValueError("SQL query not found in response")

# Function To Load deepseek r1 Model and provide queries as response
def get_deepseek_r1_response(question, template):
    set_verbose(True)  # more details about output
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    try:
        response = chain.invoke({
            "input_language": "English",
            "output_language": "English",
            'question': question
        })
        print(response)  # Log the full response
        if response:
            print(response)
            sql_query = extract_sql_query(response)
            print('sql_query:' + sql_query)
            return sql_query
        else:
            raise ValueError("Invalid response format")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return str(e)

# Function to convert speech to text with reduced listening time
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Create an empty container for the "Listening..." message
        message_placeholder = st.empty()
        message_placeholder.info("Listening...")

        # Adjust the duration parameter to reduce listening time
        audio = r.listen(source, timeout=2, phrase_time_limit=5)

    try:
        text = r.recognize_google(audio)
        # Clear the "Listening..." message
        message_placeholder.empty()
        return text
    except sr.UnknownValueError:
        # Clear the "Listening..." message
        message_placeholder.empty()
        st.error("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        # Clear the "Listening..." message
        message_placeholder.empty()
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function to execute the question
def execute():
    if validate_question(question):
        response = get_deepseek_r1_response(question, template)
        if isinstance(response, Exception):
            st.error("An error occurred while processing your request. Please try again.")
        else:
            if is_valid_sql(response):
                response = read_sql_query(response, "movie.db")
                st.subheader("Results:")
                # Convert the data to a DataFrame
                df = pd.DataFrame(response[1:], columns=response[0])
                # Display the DataFrame as a table in Streamlit
                st.table(df)
            else:
                st.write('Please refine your question')
    else:
        st.error("Invalid question. Please ask a question related to the movie database.")

# Streamlit App
st.set_page_config(page_title="Movie Database App", page_icon="🎬", layout="wide")
st.header("Type your question to get the results from the Movie Database")
st.write("This app uses DeepSeek R1 locally to convert English questions to SQL queries for the Movie Database.")

# Initialize session state variables
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "Text Input"
if "speech_text" not in st.session_state:
    st.session_state.speech_text = ""
if "listening" not in st.session_state:
    st.session_state.listening = False

# Radio button to switch between text and audio input
input_mode = st.radio("Choose input mode:", ("Text Input", "Audio Input"), index=0 if st.session_state.input_mode == "Text Input" else 1)

if input_mode != st.session_state.input_mode:
    st.session_state.input_mode = input_mode
    st.session_state.speech_text = ""

question = ""
if st.session_state.input_mode == "Text Input":
    # The text input field for the user's question
    question = st.text_input("Input: ", value=st.session_state.speech_text, key="input")
elif st.session_state.input_mode == "Audio Input":
    if st.button("Use Speech-to-Text"):
        text = speech_to_text()
        if text:
            st.session_state.speech_text = text
            st.session_state.input_mode = "Text Input"
            question = text
            st.session_state.listening = False
            execute()

# The content of the Submit button
submit = st.button("Get Results ->")

# Execute the question if the Submit button is clicked
if submit:
    execute()
