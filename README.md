To run nl2sql proj

Install Ollama: If you haven't already, download and install Ollama from the official website.

run below in bash
ollama pull deepseek-r1:1.5b


install Python from the official website: https://www.python.org/downloads/
get a gemini pro api key , create file config.ini and put your api key like below

[genai]

api_key = Your key

Clone the Project and run the below commands

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

streamlit run app_movie_compact.py


![image](https://github.com/user-attachments/assets/d5ea6236-36f9-490c-814b-db87ba0ed46b)



![image](https://github.com/user-attachments/assets/3eea925a-2c2c-41b6-8129-21f63769faa2)
