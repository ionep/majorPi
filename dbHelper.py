import MySQLdb


class Database:

    host = 'localhost'
    user = 'root'
    password = 'pass'
    db = 'HexFlood'

    def __init__(self):
        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except MySQLdb.Error,e:
            print(e.args[1]);
            self.connection.rollback()



    def query(self, query):
        cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        num=int(cursor.execute(query))

        return num,cursor.fetchall()
        
	def __del__(self):
		self.connection.close()


'''if __name__ == "__main__":

    db = Database()

    #CleanUp Operation
    #del_query = "DELETE FROM basic_python_database"
    #db.insert(del_query)

    # Data Insert into the table
    query = """
		INSERT INTO consumption
        (date, volume,sent)
        VALUES
        ('2018/11/23', '10','false'),
        ('2018/11/24', '19','false')
        """

    # db.query(query)
    db.insert(query)
    
    select_query = """
        SELECT * FROM consumption
        """

    data = db.query(select_query)

    for d in data:
        print "id= " + str(d['id'])
        print "date= " + str(d['date'])
        print "volume= " + str(d['volume'])
        print "sent= " + str(d['sent'])
'''
