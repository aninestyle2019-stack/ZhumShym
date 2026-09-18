import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = "8574888559:AAFTFR39vbk4XKwxppSS_3uZyZvT1aXWzSQ"
ADMIN_ID = 1101629808  # Твой ID администратора

router = Router()


class CandidateForm(StatesGroup):
  name = State()
  age = State()
  phone = State()
  experience = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
  await state.clear()
  args = message.text.split(maxsplit=1)

  if len(args) <= 1:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🌐 Открыть сайт с вакансиями",
                url=(
                    "https://sites.google.com/view/zhumshym/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
                ),
            )
        ]]
    )
    await message.answer(
        "👋 Привет! Добро пожаловать в службу найма **ЖумШым**.\n\n"
        "Чтобы подать заявку, выберите интересующую вас вакансию и нажмите"
        " кнопку отклика на нашем сайте:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return

  vacancy = args[1]
  await state.update_data(vacancy=vacancy)
  await state.set_state(CandidateForm.name)
  await message.answer(
      f"👋 Привет! Добро пожаловать в службу найма **ЖумШым**!\n"
      f"Ты откликаешься на вакансию: <b>{vacancy}</b>.\n\n"
      f"Давай заполним небольшую анкету. Как тебя зовут? (Введите ФИО или имя)",
      parse_mode="HTML",
  )


@router.message(CandidateForm.name)
async def process_name(message: Message, state: FSMContext):
  user_input = message.text.strip()
  if not re.match(r"^[А-Яа-яЁёA-Za-z\s\-]{2,50}$", user_input):
    await message.answer(
        "❌ Пожалуйста, введите реальное имя (используйте только буквы, от 2 до"
        " 50 символов)."
    )
    return

  await state.update_data(name=user_input)
  await state.set_state(CandidateForm.age)
  await message.answer(
      "Сколько тебе лет? (введи цифрами, например: 20)\n<i>(Обратите внимание:"
      " работа доступна только с 18 лет)</i>",
      parse_mode="HTML",
  )


@router.message(CandidateForm.age)
async def process_age(message: Message, state: FSMContext):
  if not message.text.isdigit():
    await message.answer(
        "❌ Возраст должен состоять только из цифр. Пожалуйста, введите возраст"
        " цифрами:"
    )
    return

  age = int(message.text)

  if age < 18:
    await message.answer(
        "❌ К сожалению, у нас нельзя работать лицам младше 18 лет."
    )
    return
  if age > 60:
    await message.answer(
        "❌ Пожалуйста, укажи реальный возраст (до 60 лет): цифровое"
        " значение:"
    )
    return

  await state.update_data(age=age)
  await state.set_state(CandidateForm.phone)
  await message.answer(
      "📱 Напиши свой номер телефона для связи (например: +7 701 123 45 67):"
  )


@router.message(CandidateForm.phone)
async def process_phone(message: Message, state: FSMContext):
  user_phone = message.text.strip()
  digits_only = "".join([c for c in user_phone if c.isdigit()])

  if not (10 <= len(digits_only) <= 12):
    await message.answer(
        "❌ Неверный формат номера. Пожалуйста, введите именно номер телефона"
        " (цифрами, например: +7 701 123 45 67):"
    )
    return

  await state.update_data(phone=user_phone)
  await state.set_state(CandidateForm.experience)
  await message.answer(
      "💼 Расскажи коротко о своем опыте работы (если опыта нет, напиши «нет"
      " опыта»):"
  )


@router.message(CandidateForm.experience)
async def process_experience(message: Message, state: FSMContext):
  experience = message.text.strip()
  await state.update_data(experience=experience)
  data = await state.get_data()

  admin_message = (
      f"🔥 **Новый отклик на вакансию!**\n\n"
      f"📌 **Вакансия:** {data.get('vacancy')}\n"
      f"👤 **Имя:** {data.get('name')}\n"
      f"🎂 **Возраст:** {data.get('age')}\n"
      f"📞 **Телефон:** {data.get('phone')}\n"
      f"💼 **Опыт:** {data.get('experience')}"
  )

  try:
    await message.bot.send_message(
        chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown"
    )
    await message.answer(
        "✅ Спасибо! Твоя анкета успешно отправлена менеджеру. Мы свяжемся с"
        " тобой в ближайшее время!"
    )
  except Exception as e:
    await message.answer(
        f"❌ Ошибка при отправке админу: {e}\nУбедись, что ты нажал /start в боте"
        " администратора!"
    )
    logging.error(f"Ошибка отправки админу: {e}")

  await state.clear()


async def main():
  logging.basicConfig(level=logging.INFO)
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(router)
  print("Бот запущен и готов принимать анкеты!")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
