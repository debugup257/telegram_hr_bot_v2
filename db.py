import psycopg2

class GlobalVar():
    def __init__(self, host, dbname, user, password):
        self.conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        self.cur = self.conn.cursor()
        
    # Other methods
    
    def add_or_update_column(self, chat_id, column_name, new_value):
        # check if the record with given chat_id is present or not
        self.cur.execute(f"SELECT * FROM global_var WHERE chat_id = '{chat_id}'")
        record = self.cur.fetchone()
        
        if record:
            # update the column
            self.cur.execute(f"UPDATE global_var SET {column_name} = '{new_value}' WHERE chat_id = '{chat_id}'")
            self.conn.commit()
            print(f"Record with chat_id {chat_id} updated successfully")
        else:
            # insert new record
            self.cur.execute(f"INSERT INTO global_var (chat_id, {column_name}) VALUES ('{chat_id}', '{new_value}')")
            self.conn.commit()
            print(f"Record with chat_id {chat_id} inserted successfully")

    def fetch_column_value(self, chat_id, column_name):
        # check if the record with given chat_id is present or not
        self.cur.execute(f"SELECT {column_name} FROM global_var WHERE chat_id = '{chat_id}'")
        record = self.cur.fetchone()
        
        if record:
            return record[0]
        else:
            return None
        



    def insert_applicant(self,applicant_data,uid):

        # Build the INSERT statement
        sql = "INSERT INTO applicants (id,name, email, pan, location, exp, edu) VALUES (%s,%s, %s, %s, %s, %s, %s)"
        values = (uid,applicant_data['name'], applicant_data['email'], applicant_data['pan'], applicant_data['location'], applicant_data['exp'], applicant_data['edu'])

        # Execute the statement
        self.cur.execute(sql, values)

        # Commit the changes to the database
        self.conn.commit()

        # Close the cursor and connection
        # self.cur.close()
        # self.conn.close()

    def upload_data(self,data,id):
        try:

            
            # insert data into the faq table
            for question, answer in data.items():
                self.cur.execute("INSERT INTO faq(id,question, answer) VALUES(%s,%s, %s)",
                                (id,question, answer))
            
            # save changes to the database
            self.conn.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
