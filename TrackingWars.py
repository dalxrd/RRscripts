# Слежение за изменениями в войнах/восстаниях/бунтах госки

import json
import time

from lxml import html
import requests
import re

# -------------------------ЛИНКИ------------------------------
timer = 120
id_state = "4228"
main_url = "https://rivalregions.com/"
# ------------------------------------------------------------

# ------------------------АВТОРИЗАЦИЯ------------------------------------------
session = requests.session()
with open('cookies.json', 'r') as f:
    cookies_list = json.load(f)
# Создание словаря cookies
cookies = {}
for cookie in cookies_list:
    cookies[cookie['name']] = cookie['value']
response_login = session.get(main_url, cookies=cookies)
print(f"------- Авторизация: {response_login.status_code}-------")
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
if response_login.status_code != 200:
    print("Ошибка")
else:
    response_list_of_wars = session.get(f"{main_url}/listed/statewars/{id_state}", cookies=cookies)
    tree_wars = html.fromstring(response_list_of_wars.text)

    try:
        table = tree_wars.xpath("//table[@id='table_list']")[0]
    except Exception as e:
        print('Войн нет.')
    else:
        tbody = table.xpath("./tbody")[0]
        # строчки = войны
        trs = tbody.xpath("./tr")

        # список словарей войн
        wars = []
        # пройтись по строчкам
        for tr in trs:
            # колонки
            tds = tr.xpath("./td")

            # левая сторона
            try:
                # если война
                left_side = tds[1].xpath("./div")[0].get("title").replace("\t", "").replace("\n", "")
            except:
                # если восстанка/бунт
                left_side = tds[1].xpath("./div")[0].text.replace("\t", "").replace("\n", "").replace("\r", "")

            # правая сторона
            right_side = tds[3].xpath("./div")[0].get("title").replace("\t", "").replace("\n", "")

            # значение буфа
            damage = tds[4].text

            # сохранить в словарь
            d = {
                "left": left_side,
                "right": right_side,
                "damage": tds[4].text
            }
            # добавить в список
            wars.append(d)
            print(f"{d['damage']} | {d['left']} - {d['right']}")

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    while True:
        time.sleep(timer)
        response_list_of_wars = session.get(f"{main_url}/listed/statewars/{id_state}", cookies=cookies)
        tree_wars = html.fromstring(response_list_of_wars.text)

        try:
            table = tree_wars.xpath("//table[@id='table_list']")[0]
        except:
            print('Войн нет.')
        else:
            tbody = table.xpath("./tbody")[0]
            # строчки = войны
            trs = tbody.xpath("./tr")

            for index, tr in enumerate(trs):
                # колонки
                tds = tr.xpath("./td")

                # левая сторона
                try:
                    # если война
                    left_side = tds[1].xpath("./div")[0].get("title").replace("\t", "").replace("\n", "")
                except:
                    # если восстанка/бунт
                    left_side = tds[1].xpath("./div")[0].text.replace("\t", "").replace("\n", "").replace("\r", "")

                # правая сторона
                right_side = tds[3].xpath("./div")[0].get("title").replace("\t", "").replace("\n", "")

                # значение буфа
                damage = tds[4].text

                # сохранить в словарь
                d = {
                    "left": left_side,
                    "right": right_side,
                    "damage": damage
                }

                # посчитать разницу
                difference = int(damage.replace(".", "")) - int(wars[index]["damage"].replace(".", ""))
                difference = format(difference, ',').replace(',', '.')
                difference = f"+{difference}" if difference[0] != "-" else difference

                # заменить элементы
                wars[index] = d

                print(f"({difference}) {d['damage']} | {d['left']} - {d['right']}")

            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# -----------------------------------------------------------------------------




