# ����� ����� ������� � ���� ������, ������� ��� �����������
# ����� ������� ����� �� � ������������� �������

import sqlite3


# ������ ��� ��������
class DataBase():

    def __init__(self, db_file):

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

# ��� ��� ����� �������� �� ����� ��������)
class ClassName(DataBase):

    def funcName(self) -> None:

        with self.connection: # ����������� �������� �������, �� ��������� ���� � ��� ��������� ��� � �����������
            pass
            # ������� CRUD � �� SQLite
            # self.cursor.execute("������",(���������,))


#db = ClassName(db_file="���� � ����� ��") ������ �� �������� ���� ���� ������