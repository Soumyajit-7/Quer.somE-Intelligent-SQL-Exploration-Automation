# Quer.somE: Intelligent SQL Exploration & Automation

QueryCraft is a Streamlit application designed to generate SQL queries from natural language questions, execute those queries on an uploaded SQLite database, and display the results in an intuitive interface. Powered by Google Gemini's generative AI, QueryCraft simplifies database querying and management.

## Features

- Upload an SQLite database file
- Display database and table structures in a user-friendly tabular format
- Input natural language questions to generate SQL queries
- Execute SQL queries and display results in a dynamic table
- Maintain query history
- Download the modified database

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Soumyajit-7/Quer.somE-Intelligent-SQL-Exploration-Automation.git
   cd Quer.somE-Intelligent-SQL-Exploration-Automation

2. Install Requirements:
   ```bash
   pip install -r requirements.txt
   
3. Set up environment variables:
   ```bash
   $env:GOOGLE_API_KEY="your_google_api_key_here"
   
4. Run the Streamlit app:
   ```bash
   streamlit run main.py --server.enableXsrfProtection false


## Code Explanation
 - get_gemini_response(question, prompt): Uses Google Gemini's AI to generate an SQL query from a natural language question and a detailed prompt.

 - execute_sql_query(sql, db): Executes a SQL query on the specified SQLite database and returns the results, along with success status and any error messages.

 - get_table_details(db): Retrieves metadata about tables in the SQLite database, including table names, column details, and row counts.

 - generate_prompt(table_details): Creates a prompt for the Google Gemini model based on the database structure and query history to generate accurate SQL queries.
