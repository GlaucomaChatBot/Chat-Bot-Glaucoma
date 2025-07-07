from typing import List, Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

def get_confirmation_keyboard(medication_id: int, scheduled_time: datetime = None) -> InlineKeyboardMarkup:
    callback_data = f"confirm_{medication_id}"
    if scheduled_time:
        callback_data += f"_{scheduled_time.strftime('%Y%m%d_%H%M')}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data=callback_data)]
    ])
    return keyboard

def get_doctor_selection_keyboard(doctors: List[Dict]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Врач {d['doctor_id']} ({d.get('name', '')})", 
                            callback_data=f"select_doctor_{d['doctor_id']}")]
        for d in doctors
    ])
    return keyboard

def get_medication_management_keyboard(medication_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить", callback_data=f"delete_med_{medication_id}")]
    ])
    return keyboard