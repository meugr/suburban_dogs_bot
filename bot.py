import telebot
from telebot import types
import config
import parser
import little_db

bot = telebot.TeleBot(config.TG_TOKEN)
remove_markup = types.ReplyKeyboardRemove()
markup = types.ReplyKeyboardMarkup()
markup.row('Сегодня', 'Завтра')


@bot.message_handler(commands=['start'])
def start_message(message):
    little_db.create_new_user(message.chat.id)
    bot.send_message(message.chat.id, 'Добро пожаловать.')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Узнай актуальное расписание \
электричек!\nВыберите свой часовой пояс для корректной работы.')


@bot.message_handler(commands=['cancel'])
def cancel_search(message):
    print(little_db.get_info(message.chat.id))
    little_db.reset_info(message.chat.id)
    bot.send_message(message.chat.id, 'Вы отменили выбор станции.',
                     reply_markup=remove_markup)


@bot.message_handler(commands=['cmd'],
                     func=lambda message: little_db.get_info(
                     message.chat.id) == [None])
def get_departure(message):
    little_db.set_empty_info(message.chat.id)
    bot.send_message(message.chat.id, 'Введите станцию отправления')
    print(little_db.get_info(message.chat.id))


@bot.message_handler(func=lambda message:
                     len(little_db.get_info(message.chat.id)) == 0)
def get_arrival(message):
    little_db.append_info(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Введите станцию прибытия')
    print(little_db.get_info(message.chat.id))


@bot.message_handler(func=lambda message:
                     (len(little_db.get_info(message.chat.id)) == 1) and
                     (little_db.get_info(message.chat.id) != [None]))
def get_date(message):
    little_db.append_info(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Выберете дату', reply_markup=markup)
    print(little_db.get_info(message.chat.id))


@bot.message_handler(func=lambda message:
                     len(little_db.get_info(message.chat.id)) == 2)
def return_result(message):
    bot.send_message(
        message.chat.id, 'Загружаю расписание...', reply_markup=remove_markup)
    little_db.append_info(message.chat.id, message.text)
    print(little_db.get_info(message.chat.id))
    trains = parser.test_main(little_db.get_info(message.chat.id))
    for train in trains:
        bot.send_message(message.chat.id, train)
    little_db.reset_info(message.chat.id)







if __name__ == '__main__':
    bot.polling(none_stop=True)
