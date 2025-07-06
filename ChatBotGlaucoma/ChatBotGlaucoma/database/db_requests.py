# здесь будут запросы к базе данных, которые нам понадобятся
# нужно создать класс БД и реализовывать запросы

import sqlite3


# каркас для запросов
class DataBase():

    def __init__(self, db_file):

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

# тут имя можно поменять на более логичное)
class ClassName(DataBase):

    def funcName(self) -> None:

        with self.connection: # контекстный менеджер пайтона, он открывает файл и сам закрывает его с сохранением
            pass
            # Запросы CRUD к БД SQLite
            # self.cursor.execute("ЗАПРОС",(АРГУМЕНТЫ,))


#db = ClassName(db_file="ПУТЬ К ФАЙЛУ БД") храним мы бинарный файл базы данных