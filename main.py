"""
"""
import json
from os import mkdir, system
from os.path import exists
from time import sleep
from requests import session
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

# user_variables
chd_url = ""
# user_name = "2019900086"
# password = "wangjuanyu123"
over_page = 2
max_notice = 100
driver: webdriver.Chrome
driver_path = ""  # "chromedriver.exe"
chrome_opt = Options()

# model variables
notice_number = 0
notice_titles = []
attachments = {}
now_page = 0
s = session()


def init():
    global chd_url, driver_path
    chd_url = "http://portal.chd.edu.cn"
    driver_path = None
    chrome_opt.add_argument('--headless')
    # chrome_opt.add_argument('--disable-infobars')
    # with open("config.json", 'r') as config_fp:
    #     config_data = json.load(config_fp)
    # chd_url = config_data['chd_url']
    # user_name = config_data['username']
    # password = config_data['password']
    # if config_data['Headless'] == 'True':
    #     chrome_opt.add_argument('--headless')
    # if config_data['Disable_infobars'] == 'True':
        # chrome_opt.add_argument('--disable-infobars')


def startDriver():
    global driver
    if driver_path is None:
        driver = webdriver.Chrome(options=chrome_opt)
    else:
        driver = webdriver.Chrome(driver_path, options=chrome_opt)
    print('Connecting...')
    driver.get(chd_url)
    print('connect succeed!')

    return driver


def login():
    global user_name, password
    print('logging in...')
    user_name = input('Please enter your user_name:')
    password = input('Please enter your password:')
    WebDriverWait(driver, 10).until(
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
    # 点击 MORE 进入整个新闻界面
    driver.switch_to.window(driver.window_handles[1])
    print('changed to main notice page!')
    sleep(2)


def getNotices():
    while now_page < over_page:
        searchNotices()
        changePage(5)
    searchNotices()


def changePage(times):
    #
    # driver show in notices main page
    global now_page
    try:
        next_page_button = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/a[3]')
        next_page_button.click()
    except Exception as e:
        print("change to new page error")
        print(e)
        # try again
        changePage(times - 1)
    else:
        now_page += 1
        print('change to page {}'.format(now_page))
    sleep(2)


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
        parseNotices(title)  # 分析一个子通知


def parseNotices(title):
    # TODO:把title中的反斜杠替换
    title: str = title.replace('/', '_')
    global notice_number
    print('parsing notice...')
    driver.switch_to.window(driver.window_handles[-1])
    # TODO：获取消息和附件信息
    content = None
    attachment_element = None
    try:
        content = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'bulletin-contentpe65'))
        )
    except TimeoutException as te:
        # 如果超时，取消获取这个通知
        print('fail to get content of {}'.format(title))
        return
    try:
        attachment_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/ul'))
        )
    except TimeoutException as te:
        print('no attachment find!')
        return

    print('writing content...')
    if not exists('notices'):
        mkdir('notices')
    # TODO: 记录消息内容
    if content is not None:
        if not exists('notices/{}'.format(title)):
            mkdir('notices/{}'.format(title))
        with open('notices/{}/'.format(title) + title + '.txt', 'w+', encoding='utf-8') as fp:
            fp.write(content.text)
        print('writing succeed!')
        notice_number += 1
        notice_titles.append(title)
    # TODO: 记录附件
    if attachment_element is not None:
        atm_s = attachment_element.find_elements_by_tag_name('li')
        # 第一个 li 元素舍弃
        for atm in atm_s[1:]:
            attachment_name = atm.text
            attachment_url = getAttachmentUrl(atm.get_attribute('innerHTML'))
            if title not in attachments.keys():
                attachments.update(
                    {
                        title: {
                            'name': [attachment_name],
                            'url': [attachment_url]
                        }
                    }
                )
            else:
                attachments[title]['name'].append(attachment_name)
                attachments[title]['url'].append(attachment_url)

    # close notice page
    driver.close()
    # change to main notices page
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
    # TODO: 通过cookie 构造 header
    for cookie in cookies:
        if cookie['name'] == 'JSESSIONID':
            jse_cookie = cookie['value']
        if cookie['name'] == 'route':
            rou_cookie = cookie['value']
        if cookie['name'] == 'iPlanetDirectoryPro':
            ipl_cookie = cookie['value']
        if cookie['name'] == 'MOD_AUTH_CAS':
            mod_cookie = cookie['value']

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

    for title, info in attachments.items():
        # 下面的这个函数封装在 downloadAttachment.py 模块中
        for i in range(len(info['name'])):
            downloadAttachment(title, info['name'][i], info['url'][i], headers)


def downloadAttachment(title, att_name, url, headers):

    # print(headers)
    print('getting attachment...')

    try:
        response = s.get(url=url, headers=headers)
    except Exception as e:
        print(e)
        print('got attachment failed!')
        return
    print('got attachment!')

    if not exists('notices/{}/attachments'.format(title)):
        mkdir('notices/{}/attachments'.format(title))

    print('saving %s ...' % att_name)

    with open('notices/{}/attachments/{}'.format(title, att_name), 'wb') as fp:
        fp.write(response.content)
    print('saved!')


def main():
    init()
    try:
        startDriver()
        login()
        visitNoticesPage()
        getNotices()
        # downloadAttachments()

    except Exception as e:
        raise
    finally:
        print('quiting...')
        print('====== the notices list ======')
        with open('attachments.txt', 'w+') as fp:
            json.dump(attachments, fp, indent=2, encoding='utf-8')
        for title in notice_titles:
            print(title)
            sleep(0.1)
        driver.quit()
        print('total saved notices number: {}'.format(notice_number))
        print('quit succeed!')


if __name__ == '__main__':
    main()
    system('pause')
