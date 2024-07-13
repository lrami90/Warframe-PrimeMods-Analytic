import sys
from enum import Enum
from array import *

import aiohttp
import asyncio

from AsyncioPySide6 import AsyncioPySide6
from PySide6 import QtCore as qrc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg

from ui_mainwindow import Ui_Form
from qt_material import apply_stylesheet

class ModsList(Enum):
    primed_pressure_point = "Болевая точка Прайм"
    primed_continuity = "Непрерывность Прайм"
    primed_flow = "Поток Прайм"
    primed_cryo_rounds = "Крио Патроны Прайм"
    primed_firestorm = "Огненный Шторм Прайм"
    primed_point_blank = "В Упор Прайм"
    primed_charged_shell= "Заряженные Снаряды Прайм"
    primed_animal_instinct = "Животный Инстинкт Прайм"
    primed_reach = "Размах Прайм"
    primed_fever_strike = "Лихорадочный Удар Прайм"
    primed_pistol_gambit = "Пистолетный Гамбит Прайм"
    primed_convulsion = "Конвульсия Прайм"
    primed_fulmination = "Инициирование Прайм"
    primed_target_cracker = "Дробитель Прайм"
    primed_heated_charge = "Горячий Заряд Прайм"
    primed_chilling_grasp = "Ледяное Прикосновение Прайм"
    primed_ravage = "Опустошение Прайм"

sortingArray = []

async def getPrimeModPrice(modName):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.warframe.market/v1/items/%s/orders' % modName) as response:
            jsonRequest = await response.json()
            jsonRequest = jsonRequest["payload"]["orders"]
            jsonRequest.sort(key=lambda entry: entry['platinum'])

            mediumPrice = 0
            profitPrice = 0
            orderIndex = 1
            goodOrders = 0

            while goodOrders < 3:
                if jsonRequest[orderIndex]["user"]["status"] == "ingame" and jsonRequest[orderIndex]["order_type"] == "sell":
                    mediumPrice += jsonRequest[orderIndex]["platinum"]
                    goodOrders = goodOrders + 1
                    orderIndex += 1
                else:
                    orderIndex += 1

            orderIndex = 1
            goodOrders = 0

            while goodOrders < 3:
                if jsonRequest[orderIndex]["user"]["status"] == "ingame" and jsonRequest[orderIndex]["order_type"] == "sell" and jsonRequest[orderIndex]["mod_rank"] == 10:
                    profitPrice += jsonRequest[orderIndex]["platinum"]
                    goodOrders = goodOrders + 1
                    orderIndex += 1
                else:
                    orderIndex += 1

            return round(mediumPrice / 3), round(profitPrice / 3)

def takeProfitElement(elem):
    return elem[3]

class MainWindow (qtw.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.commandLinkButton.clicked.connect(self.processGetPrice)
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 200)

        self.tableWidget.setRowCount(len(ModsList))

    def processGetPrice(self):
        sortingArray = []
        async def asyncTask():
            rowValue = 0
            self.tableWidget.setRowCount(len(ModsList))
            for value in ModsList:
                normalPrice, highPrice = await getPrimeModPrice(value.name)
                sortingArray.insert(rowValue, [value.value, normalPrice, highPrice, highPrice - normalPrice])
                rowValue += 1
                self.commandLinkButton.setText(f'Обновить ({rowValue}/{len(ModsList)})')
               

            rowValue = 0    
            sortingArray.sort(key=takeProfitElement, reverse=True)
            self.commandLinkButton.setText('Обновить')
            for data in sortingArray:
              self.tableWidget.setItem(rowValue, 0, qtw.QTableWidgetItem(data[0]))
              self.tableWidget.setItem(rowValue, 1, qtw.QTableWidgetItem(str(data[1])))
              self.tableWidget.setItem(rowValue, 2, qtw.QTableWidgetItem(str(data[2])))
              self.tableWidget.setItem(rowValue, 3, qtw.QTableWidgetItem(str(data[3])))
              rowValue += 1
        AsyncioPySide6.runTask(asyncTask())

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    with AsyncioPySide6.use_asyncio():
        window = MainWindow()
        window.show()
        apply_stylesheet(app, theme='dark_blue.xml')
        app.exec()