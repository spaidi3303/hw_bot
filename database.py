import datetime
import logging
import pymysql
import json
from dotenv import load_dotenv
import os
from constants import LESSONS
from others_func import get_lesson_full_name

days_of_week = {1: 'пн', 2: 'вт', 3: 'ср', 4: 'чт', 5: 'пт', 6: 'сб', 7: "вс"}


load_dotenv("secret.env")  # Загружает переменные из файла
# token = os.getenv("token")
database = os.getenv("database")
host = os.getenv("host")
password = os.getenv("password")
user = os.getenv("user")

class Connect:
    def __init__(self, id):
        self.conn = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.id = id
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS `Users` (userid VARCHAR(15) PRIMARY KEY, class TEXT, login INT DEFAULT 0, password INT DEFAULT 0)"
                )
            self.conn.commit()
    
    def __del__(self):
        self.conn.close()

    def check_table(self, class_name):
        try:
            command = "(id INT AUTO_INCREMENT PRIMARY KEY, lesson VARCHAR(255) UNIQUE, homework JSON)"
            with self.conn.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {class_name} {command}")
            self.conn.commit()
            array = list(LESSONS.values())
            for lesson in array:
                insert_query = f"INSERT INTO {class_name} (lesson, homework) VALUES (%s, %s)"
                with self.conn.cursor() as cursor:
                    cursor.execute(insert_query, (lesson, json.dumps({})))
                    self.conn.commit()

        except Exception as e:
            logging.error(f"Ошибка check_table: {e}")


    def user_exists(self) -> bool:
        query = f"SELECT userid FROM `Users` WHERE userid = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (self.id, ))
            result = cursor.fetchone()
            return result is not None
        
    def create_user(self, class_name):
        self.check_table(class_name)
        query = f"INSERT INTO `Users` (userid, class) VALUES (%s, %s)"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (self.id, class_name))
            self.conn.commit()
    
    def get_homework(self, class_name: str, lesson: str) -> dict:
        try:
            query = f"SELECT homework FROM {class_name} WHERE lesson = %s"
            with self.conn.cursor() as cursor:
                cursor.execute(query, (lesson, ))
                result = cursor.fetchone()
            try:
                return json.loads(result['homework'])
            except:
                return {}
        except Exception as e:
                logging.error(f'Ошибка get_hw: {e}')

    def update_homework(self, class_name: str, lesson: str, date: str, homework_text) -> None:
        try:
            homework = self.get_homework(class_name, lesson)
            array = []
            try:
                for i in homework[date]:
                    array.append(i)
            except KeyError:
                pass
            array.append(homework_text)
            homework[date] = array
            update_query = f"UPDATE {class_name} SET homework = %s WHERE lesson = %s"
            with self.conn.cursor() as cursor:       
                cursor.execute(update_query, (json.dumps(homework, ensure_ascii=False), (lesson)))
                self.conn.commit()
        except Exception as e:
                logging.error(f'Ошибка update_homework: {e}')
        
    def del_table(self, table_name):
        with self.conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE {table_name}")
            self.conn.commit()

    def get_class(self):
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT class FROM Users WHERE userid = %s", (self.id, ))
            result = cursor.fetchone()
            return result['class']
    
    def get_class_id(self, uid):
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT class FROM Users WHERE userid = %s", (uid,))
            result = cursor.fetchone()
            return result['class']
        
    def get_all_homework(self, class_name, date: str) -> dict:
        try:
            array = {}
            with open('schedule.json') as file:
                array = json.loads(file.read())
            dates = list(map(int, date.split('.')))
            try:
                dat_of_week = datetime.datetime(year=datetime.datetime.now().year, month=dates[1], day=dates[0]).isoweekday()
            except ValueError:
                return {}
            lessons = array[class_name][days_of_week[dat_of_week]]
            array = {}
            for lesson in lessons:
                homework = self.get_homework(class_name, lesson)
                try:
                    homework = homework[date]
                    array[lesson] = homework
                except KeyError:
                    homework = "Нет дз"
            return array
        except Exception as e:
                logging.error(f'Ошибка get_all_hw: {e}')

    def get_all_dates(self, lesson: str):
        try:
            today = datetime.datetime.now()
            class_name = self.get_class()
            homework = self.get_homework(class_name, get_lesson_full_name(lesson))
            dates = homework.keys()
            array = []
            for date in dates:
                day = int(date.split('.')[0])
                month = int(date.split('.')[1])
                date_dt = datetime.datetime(year=datetime.datetime.now().year, month=month, day=day)
                if date_dt >= today:
                    array.append(date_dt.strftime('%d.%m'))
            sorted_dates = sorted(array, key=lambda x: datetime.datetime.strptime(f"{x}.2000", '%d.%m.%Y'))
            return sorted_dates
        except Exception as e:
                logging.error(f'Ошибка get_all_dates: {e}')
    
    def dell_homework(self, lesson: str, date: str):
        class_name = self.get_class()
        homework = self.get_homework(class_name, lesson)
        del homework[date]
        update_query = f"UPDATE {class_name} SET homework = $s WHERE lesson = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(update_query, (json.dumps(homework, ensure_ascii=False), lesson))
            self.conn.commit()

    def get_login_password(self):
        query = F"SELECT login, password FROM Users WHERE userid = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (self.id,))
            result = cursor.fetchone()
        return str(result['login']), str(result['password'])

    def update_login_password(self, login: str, password: str):
        query = f"UPDATE Users SET login = %s, password = %s WHERE userid = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (login, password, self.id))
            self.conn.commit()
    
    def get_all_id(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT userid FROM Users")
            result = cursor.fetchall()
        array = []
        for i in result:
            array.append(i['userid'])
        return array
    
    def dell_user(self):
        with self.conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM `Users` WHERE userid = %s", (self.id,))
            self.conn.commit()