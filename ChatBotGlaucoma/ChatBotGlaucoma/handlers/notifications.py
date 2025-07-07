from aiogram.types import CallbackQuery
from aiogram import F, Router
from instance import db, bot
from keyboards import inline
from datetime import datetime, timedelta
import asyncio

router = Router()

# Глобальные переменные для отслеживания состояния уведомлений
active_notifications = {}  # {notification_key: timestamp}
pending_confirmations = {}  # {confirmation_key: data}
last_notification_check = datetime.min  # Время последней проверки

async def send_medication_reminders():
    """Функция для периодической отправки уведомлений о приёме лекарств"""
    global last_notification_check
    
    while True:
        try:
            current_time = datetime.now()
            
            # Увеличиваем частоту проверки для точности
            if (current_time - last_notification_check).total_seconds() < 10:
                await asyncio.sleep(1)
                continue
                
            last_notification_check = current_time
            
            # Получаем всех пациентов и их лекарства
            all_medications = []
            patients = db.get_all_patients()
            
            for patient in patients:
                meds = db.get_patient_medications(patient['patient_id'])
                for med in meds:
                    med['patient_id'] = patient['patient_id']
                    all_medications.append(med)
            
            # Очищаем старые уведомления
            await cleanup_old_notifications()
            
            # Для каждого лекарства рассчитываем точное время следующего приема
            for med in all_medications:
                patient_id = med['patient_id']
                med_id = med['medication_id']
                
                # Парсим время начала приема
                try:
                    start_time = datetime.strptime(med['start_time'], "%H:%M:%S").time()
                except ValueError:
                    print(f"Ошибка формата времени для лекарства {med['name']}")
                    continue
                
                # Текущие дата и время
                now = current_time
                today = now.date()
                current_time_only = now.time()
                
                # Рассчитываем следующее время приема
                first_intake_today = datetime.combine(today, start_time)
                
                # Если текущее время меньше времени начала
                if current_time_only < start_time:
                    next_intake = first_intake_today
                else:
                    # Рассчитываем сколько интервалов прошло
                    elapsed = now - first_intake_today
                    intervals_passed = elapsed.total_seconds() // (med['interval_minutes'] * 60)
                    next_intake = first_intake_today + timedelta(minutes=med['interval_minutes'] * (intervals_passed + 1))
                
                # Проверяем, что следующее время приема наступило или наступит в течение 10 секунд
                time_diff = (next_intake - now).total_seconds()
                if 0 <= time_diff < 10:  # Только если время приема наступило или наступит в ближайшие 10 секунд
                    notification_key = f"{patient_id}_{med_id}_{next_intake.strftime('%Y%m%d_%H%M')}"
                    
                    # Пропускаем если уведомление уже отправлено
                    if notification_key in active_notifications:
                        continue
                    
                    try:
                        # Ждем точного времени приема
                        if time_diff > 0:
                            await asyncio.sleep(time_diff)
                        
                        # Двойная проверка после сна
                        current_time_after_sleep = datetime.now()
                        if abs((next_intake - current_time_after_sleep).total_seconds()) > 30:
                            continue
                            
                        # Отправляем уведомление
                        await bot.send_message(
                            chat_id=patient_id,
                            text=f"💊 Время принять лекарство!\n\n"
                                 f"🔸 {med['name']}\n"
                                 f"⏰ Запланировано на: {next_intake.strftime('%H:%M')}\n"
                                 f"⚠️ У вас есть 30 минут для подтверждения приема",
                            reply_markup=inline.get_confirmation_keyboard(med_id, next_intake)
                        )
                        
                        # Записываем факт отправки уведомления
                        active_notifications[notification_key] = next_intake
                        
                        # Добавляем в ожидающие подтверждения
                        pending_confirmations[notification_key] = {
                            'patient_id': patient_id,
                            'med_id': med_id,
                            'notification_time': next_intake,
                            'scheduled_time': next_intake
                        }
                        
                        print(f"Отправлено уведомление в {next_intake.strftime('%H:%M:%S')}: {notification_key}")
                        
                    except Exception as e:
                        print(f"Ошибка отправки уведомления пациенту {patient_id}: {e}")
            
            # Проверяем просроченные подтверждения
            await check_overdue_confirmations()
            
            await asyncio.sleep(5)  # Короткая пауза между итерациями
            
        except Exception as e:
            print(f"Ошибка в send_medication_reminders: {e}")
            await asyncio.sleep(10)

async def cleanup_old_notifications():
    """Очистка старых уведомлений"""
    current_time = datetime.now()
    old_keys = []
    
    for key, timestamp in active_notifications.items():
        # Удаляем уведомления старше 1 часа
        if (current_time - timestamp).total_seconds() > 3600:
            old_keys.append(key)
    
    for key in old_keys:
        del active_notifications[key]

async def check_overdue_confirmations():
    """Проверка просроченных подтверждений"""
    current_time = datetime.now()
    overdue_keys = []
    
    for key, confirmation in pending_confirmations.items():
        # Если прошло больше 30 минут с момента уведомления
        if (current_time - confirmation['notification_time']).total_seconds() > 1800:
            patient_id = confirmation['patient_id']
            med_id = confirmation['med_id']
            
            # Проверяем, не было ли подтверждения
            if not db.check_intake(patient_id, med_id):
                db.log_missed_intake(patient_id, med_id, confirmation['notification_time'])
                await notify_doctor_missed_intake(patient_id, med_id, confirmation['notification_time'])
                print(f"Прием помечен как пропущенный: {key}")
            
            overdue_keys.append(key)
    
    # Удаляем обработанные подтверждения
    for key in overdue_keys:
        del pending_confirmations[key]

async def notify_doctor_missed_intake(patient_id: int, med_id: int, scheduled_time: datetime):
    """Уведомить врача о пропущенном приеме"""
    try:
        doctor_id = db.get_doctor_id_by_patient(patient_id)
        if doctor_id:
            patient = db.get_patient(patient_id)
            medication = db.get_medication(med_id)
            
            if patient and medication:
                patient_name = patient.get('name', f'Пациент {patient_id}')
                med_name = medication['name']
                
                await bot.send_message(
                    chat_id=doctor_id,
                    text=f"⚠️ Пропущен прием лекарства\n\n"
                         f"👤 Пациент: {patient_name}\n"
                         f"💊 Лекарство: {med_name}\n"
                         f"⏰ Запланированное время: {scheduled_time.strftime('%d.%m.%Y %H:%M')}\n"
                         f"❌ Прием не был подтвержден в течение 30 минут"
                )
    except Exception as e:
        print(f"Ошибка при уведомлении врача о пропуске: {e}")

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_medication(callback: CallbackQuery):
    """Обработка подтверждения приёма лекарства"""
    try:
        print(f"Получено подтверждение: {callback.data}")
        
        parts = callback.data.split("_")
        medication_id = int(parts[1])
        patient_id = callback.from_user.id
        
        # Извлекаем scheduled_time из callback_data
        scheduled_time = None
        if len(parts) > 2:
            try:
                # Формат: confirm_123_20230715_1530
                date_str = parts[2]
                time_str = parts[3]
                scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M")
                print(f"Распознано время приёма: {scheduled_time}")
            except Exception as e:
                print(f"Ошибка парсинга времени: {e}")
                scheduled_time = datetime.now()
        else:
            scheduled_time = datetime.now()
        
        # Проверяем, не было ли уже подтверждения для этого конкретного времени
        if db.check_specific_intake(patient_id, medication_id, scheduled_time):
            await callback.answer("❌ Вы уже подтвердили этот приём ранее!", show_alert=True)
            return
        
        # Записываем приём в базу данных
        success = db.log_intake(patient_id, medication_id, scheduled_time)
        if success:
            med = db.get_medication(medication_id)
            if med:
                # Обновляем сообщение
                await callback.message.edit_text(
                    text=f"✅ Приём лекарства '{med['name']}' успешно подтверждён!\n"
                         f"⏰ Время: {scheduled_time.strftime('%d.%m.%Y %H:%M')}",
                    reply_markup=None
                )
                
                # Удаляем из ожидающих подтверждения
                confirmation_key = f"{patient_id}_{medication_id}_{scheduled_time.strftime('%Y%m%d_%H%M')}"
                if confirmation_key in pending_confirmations:
                    del pending_confirmations[confirmation_key]
                    print(f"Подтверждение удалено: {confirmation_key}")
            else:
                await callback.message.edit_text(
                    text="❌ Лекарство не найдено! Обратитесь к врачу.",
                    reply_markup=None
                )
        else:
            await callback.message.edit_text(
                text="❌ Ошибка при подтверждении! Попробуйте снова.",
                reply_markup=None
            )
        
        await callback.answer()
    except Exception as e:
        import traceback
        print(f"Критическая ошибка в confirm_medication: {e}\n{traceback.format_exc()}")
        await callback.answer("Произошла критическая ошибка. Сообщите врачу.", show_alert=True)