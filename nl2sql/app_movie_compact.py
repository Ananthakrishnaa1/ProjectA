import streamlit as st
import pandas as pd
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from configparser import ConfigParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.globals import set_verbose
from dotenv import load_dotenv
import re

# Read API key from config file
config = ConfigParser()
config.read('config.ini')
api_key = config.get('genai', 'api_key')

if api_key:
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
else:
    raise ValueError("API key not found. Please set the API key in the config.ini file.")

## Define Your Prompt
template = """
You are an expert in converting English questions to SQL query!
The SQL database has the name MOVIE and has the following columns 
- Name, Revenue, Year, Universe

For example,
Example 1 - How many entries of records are present?, 
the SQL command will be something like this SELECT COUNT(*) FROM MOVIE ;

Example 2 - Tell me all the movies in Marvel Universe?, 
the SQL command will be something like this SELECT * FROM MOVIE 
where Universe="Marvel"; 

If user asks a question out of context,the output should be a generic message
For example,
Example 3 - How many planets in the solar system?,
the output should be "Sorry, I can't help with that."

Example 4 - who is the producer of top grossing movie?,
 since the database does not have producer column. the output should be "Sorry, I can't help with that."

also the sql code should not have ``` 
in beginning or end and sql word in output

Question: {question}
SQL Query:
"""

## Function to retrieve query from the database
def read_sql_query(sql,db):
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

## Function to validate the question
def validate_question(question):
    keywords = ["movie", "movies", "film", "films", "cinema", "revenue", "year", "universe", "Marvel", "DC"]
    if any(keyword.lower() in question.lower() for keyword in keywords):
        return True
    return

## Function to validate the SQL query
def is_valid_sql(query):
    # Regular expression to match basic SQL commands
    sql_regex = re.compile(r'^\s*(SELECT|INSERT|UPDATE|DELETE)\s+', re.IGNORECASE)
    return bool(sql_regex.match(query))
    
## Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question,template):
    set_verbose(True) #more details about output
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        response = chain.invoke({
        "input_language": "English",
        "output_language": "English",
        'question' : question
        })
        return response['text']
    except ChatGoogleGenerativeAIError as e:
        print(f"An error occurred: {e}")
        return e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return e

## Streamlit App
st.set_page_config(page_title="Movie Database App",page_icon="🎬",layout="wide")
st.header("Type your question to get the results from the Movie Database")

question=st.text_input("Input: ",key="input")

# The content of the Submit button
submit=st.button("Get Results ->")

# if submit is clicked
if submit:
 if validate_question(question):
    response = get_gemini_response(question, template)
    if isinstance(response, Exception):
        st.error("An error occurred while processing your request. Please try again.")
    else:
        print(response)
        if is_valid_sql(response):
         response = read_sql_query(response, "movie.db")
         st.subheader("Results:")
         data = []
         # Convert the data to a DataFrame
         df = pd.DataFrame(response[1:], columns=response[0])
         # Display the DataFrame as a table in Streamlit
         st.table(df)
        else:
         st.write(response)
        
 else:
    st.error("Invalid question. Please ask a question related to the movie database.")
