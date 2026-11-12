"""
CyberGlow Neon Studio — Aiogram 3.x Telegram Bot Companion
Handles figure catalog, custom sketch submission, calculation wizard, and lead alerts.
"""

import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from backend.app import compute_tube_metrics

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc")
OWNER_ID = int(os.environ.get("TELEGRAM_OWNER_ID", "1387913438"))
OWNER_USERNAME = os.environ.get("TELEGRAM_OWNER_USERNAME", "@Idrisov_prod")

router = Router()

class SignCalculationState(StatesGroup):
    waiting_for_text = State()
    waiting_for_color = State()
    waiting_for_contact = State()

class CustomSketchState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_details = State()
    waiting_for_contact = State()

def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏮 Каталог готовых фигур", callback_data="catalog_list")],
        [InlineKeyboardButton(text="📐 Рассчитать надпись", callback_data="calc_wizard")],
        [InlineKeyboardButton(text="📸 Заказать по фото / эскизу", callback_data="custom_sketch")],
        [InlineKeyboardButton(text="💬 Менеджер студии", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")]
    ])

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🏮 <b>Добро пожаловать в CyberGlow Neon Studio!</b>\n\n"
        "Мы создаем премиальные LED-неоновые вывески в стилистике ночного Токио.\n\n"
        "⚡ <b>Наши преимущества:</b>\n"
        "• Японский силикон 2-го поколения (равномерное свечение)\n"
        "• Гарантия 24 месяца\n"
        "• Срок изготовления: 3–5 рабочих дней\n"
        "• Доставка по всей РФ и миру\n\n"
        "Выберите действие в меню ниже:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🏮 <b>Главное меню CyberGlow:</b>", parse_mode="HTML", reply_markup=get_main_menu())
    await call.answer()

# --- Catalog Handlers ---
@router.callback_query(F.data == "catalog_list")
async def cb_catalog(call: CallbackQuery):
    figures = database.get_all_figures()
    keyboard_buttons = []
    
    for fig in figures:
        btn_text = f"{fig['title']} — {fig['price_rub']:,} ₽".replace(",", " ")
        keyboard_buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"fig_{fig['slug']}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")])
    
    text = "🏮 <b>Каталог бестселлеров CyberGlow:</b>\nВыберите фигуру для просмотра характеристик:"
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons))
    await call.answer()

@router.callback_query(F.data.startswith("fig_"))
async def cb_figure_detail(call: CallbackQuery):
    slug = call.data.replace("fig_", "")
    fig = database.get_figure_by_slug(slug)
    
    if not fig:
        await call.answer("Фигура не найдена", show_alert=True)
        return

    text = (
        f"✨ <b>{fig['title']}</b>\n\n"
        f"📝 {fig['description']}\n\n"
        f"📐 <b>Размеры:</b> {fig['dimensions']}\n"
        f"〰️ <b>Длина неона:</b> {fig['tube_length_m']} м\n"
        f"⚡ <b>Мощность:</b> {fig['power_watts']} W (блок питания в комплекте)\n"
        f"💰 <b>Стоимость:</b> {fig['price_rub']:,} ₽\n"
    ).replace(",", " ")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Заказать эту фигуру", callback_data=f"order_fig_{fig['slug']}")],
        [InlineKeyboardButton(text="⬅️ К каталогу", callback_data="catalog_list")]
    ])
    
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("order_fig_"))
async def cb_order_figure(call: CallbackQuery):
    slug = call.data.replace("order_fig_", "")
    fig = database.get_figure_by_slug(slug)
    
    user = call.from_user
    username = f"@{user.username}" if user.username else f"ID {user.id}"
    
    quote_data = {
        "client_name": user.full_name,
        "contact": username,
        "sign_text": fig['title'],
        "font_name": "Figure Preset",
        "color_name": fig['color_primary'],
        "wall_texture": "acrylic",
        "tube_length_m": fig['tube_length_m'],
        "power_watts": fig['power_watts'],
        "total_price_rub": fig['price_rub'],
        "notes": f"Заказ готовой фигуры {fig['title']}"
    }
    quote_id = database.save_quote(quote_data)
    
    # Notify user
    await call.message.edit_text(
        f"🎉 <b>Заявка #{quote_id} принята!</b>\n\n"
        f"Вы выбрали: <b>{fig['title']}</b>\n"
        f"Сумма: <b>{fig['price_rub']:,} ₽</b>\n\n"
        f"Мастер CyberGlow ({OWNER_USERNAME}) свяжется с вами в течение 10–15 минут для согласования доставки!".replace(",", " "),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
        ])
    )
    await call.answer()

# --- Calculation Wizard Handlers ---
@router.callback_query(F.data == "calc_wizard")
async def cb_calc_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(SignCalculationState.waiting_for_text)
    await call.message.edit_text(
        "📐 <b>Калькулятор неоновой вывески</b>\n\n"
        "Отправьте текст, который вы хотите видеть на вывеске (например: <i>TOKYO BAR</i>):",
        parse_mode="HTML"
    )
    await call.answer()

@router.message(SignCalculationState.waiting_for_text)
async def process_calc_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Пожалуйста, введите непустой текст:")
        return
    
    await state.update_data(sign_text=text)
    await state.set_state(SignCalculationState.waiting_for_color)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Tokyo Cyan", callback_data="color_Tokyo Cyan"),
         InlineKeyboardButton(text="🌸 Sakura Pink", callback_data="color_Sakura Pink")],
        [InlineKeyboardButton(text="🟢 Electric Lime", callback_data="color_Electric Lime"),
         InlineKeyboardButton(text="🟣 Ultraviolet", callback_data="color_Ultraviolet")],
        [InlineKeyboardButton(text="🟠 Sunset Amber", callback_data="color_Sunset Amber"),
         InlineKeyboardButton(text="⚪ Ice White", callback_data="color_Ice White")]
    ])
    
    await message.answer(f"Текст принят: <b>{text}</b>\nВыберите желаемый цвет свечения:", parse_mode="HTML", reply_markup=kb)

@router.callback_query(SignCalculationState.waiting_for_color, F.data.startswith("color_"))
async def process_calc_color(call: CallbackQuery, state: FSMContext):
    color = call.data.replace("color_", "")
    data = await state.get_data()
    text = data.get("sign_text", "NEON")
    
    metrics = compute_tube_metrics(text, font_name="Monoline Neon", height_cm=20.0)
    await state.update_data(color=color, metrics=metrics)
    await state.set_state(SignCalculationState.waiting_for_contact)
    
    report = (
        f"📊 <b>Предварительный расчет вывески</b>\n\n"
        f"🔤 <b>Текст:</b> {text}\n"
        f"🌈 <b>Цвет:</b> {color}\n"
        f"📐 <b>Ориентировочный размер:</b> {metrics['dimensions_cm']}\n"
        f"〰️ <b>Длина неона:</b> {metrics['tube_length_m']} м\n"
        f"⚡ <b>Мощность:</b> {metrics['power_watts']} W ({metrics['recommended_psu']})\n"
        f"💰 <b>Стоимость изготовления:</b> {metrics['total_price_rub']:,} ₽\n\n"
        f"<i>Отправьте ваш контактный номер телефона или подтвердите заявку:</i>"
    ).replace(",", " ")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Заказать вывеску", callback_data="confirm_calc_order")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")]
    ])
    
    await call.message.edit_text(report, parse_mode="HTML", reply_markup=kb)
    await call.answer()

@router.callback_query(SignCalculationState.waiting_for_contact, F.data == "confirm_calc_order")
@router.message(SignCalculationState.waiting_for_contact)
async def process_calc_finish(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = event.from_user
    username = f"@{user.username}" if user.username else f"ID {user.id}"
    contact = event.text if isinstance(event, Message) else username
    
    metrics = data.get("metrics", {})
    quote_data = {
        "client_name": user.full_name,
        "contact": contact,
        "sign_text": data.get("sign_text"),
        "font_name": "Monoline Neon",
        "color_name": data.get("color"),
        "wall_texture": "brick",
        "tube_length_m": metrics.get("tube_length_m", 2.0),
        "power_watts": metrics.get("power_watts", 30),
        "total_price_rub": metrics.get("total_price_rub", 8900),
        "notes": "Расчет через Telegram-бот калькулятор"
    }
    quote_id = database.save_quote(quote_data)
    await state.clear()
    
    msg_text = (
        f"🎉 <b>Заявка #{quote_id} зарегистрирована!</b>\n\n"
        f"Текст вывески: <b>{data.get('sign_text')}</b>\n"
        f"Сумма: <b>{metrics.get('total_price_rub', 0):,} ₽</b>\n\n"
        f"Мы подготовим бесплатный 3D-макет и напишем вам в ближайшее время!".replace(",", " ")
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(msg_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
        ]))
        await event.answer()
    else:
        await event.answer(msg_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
        ]))

# --- Custom Sketch Intake ---
@router.callback_query(F.data == "custom_sketch")
async def cb_custom_sketch_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(CustomSketchState.waiting_for_photo)
    await call.message.edit_text(
        "📸 <b>Индивидуальный расчет по фото / эскизу</b>\n\n"
        "Отправьте фотографию, рисунок или скетч вашей будущей вывески в чат (форматы JPG, PNG):",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="main_menu")]
        ])
    )
    await call.answer()

@router.message(CustomSketchState.waiting_for_photo, F.photo)
async def process_sketch_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await state.set_state(CustomSketchState.waiting_for_details)
    await message.answer(
        "✅ Фото успешно получено!\n\n"
        "Укажите ориентировочные размеры (например: <i>80х50 см</i>) и желаемый цвет свечения:",
        parse_mode="HTML"
    )

@router.message(CustomSketchState.waiting_for_photo, ~F.photo)
async def process_sketch_invalid(message: Message):
    await message.answer("⚠️ Пожалуйста, отправьте эскиз или фото вывески в формате JPG или PNG.")

@router.message(CustomSketchState.waiting_for_details)
async def process_sketch_details(message: Message, state: FSMContext):
    details = message.text.strip()
    data = await state.get_data()
    user = message.from_user
    username = f"@{user.username}" if user.username else f"ID {user.id}"
    
    quote_data = {
        "client_name": user.full_name,
        "contact": username,
        "sign_text": "Кастомный эскиз",
        "font_name": "Custom Vector",
        "color_name": "По согласованию",
        "wall_texture": "acrylic",
        "tube_length_m": 3.0,
        "power_watts": 45,
        "total_price_rub": 12500,
        "notes": f"Параметры заказчика: {details}",
        "photo_file_id": data.get("photo_file_id")
    }
    quote_id = database.save_quote(quote_data)
    await state.clear()
    
    await message.answer(
        f"🎯 <b>Заявка #{quote_id} на расчет макета принята!</b>\n\n"
        f"Дизайнер CyberGlow изучит ваш скетч и свяжется с вами с точной 3D-визуализацией и сметой в течение 30 минут.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
        ])
    )

def create_bot_and_dispatcher():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    return bot, dp

async def main():
    bot, dp = create_bot_and_dispatcher()
    print("Starting CyberGlow Telegram Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
