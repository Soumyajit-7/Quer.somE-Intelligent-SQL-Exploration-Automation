import streamlit as st
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()

# Function to execute query in the database
def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    success = True
    error_message = None
    rows = []
    try:
        # Split the SQL statements if there are multiple
        sql_commands = sql.split(';')
        for command in sql_commands:
            if command.strip():
                cur.execute(command.strip())
                if command.strip().lower().startswith("select"):
                    rows = cur.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        success = False
        error_message = str(e)
    finally:
        conn.close()
    return rows, success, error_message

# Function to get table details
def get_table_details(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    table_details = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]

        column_details = [{"name": col[1], "type": col[2]} for col in columns]
        table_details.append({"table_name": table_name, "columns": column_details, "row_count": row_count})

    conn.close()
    return table_details

# Function to generate the prompt with history
def generate_prompt(table_details):
    detailed_table_info = []
    for table in table_details:
        table_info = f"Table: {table['table_name']} (Rows: {table['row_count']}), Columns: "
        for column in table['columns']:
            table_info += f"{column['name']} ({column['type']}), "
        detailed_table_info.append(table_info.rstrip(", "))

    history = "\n".join(
        [f"Q: {item['question']}\nSQL: {item['sql']}\nSuccess: {item['success']}\n" + (f"Error: {item['error']}" if 'error' in item else "") for item in st.session_state.query_history]
    )

    prompt = [
        f"""
        You are an SQL database expert, highly skilled in writing and optimizing SQL queries for SQLite databases.
        The SQL database contains the following tables and columns:
        {'; '.join(detailed_table_info)}
        Here is the history of previous questions and their corresponding SQL queries and results:
        {history}
        Please use your expertise to convert English questions into efficient and accurate SQL queries.
        
        Consider the following examples for guidance:

        Example 1: How many records are present in the STUDENT table?
        SQL command: SELECT COUNT(*) FROM STUDENT;

        Example 2: List all students studying in the Data Science class.
        SQL command: SELECT * FROM STUDENT WHERE CLASS = 'Data Science';

        Example 3: Retrieve the names of students in Section A.
        SQL command: SELECT NAME FROM STUDENT WHERE SECTION = 'A';

        Example 4: Count the number of students in each class.
        SQL command: SELECT CLASS, COUNT(*) FROM STUDENT GROUP BY CLASS;

        Example 5: Get all details of students sorted by their names.
        SQL command: SELECT * FROM STUDENT ORDER BY NAME;

        Ensure that the generated SQL queries do not include unnecessary formatting characters (such as backticks, triple backticks, or the word "sql").
        Always verify that the generated queries are syntactically correct and optimized for execution in an SQLite environment.

        only retun Sqlite query and nothing else irrespective of the question asked by the user.

        Also while generating the query, consider the following:
        - Use the correct table and column names.
        - Use the appropriate SQL keywords and functions.
        - Optimize the query for performance and efficiency.
        - Handle any potential errors or exceptions that may occur during query execution.
        - Ensure that the query results are accurate and relevant to the question asked.
        - Do not generate responses like this: "SQL: SELECT * FROM inventory ORDER BY last_update DESC LIMIT 10;" as the word "SQL" is not required and is not a part of any sql query. only return the query and nothing else.
        - donot include any backticks or triple backticks in the response.
        - Do not include the word "sql" in the response.
        - Do not include any unnecessary formatting characters in the response.
        - Do not include any unnecessary information in the response.
        - your response should not be anything like this"Generated SQL query: Q: Calculate the total sales for each staff member. SQL: SELECT staff_id, SUM(amount) AS total_sales FROM payment GROUP BY staff_id;" 
        as this causes this error :
            The Response is
            An error occurred: near "Q": syntax error

        """
    ]
    return prompt

# Streamlit App
st.set_page_config(page_title="Quersome", page_icon="Designer.png", layout="wide")
st.header("Quer.somE: Intelligent SQL Exploration & Automation")

# File uploader for SQL database
uploaded_file = st.file_uploader("Choose a SQL database file", type="db", key="file", help="Upload a SQL database file to get started", accept_multiple_files=False)

if uploaded_file is not None:
    # Ensure the 'uploaded_files' directory exists
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")

    db_path = os.path.join("uploaded_files", uploaded_file.name)

    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully")

    # Get and display table details
    table_details = get_table_details(db_path)
    st.write("Tables in the database:")
    for table in table_details:
        st.write(f"Table: {table['table_name']}, Rows: {table['row_count']}")
        st.write("Columns:")
        for column in table['columns']:
            st.write(f" - {column['name']} ({column['type']})")

    # Define your dynamic prompt
    prompt = generate_prompt(table_details)

    # Input for natural language question
    question = st.text_input("Query in your language:", key="input")

    submit = st.button("Ask the question")

    # If submit is clicked
    if submit:
        sql_query = get_gemini_response(question, prompt)
        
        # Remove any unnecessary formatting characters
        sql_query = sql_query.replace("```", "").replace("sql", "").strip()
        st.write(f"Generated SQL query: {sql_query}")

        rows, success, error_message = execute_sql_query(sql_query, db_path)
        
        # Update query history
        st.session_state.query_history.append({
            "question": question,
            "sql": sql_query,
            "success": success,
            "error": error_message
        })

        st.subheader("The Response is")
        if success:
            if rows:
                # Dynamically get the column names from the query result
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute(sql_query)
                col_names = [description[0] for description in cur.description]
                conn.close()
                
                df = pd.DataFrame(rows, columns=col_names)
                st.dataframe(df)
            else:
                st.write("No results found.")
        else:
            st.write(f"An error occurred: {error_message}")

    # Provide download link for modified database
    with open(db_path, "rb") as f:
        st.download_button(
            label="Download Modified Database",
            data=f,
            file_name=uploaded_file.name,
            mime="application/octet-stream"
        )
else:
    st.write("Please upload a SQL database (.db) file to get started.")
