import os
import sys
import time
import mariadb
from argparse import Namespace

# __dir__ = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(__dir__)
# sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

# os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

class DBManager():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if DBManager.__instance__ == None:
            DBManager()
        return DBManager.__instance__

    def __init__(self):
        if DBManager.__instance__ != None:
            raise Exception('Paddle Text Recognizer is a singleton!')
        else:
            DBManager.__instance__ = self

            self.rec_args = Namespace(
               user="radar",
               password="123456",
               host="192.168.1.170",
               port=3306,
               database="radar_database",
            )

    def mysql_real_connect(self):
        conn = mariadb.connect(
           user=self.rec_args.user,
           password=self.rec_args.password,
           host=self.rec_args.host,
           port=self.rec_args.port,
           database=self.rec_args.database
        )

        return conn


    def create_database(self, form_name):
        conn = self.mysql_real_connect()
        # Get Cursor
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {form_name};")
        cur.execute("CREATE TABLE distance(ID INT auto_increment, Distance_1 float(6,2), \
                    Distance_2 float(6,2), Pitch float(5,2), Yaw float(5,2), primary key(ID));")
        conn.commit()
        conn.close()


# while True:
# # print("aa")
# distance1 = distance(GPIO_TRIGGER1, GPIO_ECHO1)
# distance2 = distance(GPIO_TRIGGER2, GPIO_ECHO2)
# conn = mysql_real_connect(user,password,database,host,port)
# cur = conn.cursor()
# cur.execute("INSERT INTO distance (Distance_1, Distance_2, Pitch, Yaw) VALUES (?,?,?,?);", (distance1,distance2,10,0))
# conn.commit()
# conn.close()
# # print("aa")
# print("Distance1 : %.1f" % distance1, 'cm')
# print("Distance2 : %.1f" % distance2, 'cm')

# time.sleep(0.5)
