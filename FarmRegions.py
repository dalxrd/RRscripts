# Список регионов госки, с отображением работающих акков в них
import json

from lxml import html
import requests
import re


# -------------------------ЛИНКИ------------------------------
id_state = "2976"
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
    pass
else:
    response_state = session.get(f"{main_url}/map/state_details/{id_state}", cookies=cookies)
    content_type = response_state.headers.get('Content-Type')
    if content_type:
        charset_pos = content_type.find('charset=')
        if charset_pos >= 0:
            response_state.encoding = content_type[charset_pos + len('charset='):].strip()
    print(f"Статус код: {response_state.status_code}")
    html_code = response_state.text
    tree_state = html.fromstring(html_code)

    # ------------ название Госки ------------
    h1_white_slide_title = tree_state.xpath('//h1[@class="white slide_title"]')[0]
    state = h1_white_slide_title.xpath('.//a')[0]
    print(f"Государство: {state.text}")

    # --------------- Pегионы  ---------------
    print("------- Регионы: -------")
    # вкладка Ресурсы
    response_resources = session.get(f"{main_url}/listed/stateresources/{id_state}", cookies=cookies)
    tree_resources = html.fromstring(response_resources.text)
    tbody_list_tbody = tree_resources.xpath("//tbody[@id='list_tbody']")[0]
    regions_all = tbody_list_tbody.xpath('./tr')

    regions = []

    for region in regions_all:  # проход по всем регам

        gold_limit = float(region.xpath("./td")[5].get('rat'))
        gold_now = float(region.xpath("./td")[2].get('rat'))
        gold = int(gold_limit + gold_now)

        if gold != 0:

            id_region = region.get('user')
            # перейти на страницу рега
            response_region = session.get(f"{main_url}/map/details/{id_region}", cookies=cookies)
            tree_region = html.fromstring(response_region.text)

            # название рега
            h1_element = tree_region.xpath('//h1[@class="white slide_title"]')[0]
            text_elements = h1_element.xpath('.//text()')
            text = ''.join(text_elements).strip()
            match = re.search(r'регіон ([^,]*(?: область)?)', text)
            if match:
                region_name = match.group(1)[:-11]
                if region_name[-1] == "и":
                    region_name = region_name[:-12]
            else:
                region_name = "Івано-Франківська область"
            # индекс медицины
            div_element = tree_region.xpath('//div[@class="short_details tc imp float_left no_pointer spd hosp_wiki"]')[0]
            span = div_element.xpath('./span')[0]
            medicine = span.text[:-3]
            # print(region_name)

            # глубокая разведка
            gr = int(region.xpath("./td")[4].get('rat'))

            # перейти на страницу фабрик рега
            response_factories = session.get(f"{main_url}factory/search/{id_region}/0/6", cookies=cookies)
            tree_factories = html.fromstring(response_factories.text)
            # лучшая фабрика
            tbody_list_tbody = tree_factories.xpath("//tbody[@id='list_tbody']")[0]
            factory_best = tbody_list_tbody.xpath('./tr')[0]
            factory_lvl = factory_best.xpath("./td")[2].text
            factory_workers = factory_best.xpath("./td")[3].text
            factory_sallary = factory_best.xpath("./td")[4].text
            # print(factory_lvl, factory_workers, factory_sallary)

            # перейти на страницу со списком онлайна в реге
            response_online = session.get(f"{main_url}/listed/online/{id_region}", cookies=cookies)
            tree_online = html.fromstring(response_online.text)
            # получить кол-во онлайна
            h1_element = tree_online.xpath('//h1[@class="white slide_title"]')[0]
            text_elements = h1_element.xpath('.//text()')
            text = ''.join(text_elements).strip()
            match = re.findall("\d+", text)
            region_online = match[0]
            # print(region_online)

            # собрать все
            dictionary = {
                "id": id_region,
                "url": main_url + "#map/details/" + id_region,
                "name": region_name,
                "online": region_online,
                "gold": gold,
                "gr": gr,
                "medicine": medicine,
                "factory lvl": factory_lvl,
                "factory workers": factory_workers,
                "factory sallary": factory_sallary,
            }
            regions.append(dictionary)

    # --- сортировки ---
    regions_by_limit = sorted(regions, key=lambda reg: reg['gold'], reverse=True)
    regions_by_online = sorted(regions, key=lambda reg: reg['online'], )
    regions_by_med = sorted(regions, key=lambda reg: reg['medicine'], reverse=True)

    # --- вывод ---
    for r in regions_by_limit:
        print(f"* {r['gold']} G ({r['gr']}) * {r['online']} online * {r['medicine']} med : {r['name']} {r['url']}")
        print(f"{r['factory lvl']} lvl {r['factory workers']} {r['factory sallary']}")
        print("")
