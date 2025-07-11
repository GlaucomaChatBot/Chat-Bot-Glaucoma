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

info_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="info_1")],
        [InlineKeyboardButton(text="2", callback_data="info_2")],
        [InlineKeyboardButton(text="3", callback_data="info_3")],
        [InlineKeyboardButton(text="4", callback_data="info_4")],
        [InlineKeyboardButton(text="5", callback_data="info_5")],
        [InlineKeyboardButton(text="6", callback_data="info_6")],
        [InlineKeyboardButton(text="7", callback_data="info_7")],
        [InlineKeyboardButton(text="8", callback_data="info_8")],
        [InlineKeyboardButton(text="9", callback_data="info_9")],
        [InlineKeyboardButton(text="10", callback_data="info_10")],
        [InlineKeyboardButton(text="11", callback_data="info_11")],
        [InlineKeyboardButton(text="12", callback_data="info_12")],
        [InlineKeyboardButton(text="13", callback_data="info_13")],
        [InlineKeyboardButton(text="14", callback_data="info_14")],
        [InlineKeyboardButton(text="15", callback_data="info_15")],
        [InlineKeyboardButton(text="16", callback_data="info_16")],
        [InlineKeyboardButton(text="17", callback_data="info_17")],
        [InlineKeyboardButton(text="18", callback_data="info_18")],
        [InlineKeyboardButton(text="19", callback_data="info_19")],
        [InlineKeyboardButton(text="20", callback_data="info_20")],
        [InlineKeyboardButton(text="21", callback_data="info_21")],
        [InlineKeyboardButton(text="22", callback_data="info_22")],
        [InlineKeyboardButton(text="23", callback_data="info_23")],
        [InlineKeyboardButton(text="24", callback_data="info_24")],
        [InlineKeyboardButton(text="25", callback_data="info_25")],
        [InlineKeyboardButton(text="26", callback_data="info_26")],
        [InlineKeyboardButton(text="27", callback_data="info_27")],
        [InlineKeyboardButton(text="28", callback_data="info_28")],
        [InlineKeyboardButton(text="29", callback_data="info_29")],
        [InlineKeyboardButton(text="30", callback_data="info_30")],
        [InlineKeyboardButton(text="31", callback_data="info_31")],
        [InlineKeyboardButton(text="32", callback_data="info_32")],
        [InlineKeyboardButton(text="33", callback_data="info_33")],
        [InlineKeyboardButton(text="34", callback_data="info_34")],
        [InlineKeyboardButton(text="35", callback_data="info_35")],
        [InlineKeyboardButton(text="36", callback_data="info_36")],
        [InlineKeyboardButton(text="37", callback_data="info_37")],
        [InlineKeyboardButton(text="38", callback_data="info_38")],
        [InlineKeyboardButton(text="39", callback_data="info_39")],
        [InlineKeyboardButton(text="40", callback_data="info_40")],
        [InlineKeyboardButton(text="41", callback_data="info_41")],
        [InlineKeyboardButton(text="42", callback_data="info_42")],
       
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ]
)