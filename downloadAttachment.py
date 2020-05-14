"""
download
"""
from requests import session
from os import mkdir
from os.path import exists

s = session()


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


if __name__ == '__main__':
    # downloadAttachment()
    pass
