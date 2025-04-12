import datetime
import logging
import re
import pymysql
import json
from dotenv import load_dotenv
import os
from others.constants import LESSONS, WEEKDAYS_DB
from others.others_func import get_lesson_full_name

days_of_week = {1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday', 7: 'sunday'}

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
                "CREATE TABLE IF NOT EXISTS `Users` ("
                "userid VARCHAR(15) PRIMARY KEY, "
                "class TEXT, "
                "login VARCHAR(255) DEFAULT '0', "
                "password VARCHAR(255) DEFAULT '0'"
                ")"
            )
            self.conn.commit()

    def __del__(self):
        self.conn.close()
    def check_table(self, db_name):
        try:
            if re.fullmatch(r"\d\d_[a-z]", db_name):
                command = "(id INT AUTO_INCREMENT PRIMARY KEY, lesson VARCHAR(255) UNIQUE, homework JSON)"
                with self.conn.cursor() as cursor:
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} {command}")
                self.conn.commit()
                array = list(LESSONS.values())
                for lesson in array:
                    insert_query = f"INSERT INTO {db_name} (lesson, homework) VALUES (%s, %s)"
                    with self.conn.cursor() as cursor:
                        cursor.execute(insert_query, (lesson, json.dumps({})))
                        self.conn.commit()
            elif re.fullmatch(r"\d\d_[a-z]_.*", db_name):
                command = "(id INT AUTO_INCREMENT PRIMARY KEY, `key` VARCHAR(255) UNIQUE, `value` JSON)"
                with self.conn.cursor() as cursor:
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_name} {command}")
                    self.conn.commit()

                class_ = re.findall(r"\d\d_[a-z]", db_name)[0]
                js = {}
                for weekday in WEEKDAYS_DB.keys():
                    with open('schedule.json') as file:
                        array = json.loads(file.read())
                    array = (array[class_][WEEKDAYS_DB[weekday]])
                    js[weekday] = array
                insert_query = f"INSERT INTO `{db_name}` (`key`, `value`) VALUES (%s, %s)"
                with self.conn.cursor() as cursor:
                    cursor.execute(insert_query, ("schedule", json.dumps(js, ensure_ascii=False)))
                    self.conn.commit()
                        
                with open('schedule.json') as file:
                    array = json.loads(file.read())                  
                own = array[class_]["own"][0]
                insert_query = f"INSERT INTO `{db_name}` (`key`, `value`) VALUES (%s, %s)"
                js_admins = {"own": own, "admins": []}
                with self.conn.cursor() as cursor:
                    cursor.execute(insert_query, ("admins", json.dumps(js_admins, ensure_ascii=False)))
                    self.conn.commit()
            elif db_name == "profmat":
                print(1)
                command = "(id INT AUTO_INCREMENT PRIMARY KEY, `key` VARCHAR(255) UNIQUE, `value` TEXT)"
                with self.conn.cursor() as cursor:
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS `{db_name}` {command}")
                    self.conn.commit()
                profmat_id = [2098644058, 5191932879, 1752185553, 5407189672, 6891657794, 7502257293, 5806734924, 5472687359, 6324042999, 2076998769]
                insert_query = f"INSERT INTO `{db_name}` (`key`, `value`) VALUES (%s, %s)"
                with self.conn.cursor() as cursor:
                    cursor.execute(insert_query, ("uids", json.dumps(profmat_id)))
                    cursor.execute(insert_query, ("hw", json.dumps({})))
                    self.conn.commit()
        except Exception as e:
            ...

    def user_exists(self) -> bool:
        query = "SELECT userid FROM `Users` WHERE userid = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (self.id, ))
            result = cursor.fetchone()
            return result is not None

    def create_user(self, class_name):
        self.check_table(class_name)
        self.check_table(class_name+"_class")
        query = "INSERT INTO `Users` (userid, class) VALUES (%s, %s)"
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
            except Exception:
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
            cursor.execute("SELECT class FROM Users WHERE userid = %s", (self.id, ))
            result = cursor.fetchone()
            return result['class']

    def get_class_id(self, uid):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT class FROM Users WHERE userid = %s", (uid,))
            result = cursor.fetchone()
            return result['class']

    def get_lessons(self):
        try:
            tb_name = f"{self.get_class()}_class"
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT `value` FROM `{tb_name}` WHERE `key` = %s", ("schedule", ))
                result = cursor.fetchone()
            result = json.loads(result['value'])

            return result
        except Exception as e:
            print(f'Ошибка get_lessons: {e}')

    def get_admins(self):
        try:
            tb_name = f"{self.get_class()}_class"
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT `value` FROM `{tb_name}` WHERE `key` = 'admins'")
                result = cursor.fetchone()
                return json.loads(result['value'])
        except Exception as e:
            logging.error(f'Ошибка get_admins: {e}')
            return None

    def get_all_homework(self, class_name, date: str) -> dict:
        try:
            dates = list(map(int, date.split('.')))
            try:
                dat_of_week = datetime.datetime(year=datetime.datetime.now().year, month=dates[1], day=dates[0]).isoweekday()
            except ValueError:
                return {}
            lessons = self.get_lessons()[days_of_week[dat_of_week]]
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

    def del_homework(self, lesson: str, date: str):
        class_name = self.get_class()
        homework = self.get_homework(class_name, lesson)
        del homework[date]
        update_query = f"UPDATE {class_name} SET homework = %s WHERE lesson = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(update_query, (json.dumps(homework, ensure_ascii=False), lesson))
            self.conn.commit()

    def get_login_password(self):
        query = "SELECT login, password FROM Users WHERE userid = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (self.id,))
            result = cursor.fetchone()
        return str(result['login']), str(result['password'])

    def update_login_password(self, login: str, password: str):
        query = "UPDATE Users SET login = %s, password = %s WHERE userid = %s"
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
            cursor.execute("DELETE FROM `Users` WHERE userid = %s", (self.id,))
            self.conn.commit()

    def update_all_homework(self, class_, lesson, hw):
        update_query = f"UPDATE {class_} SET homework = %s WHERE lesson = %s"
        with self.conn.cursor() as cursor:       
            cursor.execute(update_query, (json.dumps(hw, ensure_ascii=False), (lesson)))
            self.conn.commit()

    def add_admin(self, uid):
        try:
            class_ = self.get_class()
                
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT `value` FROM `{class_}_class` WHERE `key` = 'admins'")
                array = json.loads(cursor.fetchone()['value'])['admins']

            array.append(uid)
            js = {"own": self.id, "admins": array}
            with self.conn.cursor() as cursor:
                update_query = f"UPDATE `{class_}_class` SET `value` = %s WHERE `key` = %s"
                cursor.execute(update_query, (json.dumps(js), "admins"))
                self.conn.commit()
                
        except Exception as e:
            logging.error(f'Ошибка add_admin: {e}')
            return False
    

    def del_admin(self, uid):
        try:
            class_ = self.get_class()
                
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT `value` FROM `{class_}_class` WHERE `key` = 'admins'")
                array = json.loads(cursor.fetchone()['value'])['admins']

            array.remove(uid)
            js = {"own": self.id, "admins": array}
            with self.conn.cursor() as cursor:
                update_query = f"UPDATE `{class_}_class` SET `value` = %s WHERE `key` = %s"
                cursor.execute(update_query, (json.dumps(js), "admins"))
                self.conn.commit()
                
        except Exception as e:
            logging.error(f'Ошибка add_admin: {e}')
            return False
    

    def get_profmat_ids(self) -> list:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT `value` FROM `profmat`")
                result = cursor.fetchall()
            return json.loads(result[0]["value"])
        except Exception as e:
            print(f'Ошибка get_profmat_ids: {e}')   

    def get_hw_profmat(self) -> dict:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT `value` FROM `profmat`")
                result = cursor.fetchall()
                array_hw = json.loads(result[1]['value'])
                
            return array_hw
        
        except Exception as e:
            print(f'Ошибка get_hw_profmat: {e}')

    def add_hw_profmat(self, hw: str, date: str):
        try:
            homework = self.get_hw_profmat()
            array = []
            try:
                for i in homework[date]:
                    array.append(i)
            except KeyError:
                pass

            array.append(hw)
            homework[date] = array
            update_query = f"UPDATE `profmat` SET `value` = %s WHERE `key` = %s"
            with self.conn.cursor() as cursor:       
                cursor.execute(update_query, (json.dumps(homework, ensure_ascii=False), ("hw")))
                self.conn.commit()

        except Exception as e:
            print(f'Ошибка add_hw_profmat: {e}')