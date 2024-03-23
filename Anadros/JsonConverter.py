import json
import pymysql.cursors

# Database configuration
db_config = {
    'host': 'anadros-user-training-data-do-user-15796887-0.c.db.ondigitalocean.com',
    'user': 'doadmin',
    'password': 'AVNS_eF16Y6-AumI0bR1dJvV',
    'database': 'defaultdb',
    'port': 25060,
    'cursorclass': pymysql.cursors.DictCursor
}

# Read intents from intents.json
with open('intents.json', 'r') as file:
    intents_data = json.load(file)

# Connect to the database
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS intents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tag VARCHAR(255),
            patterns TEXT,
            responses TEXT
        )
        """
        cursor.execute(create_table_query)

        # Insert data into the table
        for intent in intents_data['intents']:
            tag = intent['tag']
            patterns = json.dumps(intent['patterns'])
            responses = json.dumps(intent['responses'])
            insert_query = """
            INSERT INTO intents (tag, patterns, responses)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (tag, patterns, responses))

    # Commit changes to the database
    connection.commit()
    print("Data migration completed successfully!")

finally:
    # Close database connection
    connection.close()
