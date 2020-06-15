import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from neuralstyletransfer import Transs

logging.basicConfig(level=logging.INFO)

API_TOKEN = '<tokenApi>'

bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    input = State()  
    style = State()  


async def send_to_admin(*args):
    await bot.send_message(chat_id=<AdminId>, text="Bot has been launched!")


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.input.set()

    await message.reply("Hi there! Send your photo which you want to change.")

@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    """
    Help
    """

    await message.reply("Hello. This bot will transfer your picture in the style you want."
                        " Use command: /start to initiate style transferring."
                        " Use command: /cancel  or type: cancel to cancel the style transeferring stage.")



# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


# Check the First Image.
@dp.message_handler(content_types=['text'], state=Form.input)
async def process_age_invalid(message: types.Message):

    return await message.reply("It's gotta be a photo")


@dp.message_handler(state=Form.input, content_types=['photo'])
async def process_name(message: types.Message, state: FSMContext):

    await message.photo[-1].download('input'+str(message.from_user.id)+'.jpg')

    await Form.next()
    await message.reply("Send your style, which you want to apply.")


# Check the Second Image.
@dp.message_handler(content_types=['text'], state=Form.style)
async def process_age_invalid(message: types.Message):

    return await message.reply("It's gotta be a photo")


@dp.message_handler(content_types=['photo'], state=Form.style)
async def process_age(message: types.Message, state: FSMContext):
    
    await message.photo[-1].download('style'+str(message.from_user.id)+'.jpg')
    await bot.send_message(chat_id=message.from_user.id, text="Loading... It will take time. Really.")
    tr = Transs('input'+str(message.from_user.id)+'.jpg', 'style'+str(message.from_user.id)+'.jpg',
                'output'+str(message.from_user.id)+'.jpg')
    logging.info('Started Style Transfering')
    tr.go()
    logging.info('Finish Style Transfering')
    with open('output'+str(message.from_user.id)+'.jpg', 'rb') as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption="Your photo!")
    await bot.send_message(chat_id=message.from_user.id, text="Here you go! See you Soon!")
    # Finish conversation
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=send_to_admin)
