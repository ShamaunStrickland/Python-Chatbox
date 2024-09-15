import json
import pymysql.cursors
from db_config import db_config

# Read responses from responses.json
with open('responses.json', 'r') as file:
    responses_data = json.load(file)

# Connect to the database
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            intent_tag VARCHAR(255),
            pattern VARCHAR(255),
            response VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)

        # Insert data into the table
        for intent_tag, intent_data in responses_data['responses'].items():
            patterns = intent_data['patterns']
            responses = intent_data['responses']
            for pattern, response in zip(patterns, responses):
                insert_query = """
                INSERT INTO responses (intent_tag, pattern, response)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (intent_tag, pattern, response))

    # Commit changes to the database
    connection.commit()
    print("Data migration completed successfully!")

finally:
    # Close database connection
    connection.close()
