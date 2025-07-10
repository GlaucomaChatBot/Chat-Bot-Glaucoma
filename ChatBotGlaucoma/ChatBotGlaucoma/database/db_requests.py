import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

class GlaucomaDB:
    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    # ===== Методы для врачей =====
    def add_doctor(self, doctor_id: int, name: str = None) -> None:
        """Добавить нового врача"""
        self.conn.execute(
            "INSERT OR IGNORE INTO doctors (doctor_id, name) VALUES (?, ?)",
            (doctor_id, name)
        )
        self.conn.commit()

    def get_doctor(self, doctor_id: int) -> Optional[Dict]:
        """Получить данные врача"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM doctors WHERE doctor_id = ?", 
            (doctor_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'doctor_id': row[0],
                'name': row[1]
            }
        return None

    def delete_doctor(self, doctor_id: int) -> bool:
        """Удалить врача (каскадно удалит связи с пациентами)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM doctors WHERE doctor_id = ?",
            (doctor_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_all_doctors(self) -> List[Dict]:
        """Получить список всех врачей"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM doctors")
        return [{
            'doctor_id': row[0],
            'name': row[1]
        } for row in cursor.fetchall()]

    def get_doctor_id_by_patient(self, patient_id: int) -> Optional[int]:
        """Получить ID врача для пациента"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT doctor_id FROM doctors_have_patients WHERE patient_id = ?",
            (patient_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    # ===== Методы для пациентов =====
    def add_patient(self, patient_id: int, name: str = None) -> bool:
        """Добавить нового пациента без врача"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO patients (patient_id, name) VALUES (?, ?)",
                (patient_id, name)
            )
            self.conn.commit()
            return cursor.rowcount == 1
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении пациента: {e}")
            self.conn.rollback()
            return False

    def get_patient(self, patient_id: int) -> Optional[Dict]:
        """Получить данные пациента"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT p.*, d.doctor_id, d.name as doctor_name FROM patients p "
            "LEFT JOIN doctors_have_patients dh ON p.patient_id = dh.patient_id "
            "LEFT JOIN doctors d ON dh.doctor_id = d.doctor_id "
            "WHERE p.patient_id = ?",
            (patient_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'patient_id': row[0],
                'name': row[1],
                'doctor_id': row[2],
                'doctor_name': row[3]
            }
        return None

    def update_patient_doctor(self, patient_id: int, doctor_id: int) -> bool:
        """Обновить врача пациента"""
        self.add_doctor(doctor_id)
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM doctors_have_patients WHERE patient_id = ?",
                (patient_id,)
            )
            cursor.execute(
                "INSERT INTO doctors_have_patients (doctor_id, patient_id) VALUES (?, ?)",
                (doctor_id, patient_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении врача пациента: {e}")
            self.conn.rollback()
            return False

    def update_patient(self, patient_id: int, name: str = None) -> bool:
        """Обновить имя пациента"""
        if name is None:
            return False
            
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE patients SET name = ? WHERE patient_id = ?",
            (name, patient_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_patient(self, patient_id: int) -> bool:
        """Удалить пациента (каскадно удалит его лекарства и логи)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM patients WHERE patient_id = ?",
            (patient_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_patients_by_doctor(self, doctor_id: int) -> List[Dict]:
        """Получить всех пациентов врача"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT p.* FROM patients p "
            "JOIN doctors_have_patients dh ON p.patient_id = dh.patient_id "
            "WHERE dh.doctor_id = ?",
            (doctor_id,)
        )
        return [{
            'patient_id': row[0],
            'name': row[1]
        } for row in cursor.fetchall()]

    def get_all_patients(self) -> List[Dict]:
        """Получить список всех пациентов"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT patient_id, name FROM patients")
        return [{
            'patient_id': row[0],
            'name': row[1]
        } for row in cursor.fetchall()]

    # ===== Методы для лекарств =====
    def add_medication(self, name: str, start_time: str, interval_hours: int) -> int:
        """Добавить новое лекарство"""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO medications (name, start_time, interval_hours)
               VALUES (?, ?, ?)""",
            (name, start_time, interval_hours)
        )
        self.conn.commit()
        med_id = cursor.lastrowid
        print(f"Добавлено лекарство с ID {med_id}: {name}, {start_time}, {interval_hours} часов")
        return med_id

    def get_medication(self, med_id: int) -> Optional[Dict]:
        """Получить данные о лекарстве"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM medications WHERE medication_id = ?",
            (med_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'medication_id': row[0],
                'name': row[1],
                'start_time': row[2],
                'interval_hours': row[3]
            }
        return None

    def update_medication(self, med_id: int, name: str = None, 
                        start_time: str = None, interval: int = None) -> bool:
        """Обновить данные лекарства"""
        query = "UPDATE medications SET "
        params = []
        if name is not None:
            query += "name = ?, "
            params.append(name)
        if start_time is not None:
            query += "start_time = ?, "
            params.append(start_time)
        if interval is not None:
            query += "interval_hours = ?, "
            params.append(interval)
        
        if not params:
            return False
            
        query = query.rstrip(", ") + " WHERE medication_id = ?"
        params.append(med_id)
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_medication(self, med_id: int) -> bool:
        """Удалить лекарство (каскадно удалит назначения и логи приёма)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM medication_intake_log WHERE medication_id = ?",
                (med_id,)
            )
            cursor.execute(
                "DELETE FROM patient_has_medications WHERE medication_id = ?",
                (med_id,)
            )
            cursor.execute(
                "DELETE FROM medications WHERE medication_id = ?",
                (med_id,)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении лекарства с ID {med_id}: {e}")
            self.conn.rollback()
            return False

    def get_all_medications(self) -> List[Dict]:
        """Получить список всех лекарств"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM medications")
        return [{
            'medication_id': row[0],
            'name': row[1],
            'start_time': row[2],
            'interval_hours': row[3]
        } for row in cursor.fetchall()]

    # ===== Методы для назначений =====
    def assign_medication(self, patient_id: int, med_id: int) -> bool:
        """Назначить лекарство пациенту"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO patient_has_medications (patient_id, medication_id)
                   VALUES (?, ?)""",
                (patient_id, med_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Ошибка назначения лекарства: {e}")
            return False

    def revoke_medication(self, patient_id: int, med_id: int) -> bool:
        """Отменить назначение лекарства"""
        cursor = self.conn.cursor()
        cursor.execute(
            """DELETE FROM patient_has_medications
               WHERE patient_id = ? AND medication_id = ?""",
            (patient_id, med_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_patient_medications(self, patient_id: int) -> List[Dict]:
        """Получить все лекарства пациента"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT m.* FROM medications m
               JOIN patient_has_medications pm ON m.medication_id = pm.medication_id
               WHERE pm.patient_id = ?""",
            (patient_id,)
        )
        return [{
            'medication_id': row[0],
            'name': row[1],
            'start_time': row[2],
            'interval_hours': row[3]
        } for row in cursor.fetchall()]

    # ===== Методы для уведомлений и подтверждений =====
    def get_medications_to_notify(self) -> List[Dict]:
        """Получить лекарства для уведомления (которые нужно принять сейчас)"""
        cursor = self.conn.cursor()
        current_time = datetime.now()
        current_date = current_time.strftime("%Y-%m-%d")
    
        cursor.execute(
            """
            SELECT DISTINCT p.patient_id, m.medication_id, m.name, p.name as patient_name,
                   m.start_time, m.interval_hours
            FROM medications m
            JOIN patient_has_medications pm ON m.medication_id = pm.medication_id
            JOIN patients p ON pm.patient_id = p.patient_id
            """
        )
    
        medications = [{
            'patient_id': row[0],
            'medication_id': row[1],
            'medication_name': row[2],
            'patient_name': row[3],
            'start_time': row[4],
            'interval_hours': row[5]
        } for row in cursor.fetchall()]
    
        result = []
        for med in medications:
            try:
                start_time = datetime.strptime(f"{current_date} {med['start_time']}", "%Y-%m-%d %H:%M:%S")
                interval = timedelta(hours=med['interval_hours'])
                now = datetime.now()
            
                elapsed = now - start_time
                intervals_passed = int(elapsed.total_seconds() // (med['interval_hours'] * 3600))
                next_intake = start_time + intervals_passed * interval
            
                if abs((now - next_intake).total_seconds()) <= 60:
                    if not self.check_specific_intake(med['patient_id'], med['medication_id'], next_intake):
                        med['next_intake'] = next_intake
                        result.append(med)
            except ValueError as e:
                print(f"Ошибка формата времени для лекарства {med['medication_name']}: {e}")
                continue
    
        return result

    def log_intake(self, patient_id: int, med_id: int, scheduled_time: datetime) -> bool:
        """Зафиксировать приём лекарства с указанием времени"""
        cursor = self.conn.cursor()
        intake_time = scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
    
        try:
            cursor.execute(
                """INSERT INTO medication_intake_log
                   (patient_id, medication_id, intake_time)
                   VALUES (?, ?, ?)""",
                (patient_id, med_id, intake_time)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при записи приёма: {e}")
            return False

    def log_intake_with_notification(self, patient_id: int, med_id: int, scheduled_time: datetime) -> Optional[Dict]:
        """Зафиксировать приём и вернуть данные для уведомления врача"""
        if self.log_intake(patient_id, med_id, scheduled_time):
            patient = self.get_patient(patient_id)
            medication = self.get_medication(med_id)
            doctor_id = self.get_doctor_id_by_patient(patient_id)
            
            if patient and medication and doctor_id:
                return {
                    'patient_name': patient.get('name', f'Пациент {patient_id}'),
                    'medication_name': medication['name'],
                    'intake_time': scheduled_time,
                    'doctor_id': doctor_id,
                    'status': 'confirmed'
                }
        return None

    def check_intake(self, patient_id: int, med_id: int) -> bool:
        """Проверить, принято ли лекарство сегодня"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM medication_intake_log
            WHERE patient_id = ? AND medication_id = ?
            AND DATE(intake_time) = DATE('now', 'localtime')
            """,
            (patient_id, med_id)
        )
        return bool(cursor.fetchone())

    def check_specific_intake(self, patient_id: int, med_id: int, scheduled_time: datetime) -> bool:
        """Проверить, был ли подтверждён приём для конкретного времени"""
        cursor = self.conn.cursor()
        start_time = scheduled_time - timedelta(seconds=30)
        end_time = scheduled_time + timedelta(seconds=30)

        cursor.execute(
            """
            SELECT 1 FROM medication_intake_log
            WHERE patient_id = ? AND medication_id = ?
            AND datetime(intake_time) BETWEEN datetime(?) AND datetime(?)
            """,
            (
                patient_id,
                med_id,
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        return bool(cursor.fetchone())

    def log_missed_intake(self, patient_id: int, med_id: int, scheduled_time: datetime) -> bool:
        """Зафиксировать пропущенный приём лекарства"""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO medication_intake_log
               (patient_id, medication_id, intake_time)
               VALUES (?, ?, ?)""",
            (patient_id, med_id, scheduled_time.strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def log_missed_intake_with_notification(self, patient_id: int, med_id: int, scheduled_time: datetime) -> Optional[Dict]:
        """Зафиксировать пропуск и вернуть данные для уведомления врача"""
        if self.log_missed_intake(patient_id, med_id, scheduled_time):
            patient = self.get_patient(patient_id)
            medication = self.get_medication(med_id)
            doctor_id = self.get_doctor_id_by_patient(patient_id)
            
            if patient and medication and doctor_id:
                return {
                    'patient_name': patient.get('name', f'Пациент {patient_id}'),
                    'medication_name': medication['name'],
                    'scheduled_time': scheduled_time,
                    'doctor_id': doctor_id,
                    'status': 'missed'
                }
        return None

    def get_intake_history(self, patient_id: int, days: int = 7) -> List[Dict]:
        """Получить историю приёма лекарств"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT m.name, mil.intake_time 
               FROM medication_intake_log mil
               JOIN medications m ON mil.medication_id = m.medication_id
               WHERE mil.patient_id = ?
               AND DATE(mil.intake_time) >= DATE('now', '-' || ? || ' days')
               ORDER BY mil.intake_time DESC""",
            (patient_id, days)
        )
        return [{
            'medication_name': row[0],
            'intake_time': row[1]
        } for row in cursor.fetchall()]

    # ===== Служебные методы =====
    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()