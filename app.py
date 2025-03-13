import chromedriver_binary  # Adds chromedriver binary to path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement

import os
import json
import time
from datetime import datetime

USER_JSON_PATH = 'users.json'
OUTPUT_CSV_PATH = './output.csv'
OUTPUT_NOTSORTED_CSV_PATH = './output/notsorted.csv'
OUTPUT_SHINJUKU_CSV_PATH = './output/shinjuku.csv'
OUTPUT_TOKYO_CSV_PATH = './output/tokyo.csv'
OUTPUT_SUGINAMI_CSV_PATH = './output/suginami.csv'

url_shinjuku = "https://www.shinjuku.eprs.jp/regasu/web/"
url_tokyo = "https://kouen.sports.metro.tokyo.lg.jp/web/"
url_suginami = "https://www.shisetsuyoyaku.city.suginami.tokyo.jp/user/Home"
        
def read_users_json():
    with open(USER_JSON_PATH, mode='r', encoding='utf-8') as f:
        js = json.load(f)
        shinjuku = js["shinjuku"]
        tokyo = js["tokyo"]
        suginami = js["suginami"]
        return shinjuku, tokyo, suginami

def write_csv(lines):
    with open(OUTPUT_CSV_PATH, mode='w', encoding='cp932') as f:
        f.write('\n')
        for line in sorted(lines):
            f.write(line + '\n')
    
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(OUTPUT_NOTSORTED_CSV_PATH), exist_ok=True)
    with open(OUTPUT_NOTSORTED_CSV_PATH, mode='w', encoding='cp932') as f:
        for line in lines:
            f.write(line + '\n')

def write_park_csv(path: str, lines: list[str]):
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode='w', encoding='cp932') as f:
        f.write(f'{datetime.now}\n')
        for line in lines:
            f.write(line + '\n')
            
def custom_text_time_shinjuku(year: str, day: str, time_slot: str, park: str) -> tuple[str, str, str]:
    # year = '利用日：2月18日(火曜)\n2025年'
    # day = '2月18日(火曜)'
    # time_slot = '時間：11時00分～\n13時00分'
    day_ary: list[str] = day.split('(')
    day_datetime: datetime = datetime.strptime(day_ary[0], '%m月%d日')
    day_week: str = day_ary[1][0]
    
    
    year = year.replace('利用日：', '').replace('\n', '')
    day = day.replace('月', '/').replace('日', '').replace('曜', '')
    time_slots: list[str] = [t.replace('時', ':').replace('分', '') for t in time_slot.replace('時間：', '').split('～\n')] 
    # year = '2月18日(火曜)2025年'
    # day = '2/18(火)'
    # time_slots = ['11:00', '13:00']

    date_text: str = f'{day_datetime.month:0>2}/{day_datetime.day:0>2}({day_week})'
    time_slot_text: str = '-'.join(time_slots)
    
    park = park.split('公園')[0]
    park = f'{park}公園'
    
    
    # 02/15(土)	11:00-13:00
    return date_text, time_slot_text, park
    
    # dats = ['5/25(木)', '6:00～', '8:00']
    starthour = time_slot.replace('～', '').split(':')
    endhour = time_slot.split(':')
    
    dates = dats[0].split('(')
    mouth = dates[0].split('/')[0]
    day = dates[0].split('/')[1]
    week = dates[1].replace(')', '')
    
    txtday = f'{mouth:0>2}/{day:0>2}({week})'
    txthour = f'{starthour[0]:0>2}:{starthour[1]:0>2}-{endhour[0]:0>2}:{endhour[1]:0>2}'
    
    return txtday, txthour

def custom_text_time_tokyo(dats):
    # dats = ['2023年5月21日 日曜日', '17時', '19時']
    # dats = ['4月23日(火曜)2024年', '19時00分～21時00分']
    dats0 = dats[0].split('曜')[0] # 4月23日(火
    date_week = dats0.split('日(') # [4月23, 火]
    
    date_tmp = date_week[0].split('月') # [4, 23]
    month = date_tmp[0]
    day = date_tmp[1]
    week = date_week[1]
    
    start_end = dats[1].split('～') # [19時00分, 21時00分]
    starthour = start_end[0].split('時')[0]
    endhour = start_end[1].split('時')[0]
    
    txtday = f'{month:0>2}/{day:0>2}({week})'
    txthour = f'{starthour:0>2}:00-{endhour:0>2}:00'
    
    return txtday, txthour

def custom_text_time_suginami(dats: list[str]) -> str:
    # dats = [2025/3/16 (日),19:00 ～ 21:00,松ノ木運動場 人工芝庭球場５番,TG]
    dates_tmp = dats[0].split('/')
    date_week = dates_tmp[2].split(' ')
    
    month = dates_tmp[1] # 3
    day = date_week[0] # 16
    week = date_week[1] # (日)
    
    time_tmp = dats[1].replace(' ', '').split('～')
    starthours = time_tmp[0].split(':') # 19:00
    endhours = time_tmp[1].split(':') # 21:0

    txtday = f'{month:0>2}/{day:0>2}{week}'
    txthour = f'{starthours[0]:0>2}:{starthours[1]:0>2}-{endhours[0]:0>2}:{endhours[1]:0>2}'
    
    park_dats = dats[2].split(' ')
    park = park_dats[0].replace('運動場', '')
    num = park_dats[1].split('庭球場')[1].replace('番', '')
    txtpark = f'{park}{num}'

    return f'{txtday},{txthour},{txtpark},{dats[3]}'

def shinjuku_person(driver: webdriver.Chrome, user: dict[str, str]) -> list[str]:
    # login画面へ遷移
    tool_btn: WebElement = driver.find_element(By.ID, 'btn-login')
    tool_btn.click()
    
    # login
    time.sleep(2)
    id_input: WebElement = driver.find_element(By.ID, "userId")
    id_input.send_keys(user["id"])
    pass_input: WebElement = driver.find_element(By.ID, "password")
    pass_input.send_keys(user["pw"])
    btn_login = driver.find_element(By.ID, "btn-go")
    btn_login.click()
    time.sleep(1)
    result = []
    
    # 予約一覧
    driver.find_element(By.CSS_SELECTOR, "#nav-menu > nav > div:nth-child(2) > a").click()
    driver.find_element(By.CSS_SELECTOR, "#nav-menu > nav > div:nth-child(2) > div > a:nth-child(2)").click()
    
    try:
        time.sleep(2)
        rsvlist = driver.find_element(By.ID, "rsvlist")
        if '該当する予約はありません' in rsvlist.text:
            print('該当する予約はありません')
            return result
        
        table: WebElement = driver.find_element(By.ID, "rsvacceptlist")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr:not(tr tr)") # tbodyの直下のtrのみ取得
        for row in rows:
            day = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > span:nth-child(2)").text
            year = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            time_slot = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
            park = row.find_element(By.CSS_SELECTOR, "td:nth-child(4) > span:nth-child(2)").text

            daytxt, hourtxt, park = custom_text_time_shinjuku(year, day, time_slot, park)
            txt = f'{daytxt},{hourtxt},{park},{user["name"]}'
            result.append(txt)
            print(txt)
    except Exception as e:
        print(e)
    finally:
        # logout
        driver.find_element(By.ID, "btn-logout").click()
    
    return result
    
def shinjuku(driver: webdriver.Chrome, users: list[dict]) -> list[str]:
    lines: list[str] = []

    for user in users:
        print(user["name"])
        books = shinjuku_person(driver, user)
        lines.extend(books)
        
    return lines

def tokyo_person(driver: webdriver.Chrome, user) -> list[str]:
    login = driver.find_element(By.ID, 'btn-login')
    login.click()
    
    time.sleep(2)
    id_input = driver.find_element(By.ID, "userId")
    id_input.send_keys(user["id"])
    time.sleep(1)
    pass_input = driver.find_element(By.ID, "password")
    pass_input.send_keys(user["pw"])
    time.sleep(1)
    pass_input.send_keys(Keys.ENTER)
    time.sleep(2)
    
    # 一覧へ
    driver.find_element(By.CSS_SELECTOR, "#nav-menu > nav > div:nth-child(2) > a").click()
    a2s = driver.find_elements(By.CSS_SELECTOR, "#modal-reservation-menus > div > div > div > table > tbody > tr:nth-child(2) > td > a")
    time.sleep(2)
    a2s[0].click()
    time.sleep(2)

    result: list[str] = []
    
    rows: list[WebElement] = driver.find_elements(By.CSS_SELECTOR, '#rsvacceptlist > tbody > tr')
    for row in rows:
        tds: list[WebElement] = row.find_elements(By.CSS_SELECTOR, 'td')
        strDate: str = tds[1].find_element(By.CSS_SELECTOR, 'span:nth-child(2)').text.replace('\n', '')
        strTime: str = tds[2].text.replace('\n', '')
        # strDate: str = tds[1].find_element(By.CSS_SELECTOR, 'span:nth-child(2)').text.replace('曜', '')
        # strTime: str = tds[2].text.replace('\n', '').replace('～', '-').replace('時', ':').replace('分', '')
        strPark: str = tds[3].find_element(By.CSS_SELECTOR, 'span:nth-child(2)').text
        daytxt, hourtxt = custom_text_time_tokyo([strDate, strTime])
        txt = f'{daytxt},{hourtxt},{strPark},{user["name"]}'
        result.append(txt)
        print(txt)

    # logout
    driver.find_element(By.ID, "userName").click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#userMenu > div > a:nth-child(9)").click()
    return result

def tokyo(driver, users):
    lines = []
    
    for user in users:
        print(user["name"])
        books = tokyo_person(driver, user)
        lines.extend(books)

    return lines

def suginami_person(driver: webdriver.Chrome, user) -> list[str]:
    loginbtn = driver.find_element(By.CSS_SELECTOR, '#app > div:nth-child(1) > form > header > div > div.d-flex.justify-content-between > div > p > button')
    loginbtn.click()
    
    time.sleep(1)

    id_input = driver.find_element(By.ID, "UserLoginInputModel_Id")
    id_input.send_keys(user["id"])

    pass_input = driver.find_element(By.ID, "password")
    pass_input.send_keys(user["pw"])
    
    login = driver.find_element(By.CSS_SELECTOR, "#app > form > div.fixed-bottom > ul > li.item.next > button")
    login.click()
    print('login done')

    time.sleep(2)
    
    tobook = driver.find_element(By.ID, "10")
    tobook.click()
    time.sleep(3)
    
    booktable = driver.find_element(By.CSS_SELECTOR, "#app > form > div.application-main > div > div:nth-child(2) > div > div.page-body.p-3 > div")
    details = booktable.find_elements(By.CLASS_NAME, "detail")
    
    result = []
    for detail in details:
        card = detail.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div > div:nth-child(2) > div.w-100 > div > div:nth-child(1)")
        items = card.find_elements(By.CLASS_NAME, "detail-items")

        park = items[0].find_element(By.CSS_SELECTOR, "dl > dd > span:nth-child(2)").text
        
        dates = items[1].find_elements(By.CSS_SELECTOR, "dl > dd")
        date = dates[0].text
        timetxt = dates[1].text    
                
        txt = custom_text_time_suginami([date, timetxt, park, user["name"]])
        print(txt)
        result.append(txt)
        
    # logout
    logout = driver.find_element(By.CSS_SELECTOR, "#app > div:nth-child(1) > form > header > div > div > div > ul > li.logout > button")
    driver.execute_script("arguments[0].click();", logout)
    print('logout')
    time.sleep(1)
    
    return result

def suginami(driver, users):
    lines = []
    
    for user in users:
        if 'ignore' in user and user['ignore'] == 1:
            continue
        print(user["name"])
        books = suginami_person(driver, user)
        lines.extend(books)

    return lines


def main():
    print('start')

    # ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
    options: webdriver.ChromeOptions = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    # USBエラーを抑制するための追加オプション
    # options.add_argument('--disable-dev-usb-keyboard')
    options.add_argument('--disable-extensions')
    # 画像の読み込みを無効化
    # options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # ログの抑制
    options.use_chromium = True

    # 困ったときはchromedriverをUpdate
    # pip install -U chromedriver-binary-auto
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    lines = []

    try:
        shinjuku_users, tokyo_users, suginami_users = read_users_json()
        print('loaded csv')
        
        # 新宿区
        driver.get(url_shinjuku)
        lines_shinjuku = shinjuku(driver, shinjuku_users)
        write_park_csv(OUTPUT_SHINJUKU_CSV_PATH, lines_shinjuku)
        lines.extend(lines_shinjuku)

        # 杉並区
        driver.get(url_suginami)
        lines_suginami = suginami(driver, suginami_users)
        write_park_csv(OUTPUT_SUGINAMI_CSV_PATH, lines_suginami)
        lines.extend(lines_suginami)
        
        # 東京都
        driver.get(url_tokyo)
        time.sleep(2)
        lines_tokyo = tokyo(driver, tokyo_users)
        write_park_csv(OUTPUT_TOKYO_CSV_PATH, lines_tokyo)
        lines.extend(lines_tokyo)

    except Exception as e:
        print(e)
    finally:
        write_csv(lines)
        driver.quit()


if __name__ == "__main__":
    main()
    print("fin")
