# Radar

import json
import time

import requests
import re

from lxml import html
from datetime import datetime

# -------------------------ЛИНКИ------------------------------
timer = 10  # каждые __ секунд (для 2 минут указывать 120 и т.д.)
id_state = "2976"  # id госки
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
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
if response_login.status_code != 200:
    print("Ошибка", response_login.status_code)
else:
    print("~~~~~~~~ RADAR: [loading] ~~~~~~~~")

    response_info_regions = session.get(f"{main_url}info/regions/{id_state}", cookies=cookies)
    html_code = response_info_regions.text
    tree_info_regions = html.fromstring(html_code)

    # считать всю страницу Info (получить название, id, кол-во )
    print("~ Собираем данные Регионы: ", end='')
    trs = tree_info_regions.xpath('//tr')  # все строчки таблицы
    trs.pop(0)  # удалить заголовки

    # проход по строчкам таблицы ----------------------------------------
    regions_info_old = []
    for tr in trs:
        # все колонки строчки
        tds = tr.xpath('./td')

        # id региона
        link = tds[0].xpath('./a')[0].get('href')
        match = re.search(r'/(\d+)$', link)
        region_id = match.group(1)

        # название региона
        a_text = tds[0].xpath('./a')[0].text
        words = re.findall(r'[^\W\d_]+', a_text)  # список из слов
        words.pop(-1)
        region_name = " ".join(words)
        # print(region_name)

        # аккаунтов внутри
        population = int(tds[2].text)

        # добавить словари в список
        dictionary = {
            "id": region_id,
            "name": region_name,
            "pop": population,
            "accs": []
        }
        regions_info_old.append(dictionary)

        print("#", end="")
    print("")

    # пройтись по всем регионам и сохранить список аккаунтов -------------
    print("~ Собираем данные Население: ", end='')
    for region in regions_info_old:
        # страница региона
        response_region = session.get(f"{main_url}listed/region/{region['id']}", cookies=cookies)
        tree_region = html.fromstring(response_region.text)

        # собрать все строчки
        table = tree_region.xpath("//table[@id='table_list']")
        tbody = table[0].xpath("./tbody")
        trs = tbody[0].xpath("./tr")  # все строчки

        # пройтись по всем строчкам
        for tr in trs:
            # все колонки
            tds = tr.xpath("./td")

            # link
            link = tds[1].get("action")
            acc_link = main_url + "#" + link
            # print(acc_link)

            # ник
            acc_nickname = tds[1].text.replace('\t', '')
            # .replace('\xe1', '').replace('\u265a', '')
            # лвл
            acc_lvl = tds[3].text

            # собрать словарь
            account = {
                "nick": acc_nickname,
                "lvl": acc_lvl,
                "link": acc_link
            }
            # прицепить его к региону
            region["accs"].append(account)
        print("#", end="")
    print("")

    # # сохранить все в json файл -------------------------------------
    # print("~ Сохраняем в БД: ", end='')
    # with open('db_radar.json', 'w') as f:
    #     json.dump(regions_info_old, f, ensure_ascii=True, indent=4)
    # print("[DONE]")

    # # для проверки
    # with open('db_radar.json', 'r') as f:
    #     data = json.load(f)
    #
    # for region in data:
    #     print(region['name'])

    print("~~~~~~~~ RADAR: [ON] ~~~~~~~~")

    while True:
        time.sleep(timer)

        # повторный проход по Info, сверка населения в регах
        # зайти на Info
        response_info_regions = session.get(f"{main_url}info/regions/{id_state}", cookies=cookies)
        tree_info_regions = html.fromstring(response_info_regions.text)

        # считать всю страницу Info (получить название, id, кол-во )
        trs = tree_info_regions.xpath('//tr')  # все строчки таблицы
        trs.pop(0)  # удалить заголовки

        # проход по строчкам таблицы ----------------------------------------
        regions_info_new = []
        for tr in trs:
            # все колонки строчки
            tds = tr.xpath('./td')

            # id региона
            link = tds[0].xpath('./a')[0].get('href')
            match = re.search(r'/(\d+)$', link)
            region_id = match.group(1)

            # название региона
            a_text = tds[0].xpath('./a')[0].text
            words = re.findall(r'[^\W\d_]+', a_text)  # список из слов
            words.pop(-1)
            region_name = " ".join(words)
            # print(region_name)

            # аккаунтов внутри
            population = int(tds[2].text)

            # добавить словари в список
            dictionary = {
                "id": region_id,
                "name": region_name,
                "pop": population,
                "accs": []
            }
            regions_info_new.append(dictionary)

        # вывод времени
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        print(f"[{current_time}]")

        detected = 0
        # найти разницу в старом и новом списке
        for region_old in regions_info_old:
            for region_new in regions_info_new:
                if region_old["name"] == region_new["name"]:
                    if region_old["pop"] != region_new["pop"]:
                        detected += 1
                        # страница региона
                        response_region_new = session.get(f"{main_url}listed/region/{region_new['id']}", cookies=cookies)
                        tree_region_new = html.fromstring(response_region_new.text)

                        # получить новый список акков
                        # собрать все строчки
                        table = tree_region_new.xpath("//table[@id='table_list']")
                        tbody = table[0].xpath("./tbody")
                        trs = tbody[0].xpath("./tr")  # все строчки

                        # пройтись по всем строчкам
                        for tr in trs:
                            # все колонки
                            tds = tr.xpath("./td")

                            # link
                            link = tds[1].get("action")
                            acc_link = main_url + "#" + link
                            # print(acc_link)

                            # ник
                            acc_nickname = tds[1].text.replace('\t', '')
                            # .replace('\xe1', '').replace('\u265a', '')
                            # лвл
                            acc_lvl = tds[3].text

                            # собрать словарь
                            account = {
                                "nick": acc_nickname,
                                "lvl": acc_lvl,
                                "link": acc_link
                            }
                            # прицепить его к региону
                            region_new["accs"].append(account)
                        # я получил новый список акков, актуальный

                        # найти разницу, какие акки
                        for acc_old in region_old["accs"]:
                            if acc_old not in region_new["accs"]:
                                print(f"Вылет из {region_old['name']}: никнейм - {acc_old['nick']}")
                        for acc_new in region_new["accs"]:
                            if acc_new not in region_old["accs"]:
                                print(f"Прилет в {region_new['name']}: никнейм - {acc_new['nick']}")

                        break

                    else:
                        region_new["accs"] = region_old["accs"]

        if detected == 0:
            print("~ чисто ~")
        else:
            # переписать старый список акков, и вписать туда новый
            regions_info_old = regions_info_new

# -----------------------------------------------------------------------------




