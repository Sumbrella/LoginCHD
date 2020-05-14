"""

"""
from os import mkdir, makedirs
from os.path import exists
from time import sleep
# import re
import json
from requests import session
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


chd_url = ""
user_name = ""
password = ""
driver: webdriver.Chrome
notice_number = 0
notice_titles = []
attachments = {}
chrome_opt = Options()
s = session()


def init():
    global chd_url, user_name, password
    with open("config.json", 'r') as config_fp:
        config_data = json.load(config_fp)
    chd_url = config_data['chd_url']
    user_name = config_data['username']
    password = config_data['password']
    if config_data['Headless'] == 'True':
        chrome_opt.add_argument('--headless')
    # if config_data['Disable_infobars'] == 'True':
        # chrome_opt.add_argument('--disable-infobars')


def startDriver():
    global driver
    driver = webdriver.Chrome('../chromedriver.exe', options=chrome_opt)
    print('Connecting...')
    driver.get(chd_url)
    print('connect succeed!')

    return driver


def login():
    print('logging in...')
    var = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(user_name)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'password'))
    ).send_keys(password)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="casLoginForm"]/p[5]/button'))
    ).click()
    print('login success!')


def visitNoticesPage():
    print('visiting notices page...')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/table/tbody/tr/td/table/tbody/tr[1]/td['
                                                  '2]/div[2]/div/div[2]/div[2]/a'))
    ).click()
    driver.switch_to.window(driver.window_handles[1])
    print('changed to news page!')
    sleep(2)


def changePage():
    pass


def searchNotices():
    print('searching notices...')
    news_element: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/div[2]/div[1]/ul'))
    )
    # print(news_element)
    # with open("news_source.html", 'w+', encoding='utf-8') as fp:
         # json.dump(news_element.get_attribute('innerHTML'), fp, indent=2)
    # news_pages 储存 每一个小的 page 页面
    notices = news_element.find_elements_by_class_name('rss-title')
    for notice in notices:
        title = notice.text if notice.text else '???'
        print('Now in page: ***' + title + '***')
        notice.click()  # 打开一个子通知
        parseNews(title)  # 分析一个子通知


def parseNews(title):
    global notice_number
    print('parsing notice...')
    driver.switch_to.window(driver.window_handles[-1])
    content = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'bulletin-contentpe65'))
    )

    try:
        attachment_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/ul'))
        )
    except Exception as e:
        print(e)
        attachment_element = None

    print('writing content...')
    # TODO: 记录内容
    if not exists('notices/{}'.format(title)):
        makedirs('notices/{}'.format(title))
    with open('notices/{}/'.format(title) + title + '.txt', 'w+', encoding='utf-8') as fp:
        fp.write(content.text)
    print('writing succeed!')
    notice_number += 1
    notice_titles.append(title)
    # TODO: 记录附件
    if attachment_element:
        atm_s = attachment_element.find_elements_by_tag_name('li')
        # 第一个 li 元素舍弃
        for atm in atm_s[1:]:
            attachment_name = atm.text
            attachment_url = getAttachmentUrl(atm.get_attribute('innerHTML'))
            attachments.update(
                {
                    title: {
                        'name': attachment_name,
                        'url': attachment_url
                    }
                }
            )

    # 关闭页面
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])


def getAttachmentUrl(source: str) -> str:
    soup = BeautifulSoup(source, 'lxml')
    res = soup.find('a')['href']

    return chd_url + '/' + res


def downloadAttachments():
    cookies = driver.get_cookies()
    jse_cookie = ''
    rou_cookie = ''
    ipl_cookie = ''
    mod_cookie = ''
    for cookie in cookies:
        if cookie['name'] == 'JSESSIONID':
            jse_cookie = cookie['value']
        if cookie['name'] == 'route':
            rou_cookie = cookie['value']
        if cookie['name'] == 'iPlanetDirectoryPro':
            ipl_cookie = cookie['value']
        if cookie['name'] == 'MOD_AUTH_CAS':
            mod_cookie = cookie['value']
    with open('attachment_urls.json', 'r+', encoding='utf-8') as fp:
        url_data = json.load(fp)
    for title, info in url_data.items():
        # 下面的这个函数封装在 downloadAttachment.py 模块中
        downloadAttachment(title, info['name'], info['url'], ipl_cookie, mod_cookie, rou_cookie, jse_cookie)


def downloadAttachment(title, att_name, url, ipl_cookie, mod_cookie, rou_cookie, jse_cookie):

    headers = {
        'Host': 'portal.chd.edu.cn',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 'iPlanetDirectoryPro={}; '
                  'MOD_AUTH_CAS={}; '
                  'route={}; '
                  'JSESSIONID={}'.format(ipl_cookie, mod_cookie, rou_cookie, jse_cookie)
    }
    # print(headers)
    print('getting attachment...')
    response = s.get(url=url, headers=headers)
    print('got attachment!')
    if not exists('notices/{}/attachments'.format(title)):
        mkdir('notices/{}/attachments'.format(title))

    print('saving attachment: %s ...' % att_name)

    with open('notices/{}/attachments/{}'.format(title, att_name), 'wb') as fp:
        fp.write(response.content)
    print('saved!')


def main():
    init()
    try:
        startDriver()
        login()
        visitNoticesPage()
        searchNotices()
        downloadAttachments()

    except Exception as e:
        raise
    finally:
        print('quiting...')
        # print('====== the notices list ======')
        # for title in notice_titles:
        #     print(title)
        #     sleep(0.1)
        driver.quit()
        with open("attachment_urls.json", "w+", encoding='utf-8') as fp:
            json.dump(attachments, fp, indent=1, ensure_ascii=False)
        print('total saved notices number: {}'.format(notice_number))
        print('quit succeed!')


if __name__ == '__main__':
    main()
