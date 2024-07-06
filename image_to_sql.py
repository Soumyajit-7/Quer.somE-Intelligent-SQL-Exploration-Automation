# image_to_sql.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

class ImageToSQL:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def generate_sql_from_image(self, image_path, prompt):
        img = Image.open(image_path)
        response = self.model.generate_content(["""Only return the sql query to create this table along with the columns and input the values. These are some additional information that you need to keep in mind. Your only job is to create table. You are using SQlite3 to do all the operations. Also note AUTO_INCREMENT is not a part of sqlite3 query. While Inserting the data in the table, id the id or primary key of each row is not mentioned in the picture, put a random primary key and dont keep it null. And dont do errors like this : "Generated SQL query from image: CREATE TABLE Occupation(ID INT NOT NULL, Name VARCHAR(255) NOT NULL, Job VARCHAR(255) NOT NULL, City VARCHAR(255) NOT NULL, PRIMARY KEY (ID)); INSERT INTO Occupation (Name, Job, City) VALUES (1, 'Jon', 'cricketer', 'Kolkata'), (2, 'Mike', 'footballer', 'Bangalore'), (3, 'Ron', 'driver', 'Hyderabad'), (4, 'Katie', 'minister', 'Delhi');
        The Response is:
        An error occurred: 4 values for 3 columns"  
        - Only follow the sqlite syntax and donot include any other syntax.
        - Do not include any additional information in the response.
        AUTO_INCREMENT is not a part of sqlite3 query. While Inserting the data in the table, id the id or primary key of each row is not mentioned in the picture, put a random primary key and dont keep it null.
        - Never mention the word SQL or Q or anything like this in the response and should only be pure sqlite3 query. """ + prompt[0], img], stream=True)
        response.resolve()
        sql_query = response.text.strip()
        sql_query = sql_query.replace("```", "").replace("sql", "").strip()
        return sql_query



# """Only return the sql query to create this table along with the columns and input the values. These are some additional information that you need to keep in mind. Your only job is to create table. You are using SQlite3 to do all the operations. Also note AUTO_INCREMENT is not a part of sqlite3 query. While Inserting the data in the table, id the id or primary key of each row is not mentioned in the picture, put a random primary key and dont keep it null. And dont do errors like this : "Generated SQL query from image: CREATE TABLE Occupation(ID INT NOT NULL, Name VARCHAR(255) NOT NULL, Job VARCHAR(255) NOT NULL, City VARCHAR(255) NOT NULL, PRIMARY KEY (ID)); INSERT INTO Occupation (Name, Job, City) VALUES (1, 'Jon', 'cricketer', 'Kolkata'), (2, 'Mike', 'footballer', 'Bangalore'), (3, 'Ron', 'driver', 'Hyderabad'), (4, 'Katie', 'minister', 'Delhi');
#         The Response is:
#         An error occurred: 4 values for 3 columns"  """