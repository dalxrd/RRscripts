# Плата за Департаменты (золото)
import json
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------ЛИНКИ------------------------------
print("------- НАСТРОЙКИ -------")
reward = str(input("Денежное вознаграждение (10 = 10kkk): ")) + "000000000"
print("----- золото -----")
g_all = int(input("Какое значение депов сейчас: "))
g_lim = int(input("Лимит: "))
is_limits = bool(int(input("Настроить остальные лимиты? (1 - да, 0 - нет): ")))
if is_limits is True:
    print("----- стройки -----")
    b_all = int(input("Какое значение депов сейчас: "))
    b_lim = int(input("Лимит: "))
    print("----- нефть -----")
    o_all = int(input("Какое значение депов сейчас: "))
    o_lim = int(input("Лимит: "))
    print("----- алмазы -----")
    d_all = int(input("Какое значение депов сейчас: "))
    d_lim = int(input("Лимит: "))
else:
    b_all = 0
    b_lim = 0
    o_all = 0
    o_lim = 0
    d_all = 0
    d_lim = 0
g_url = "https://rivalregions.com/#listed/professors/2/2976"  # депы золота
b_url = "https://rivalregions.com/#listed/professors/1/2976"  # депы строек
o_url = "https://rivalregions.com/#listed/professors/3/2976"  # депы нефти
d_url = "https://rivalregions.com/#listed/professors/5/2976"  # депы алмазов
# ------------------------------------------------------------

# объявить браузер
print("-|- START -|-")
browser = webdriver.Chrome()

# ------------------------ АВТОРИЗАЦИЯ ---------------------------
browser.get("https://rivalregions.com/")

with open('cookies.json', 'r') as f:
    cookies_json = json.load(f)

cookies = []
for cookie in cookies_json:
    cookies.append({
        'name': cookie['name'],
        'value': cookie['value'],
        'domain': cookie['domain'],
        'path': cookie['path'],
        'expiry': cookie['expirationDate'],
        'secure': cookie['secure'],
        'httpOnly': cookie['httpOnly']
    })

for cookie in cookies:
    browser.add_cookie(cookie)
browser.refresh()

# cookies = browser.get_cookies()
# with open('cookies.txt', 'w') as f:
#     for cookie in cookies:
#         f.write(f"{cookie['name']}={cookie['value']}\n")

try:
    email_input = browser.find_element(By.NAME, 'mail')
    password_input = browser.find_element(By.NAME, 'p')
    submit_button = browser.find_element(By.NAME, 's')
    email_input.send_keys('-')
    password_input.send_keys('-')
    submit_button.submit()
except Exception as e:
    print('Не удалось залогиниться. Ошибка:', e)
# ------------------------------------------------------------------


# получить список акков
def get_accounts(url, r_all, r_lim, resource, is_limit):
    browser.get(url)

    # раскрыть полный список
    wait = WebDriverWait(browser, 10)
    more_button = wait.until(EC.presence_of_element_located((By.ID, 'list_last')))
    # more_button = browser.find_element(By.ID, "list_last")
    for i in range(3):
        browser.execute_script("arguments[0].scrollIntoView();", more_button)
        browser.execute_script("arguments[0].click();", more_button)
        time.sleep(2)

    # получить список из линков на акк
    table_body = browser.find_element(By.ID, "table_list").find_element(By.TAG_NAME, "tbody")
    rows = table_body.find_elements(By.TAG_NAME, "tr")

    acc_list = []
    for row in rows:
        # прокручивать до каждого элемента
        browser.execute_script("arguments[0].scrollIntoView();", row)

        # все <td> элементы
        cells = row.find_elements(By.TAG_NAME, "td")
        date = cells[3].text  # дата
        nickname_deps = cells[1].text  # никнейм и в скобках депы
        deps = int(nickname_deps[-3:-1])
        if date.startswith('Сегодня'):
            # обработка лимитов
            if is_limits:
                if r_all >= r_lim:
                    r_all -= deps
            # print(nickname_deps, date)
        elif date.startswith('Вчера'):
            # обработка лимитов
            if is_limit:
                if r_all >= r_lim:
                    r_all -= deps
                    continue
            elif deps == 10:
                link_on_profile = cells[1].get_attribute("action")
                profile_id = re.search(r'\d+$', link_on_profile).group()
                nickname = nickname_deps[:-5]
                dictionary = {
                    "id": profile_id,
                    "nickname": nickname,
                    "resource": resource
                }
                acc_list.append(dictionary)
                print(f"{dictionary['id']} {dictionary['nickname']} {dictionary['resource']}")

    return acc_list


# цикл: Открыть акк -> перевести ему грн -> закрыть окно
def pay(acc_list, cash):

    spended = 0

    for account in acc_list:
        browser.get(f"https://rivalregions.com/#slide/donate/user/{account['id']}")
        time.sleep(1)

        # раскрыть поле
        wait = WebDriverWait(browser, 10)
        table = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='minwidth' and @style='position: abs"
                                                                     "olute; width: 800px; left: 50%; margin-left: -400"
                                                                     "px;']")))
        forms = table.find_elements(By.TAG_NAME, "div")
        open_form = forms[-1]
        open_form.click()

        # ввести сумму
        field = browser.find_element(By.XPATH, '//input[@type="text"]')
        field.send_keys(cash)

        # перевести сумму
        send_pay = browser.find_element(By.XPATH, '//div[@class="donate_sell_button button_green"]')
        send_pay.click()
        spended += int(cash)

        # отчет
        print(f"{account['resource']} - {account['nickname']} : {int(cash)}")

    print(f"Всего: {str(spended)[:-9]}kkk")
    return spended


spended_all = 0
gold_list = get_accounts(g_url, g_all, g_lim, "Gold", is_limits)
spended_all += pay(gold_list, reward)
gold_list = get_accounts(b_url, b_all, b_lim, "Buildings", is_limits)
spended_all += pay(gold_list, reward)
gold_list = get_accounts(o_url, o_all, o_lim, "Oil", is_limits)
spended_all += pay(gold_list, reward)
gold_list = get_accounts(d_url, d_all, d_lim, "Diamonds", is_limits)
spended_all += pay(gold_list, reward)

print('-|- FINISH -|-')
print(" ")
print(f"Всего потрачено: {str(spended_all)[:-9]}kkk")

