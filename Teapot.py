import logging
import math
import datetime
import sqlite3

import keyboard
from configurations import name, volume, max_t, protection, \
    temperature_controller, supply_voltage, power  # параметры чайника из файла конфигурации
from time import sleep

logging.basicConfig(level=logging.DEBUG,
                    filename="Teapot_log.log",
                    filemode="w",
                    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('dev')


class Teapot:

    def __init__(self):
        self.name = name  # Наименование
        self.volume = 0  # Объем
        self.max_volume = volume  # Максимальный объем чайника
        self.temperature = 18  # Температура воды в чайнике
        self.max_temperature = max_t  # Максимальная температура
        self.protection = protection  # Защита от включения без воды
        self.temperature_controller = temperature_controller  # Терморегулятор
        # self.boiling_time_of_water = boiling_time_of_water  # Время кипения
        self.supply_voltage = supply_voltage  # Напряжение питания
        self.power = power  # Мощность

        db = sqlite3.connect('database.db')
        # with db.cursor() as cursor:
        cursor = db.cursor()

        # # Удаление таблицы бд
        # cursor.execute(
        #     """DROP TABLE IF EXISTS Teapot"""
        # )

        # Создание таблицы бд
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Teapot(
            name TEXT NOT NULL,
            volume TEXT NOT NULL,
            temperature TEXT NOT NULL,
            max_temperature TEXT NOT NULL,
            protection TEXT NOT NULL,
            temperature_controller TEXT NOT NULL,
            supply_voltage TEXT NOT NULL,
            power TEXT NOT NULL,
            operating mode TEXT NOT NULL,
            the_kettle_is_on mode TEXT NOT NULL,
            the_kettle_is_off mode TEXT NOT NULL,
            the_kettle_boiled mode TEXT NOT NULL
            )"""
        )

        txt1 = f'Налейте воды в чайник (максимальный объем составляет {self.max_volume}л):'

        print(f'Выберите режим работы:\n'
              f'1) Тестовое задание.\n'
              f'2) Приближенный к реальности.')
        self.user_response = input()

        if self.user_response == '1':
            print(txt1)
            # Расчет времени закипания воды из ТЗ
            self.boiling_time_of_water = 10
            volume_user = float(input())
            self.my_volume(float(volume_user))

        elif self.user_response == '2':
            print(txt1)
            volume_user = float(input())
            # Расчет реального времени закипания воды по характеристикам чайника
            self.boiling_time_of_water = self.power / 4183 * volume_user * (self.max_temperature - self.temperature)
            self.my_volume(float(volume_user))

        else:
            print('Ошибка, вы выбрали не существующий режим работы! Повторите попытку еще раз!!!\n\n')
            self.__init__()

    #   *************************************************************************************
    #   *              Создание функции для проверки на заполненность воды в чайнике        *
    #   *    INPUT:                                                                         *
    #   *            temperature          - Температура воды в чайнике.                     *
    #   *            volume               - Объем воды в чайнике.                           *
    #   *************************************************************************************
    def temp(self, temperature, volume):
        if self.max_volume >= volume > 0:
            self.volume = volume
            print(f'Вы наполнили {self.volume}л')
            logger.info(f'Вы наполнили {self.volume}л')
            print('Для включения чайника нажмите: o')
            keyboard.wait('o')
            print('Для отключения чайника зажмите: p')
            print('Чайник включен')
            logger.info('Чайник включен')
            self.the_kettle_is_on = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник включен'

            self.teapot_on(self.boiling_time_of_water, temperature)

        elif volume == 0:
            mv_err1 = f'Объем должен быть больше 0л!\n\n'
            logger.error(mv_err1)
            print(mv_err1)
            self.__init__()
        else:
            print(f'Объем должен быть не больше {self.max_volume}!')
            logger.error(f'Объем должен быть не больше {self.max_volume}!')
            self.__init__()

    #   *************************************************************************************
    #   *                   Создание функции для наполнения чайника                         *
    #   *    INPUT:                                                                         *
    #   *            volume               - Объем воды в чайнике.                           *
    #   *************************************************************************************
    def my_volume(self, volume):
        if not isinstance(volume, float):
            logging.error('ValueError, Объем должен быть числом!')
            raise ValueError('Объем должен быть числом!')

        if self.protection == True:
            self.temp(self.temperature, volume)
        else:
            if volume == 0:
                self.volume = volume
                print(f'Вы наполнили {self.volume}л')
                logger.info(f'Вы наполнили {self.volume}л')
                print('Для включения чайника нажмите: o')
                keyboard.wait('o')  # Запустить цикл
                print('Для отключения чайника зажмите: p')
                print('Чайник включен')
                logger.info('Чайник включен')
                print('Чайник сделал "ПШШ ПЫШ пЫЫШШ"')
                logger.info('Чайник сделал "ПШШ ПЫШ пЫЫШШ"')
                print('Чайник сгорел! Купите новый!')
                logger.info('Чайник сгорел! Купите новый!')
                exit()
            if self.max_volume >= volume > 0:
                self.temp(self.temperature, volume)
            else:
                mv_err1 = f'Объем должен быть не больше {self.max_volume}!'
                logger.error(mv_err1)
                print(mv_err1)
                print(f'Налейте воды в чайник (максимальный объем составляет {self.max_volume}л):')
                mv_temp1 = input()
                self.my_volume(float(mv_temp1))
                # raise IndexError(mv_err1)

    #   *************************************************************************************
    #   *                   Функция показывающая сообщения процесса нагревания              *
    #   *    INPUT:                                                                         *
    #   *            timer               - Время с включения чайника.                       *
    #   *            temp                - Температура воды в чайнике.                      *
    #   *            btow                - Время кипения.                                   *
    #   *************************************************************************************
    def txt_the_heating_process(self, timer, temp, btow):
        if self.temperature_controller:
            print(f'В процессе... {timer + 1}с/{btow}c           температура: {temp}*С')
        else:
            print(f'В процессе... {timer + 1}с/{btow}c           температура: ---*С')

    #   *************************************************************************************
    #   *                   Функция состояния температуры воды                              *
    #   *    INPUT:                                                                         *
    #   *            temperature                - Температура воды в чайнике.               *
    #   *************************************************************************************
    def txt_user_shutdown(self, temperature):
        print(f'Температура чайника на данный момент составляет: {temperature}*С')
        logging.info(f'Температура чайника на данный момент составляет: {temperature}*С')

    #   *************************************************************************************
    #   *                   Создание функции для закипания воды в чайнике                   *
    #   *    INPUT:                                                                         *
    #   *            boiling_time_of_water      - Время кипения.                            *
    #   *            temperature                - Температура воды в чайнике.               *
    #   *************************************************************************************
    def teapot_on(self, boiling_time_of_water, temperature):

        self.the_kettle_boiled = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник не вскипел'

        while True:
            btow = math.ceil(boiling_time_of_water)

            for i in range(btow):

                if keyboard.is_pressed('p'):  # Остановить цикл
                    print('Чайник выключен пользователем')
                    logging.info('Чайник выключен пользователем')
                    self.the_kettle_is_off = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник выключен пользователем'
                    # Функция состояния температуры воды
                    self.txt_user_shutdown(temperature)
                    break

                # расчет шага повышения температуры от времени кипения
                step = (self.max_temperature - self.temperature) / btow
                temperature += math.ceil(step)
                if temperature >= 100:
                    temperature = 100

                sleep(1)

                # Функция показывающая сообщения процесса нагревания
                self.txt_the_heating_process(i, temperature, btow)

                if temperature >= self.max_temperature:
                    print('Чайник вскипел')
                    print('Чайник выключен')
                    logging.info('Чайник вскипел')
                    logging.info('Чайник выключен')
                    self.the_kettle_boiled = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник вскипел'
                    self.the_kettle_is_off = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник выключен'
                    break

                if i + 1 == btow:
                    print('Чайник выключен')
                    logging.info('Чайник выключен')
                    self.the_kettle_is_off = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Чайник выключен'
                    # Функция состояния температуры воды
                    self.txt_user_shutdown(temperature)
                    break
            # Добавление записи
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(f'INSERT INTO Teapot VALUES ('
                           f'"{self.name}",'
                           f'"{self.volume}",'
                           f'"{self.temperature}",'
                           f'"{self.max_temperature}",'
                           f'"{self.protection}",'
                           f'"{self.temperature_controller}",'
                           f'"{self.supply_voltage}",'
                           f'"{self.power}",'
                           f'"{self.user_response}",'
                           f'"{self.the_kettle_is_on}",'
                           f'"{self.the_kettle_is_off}",'
                           f'"{self.the_kettle_boiled}")'
                           )
            db.commit()
            break


########################################################################################################################
SadCat = Teapot()
########################################################################################################################
