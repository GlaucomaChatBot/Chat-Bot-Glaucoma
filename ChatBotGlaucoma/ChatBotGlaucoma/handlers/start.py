from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.filters import Command
from instance import main_router, db, bot, user_states
from keyboards import reply, inline
from datetime import datetime, timedelta
import asyncio
import re
import sqlite3
from typing import List, Dict

@main_router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    
    # Проверяем, есть ли пользователь в базе как пациент или врач
    patient = db.get_patient(user_id)
    doctor = db.get_doctor(user_id)
    
    if not patient and not doctor:
        await message.answer(
            "Добро пожаловать! Вы врач или пациент?",
            reply_markup=await reply.role_selection_keyboard()
        )
    elif doctor:
        await message.answer(
            "Добро пожаловать, доктор!",
            reply_markup=await reply.doctor_menu_keyboard()
        )
    else:
        await show_main_menu(message)

@main_router.message(F.text == "Я врач")
async def register_doctor(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    try:
        db.add_doctor(user_id, full_name)
        await message.answer(
            "Вы успешно зарегистрированы как врач!",
            reply_markup=await reply.doctor_menu_keyboard()
        )
    except Exception as e:
        await message.answer("Ошибка регистрации врача. Попробуйте позже.")
        print(f"Ошибка при добавлении врача: {e}")

@main_router.message(F.text == "Я пациент")
async def register_patient(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    
    # Проверяем, зарегистрирован ли уже как пациент
    if db.get_patient(user_id):
        await message.answer(
            "Вы уже зарегистрированы как пациент!",
            reply_markup=await reply.main_menu_keyboard()
        )
        return
    
    # Пытаемся добавить пациента
    if not db.add_patient(user_id, full_name):
        await message.answer(
            "❌ Ошибка регистрации. Попробуйте позже.",
            reply_markup=await reply.role_selection_keyboard()
        )
        return
    
    # Получаем список врачей
    doctors = db.get_all_doctors()
    
    if not doctors:
        # Если врачей нет - сразу показываем меню пациента
        await message.answer(
            "✅ Вы успешно зарегистрированы!\n"
            "⚠️ В системе пока нет врачей. Вы сможете выбрать врача позже.",
            reply_markup=await reply.main_menu_keyboard()
        )
    else:
        # Если врачи есть - предлагаем выбрать
        keyboard = inline.get_doctor_selection_keyboard(doctors)
        
        # Отправляем сообщение с inline-клавиатурой выбора врача
        await message.answer(
            "✅ Вы успешно зарегистрированы!\n"
            "Теперь выберите своего врача:",
            reply_markup=await reply.main_menu_keyboard()
        )
        await message.answer(
            "Выберите врача из списка:",
            reply_markup=keyboard
        )

@main_router.message(F.text == "Мои пациенты")
async def show_doctor_patients(message: Message):
    user_id = message.from_user.id
    doctor = db.get_doctor(user_id)
    
    if not doctor:
        await message.answer("Вы не зарегистрированы как врач!")
        return
    
    patients = db.get_patients_by_doctor(user_id)
    
    if not patients:
        await message.answer("У вас пока нет пациентов.")
        return
    
    response = "👥 Ваши пациенты:\n\n"
    for patient in patients:
        patient_name = patient.get('name', f'Пациент {patient["patient_id"]}')
        response += f"👤 {patient_name}\n"
        response += f"ID: {patient['patient_id']}\n"
        response += "────────────────\n"
    
    await message.answer(response)

async def show_main_menu(message: Message):
    user_id = message.from_user.id
    patient = db.get_patient(user_id)
    if patient and not patient.get('doctor_id'):
        await message.answer(
            "Внимание: У вас нет назначенного врача. Выберите врача из списка.",
            reply_markup=await reply.main_menu_keyboard()
        )
    else:
        await message.answer(
            "Главное меню:",
            reply_markup=await reply.main_menu_keyboard()
        )

@main_router.message(F.text == "Мои лекарства")
async def show_medications(message: Message):
    user_id = message.from_user.id
    medications = db.get_patient_medications(user_id)
    if medications:
        for med in medications:
            response = f"- {med['name']} (начало: {med['start_time']}, периодичность: {med['interval_hours']} часов)"
            await message.answer(
                response,
                reply_markup=inline.get_medication_management_keyboard(med['medication_id'])
            )
    else:
        await message.answer(
            "У вас нет назначенных лекарств.",
            reply_markup=await reply.main_menu_keyboard()
        )

@main_router.message(F.text == "Добавить лекарство")
async def add_medication(message: Message):
    user_id = message.from_user.id
    await message.answer(
        "Введите название лекарства, время начала (например, '12:00') и интервал в часах (например, 6 для 6 часов), разделяя пробелами:\nПример: 'Ксилокт 12:00 6'",
        reply_markup=await reply.cancel_keyboard()
    )
    user_states[user_id] = "waiting_for_medication"

@main_router.message(F.text == "Отмена")
async def cancel_action(message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await show_main_menu(message)

@main_router.message(lambda message: message.from_user.id in user_states and 
                   user_states[message.from_user.id] == "waiting_for_medication")
async def process_add_medication(message: Message):
    user_id = message.from_user.id
    try:
        del user_states[user_id]
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("Ошибка формата. Пример: 'Аспирин 08:00 6'",
                               reply_markup=await reply.main_menu_keyboard())
            return

        name, start_time, interval_str = parts[0], parts[1], parts[2]
        
        try:
            interval = int(interval_str)
            if interval <= 0:
                raise ValueError("Интервал должен быть > 0")
                
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', start_time):
                raise ValueError("Неверный формат времени. Используйте HH:MM")
                
        except ValueError as e:
            await message.answer(f"Ошибка: {e}",
                               reply_markup=await reply.main_menu_keyboard())
            return

        full_time = f"{start_time}:00"
        
        try:
            med_id = db.add_medication(name, full_time, interval)
            if med_id and db.assign_medication(user_id, med_id):
                await message.answer(
                    f"✅ Лекарство '{name}' успешно добавлено!\n"
                    f"⏰ Первый прием в {start_time}\n"
                    f"🔄 Повтор каждые {interval} часов",
                    reply_markup=await reply.main_menu_keyboard()
                )
            else:
                raise Exception("Ошибка назначения лекарства")
                
        except sqlite3.Error as e:
            await message.answer(
                "❌ Ошибка при добавлении лекарства. Попробуйте позже.",
                reply_markup=await reply.main_menu_keyboard()
            )
            print(f"Database error: {e}")
            
    except Exception as e:
        await message.answer(
            "❌ Неожиданная ошибка. Попробуйте еще раз.",
            reply_markup=await reply.main_menu_keyboard()
        )
        print(f"Unexpected error: {e}")

@main_router.message(F.text == "История приёмов")
async def show_intake_history(message: Message):
    user_id = message.from_user.id
    history = db.get_intake_history(user_id)
    
    if history:
        response = "📅 История ваших приёмов:\n\n"
        for record in history:
            # Парсим время из базы данных
            intake_time = datetime.strptime(record['intake_time'], "%Y-%m-%d %H:%M:%S")
            response += f"💊 {record['medication_name']}\n"
            response += f"⏰ {intake_time.strftime('%d.%m.%Y %H:%M')}\n"
            response += "────────────────\n"
    else:
        response = "📭 История приёмов пуста. У вас нет записей о приёме лекарств."
    
    await message.answer(response, reply_markup=await reply.main_menu_keyboard())

@main_router.message(F.text == "Выбрать своего врача")
async def choose_doctor(message: Message):
    user_id = message.from_user.id
    doctors = db.get_all_doctors()
    if not doctors:
        await message.answer("Нет зарегистрированных врачей.")
        return
    keyboard = inline.get_doctor_selection_keyboard(doctors)
    await message.answer("Выберите своего врача:", reply_markup=keyboard)

@main_router.callback_query(F.data.startswith("select_doctor_"))
async def process_doctor_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    doctor_id = int(callback.data.split("_")[2])
    if db.update_patient_doctor(user_id, doctor_id):
        await callback.message.edit_text(
            f"Врач успешно назначен как ваш доктор!",
            reply_markup=None
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            "Не удалось назначить врача. Возможно, произошла ошибка.",
            reply_markup=None
        )
        await callback.answer()

@main_router.callback_query(F.data.startswith("delete_med_"))
async def delete_medication(callback: CallbackQuery):
    """Обработка удаления лекарства"""
    try:
        medication_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        # Проверяем, принадлежит ли лекарство пользователю
        patient_medications = db.get_patient_medications(user_id)
        medication_ids = [med['medication_id'] for med in patient_medications]
        
        if medication_id not in medication_ids:
            await callback.answer("❌ Это не ваше лекарство!", show_alert=True)
            return
            
        if db.delete_medication(medication_id):
            await callback.message.edit_text(
                text="✅ Лекарство успешно удалено!",
                reply_markup=None
            )
        else:
            await callback.message.edit_text(
                text="❌ Ошибка при удалении лекарства. Возможно, оно уже удалено.",
                reply_markup=None
            )
        await callback.answer()
    except Exception as e:
        print(f"Ошибка в delete_medication: {e}")
        await callback.answer("Произошла ошибка при удалении.", show_alert=True)