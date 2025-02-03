import streamlit as st
import pandas as pd
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from configparser import ConfigParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

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
    
## Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question,template):
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(question=question)
    print(response)
    return response

## Streamlit App
st.set_page_config(page_title="Movie Database App",page_icon="🎬",layout="wide")
st.header("Type your question to get the results from the Movie Database")

question=st.text_input("Input: ",key="input")

# The content of the Submit button
submit=st.button("Get Results ->")

# if submit is clicked
if submit:
    response=get_gemini_response(question,template)
    print(response)
    response=read_sql_query(response,"movie.db")
    st.subheader("Results:")
    data = []
    # Convert the data to a DataFrame
    df = pd.DataFrame(response[1:], columns=response[0])
    # Display the DataFrame as a table in Streamlit
    st.table(df)
