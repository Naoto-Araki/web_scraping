from time import sleep
from bs4 import BeautifulSoup
import requests
import pandas as pd

# requestsでurlにアクセスしてHTML解析
# 大阪府高槻市の中古マンションSUUMOサイト
url = 'https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=060&bs=011&ta=27&jspIdFlg=patternShikugun&sc=27207&kb=1&kt=9999999&mb=0&mt=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999&page={}'

d_list = []

target_url = url.format(1)
r = requests.get(target_url)
soup = BeautifulSoup(r.text)

# ページ数を取得
pages = soup.find('div', class_='pagination pagination_set-nav')
page_tags = pages.find('ol', class_='pagination-parts')
# ページ数一覧の 'li' タグの数で変更する
page_tag = page_tags.find_all('li')[10]
page_numbers = page_tag.text  # ページ番号を文字列で取得
page_numbers = int(page_numbers)  # 整数に変換
page_numbers = page_numbers + 1  # ページ番号を1増加
#print(page_numbers)

for i in range(1, page_numbers):
    print('d_listの大きさ', len(d_list))

    target_url = url.format(i)
    #print(taget_url)

    r = requests.get(target_url)
    soup = BeautifulSoup(r.text)

    # サーバーに負荷をかけないため
    sleep(1)

    # soupから情報を取得
    contents = soup.find_all('div', class_='property_unit-content')

    for content in contents:
        # 詳細リンクを取得
        link = content.find('h2', class_='property_unit-title')
        a = link.find('a')
        href = a.get('href')
        detail_link = 'https://suumo.jp' + href + 'bukkengaiyo/?fmlg=t001'

        print(detail_link)

        r_child = requests.get(detail_link)
        soup_child = BeautifulSoup(r_child.text)

        # サーバーに負荷をかけないために
        sleep(1)

        # soup_childから情報を取得
        contents_child = soup_child.find_all('div', class_='secTitleOuterR') or soup_child.find_all('div', class_='secTitleOuterK')
        content_child = contents_child[0]
        title = content_child.find('h3', class_='secTitleInnerR') or content_child.find('h3', class_='secTitleInnerK')
        tables_child = soup_child.find_all('table', class_='mt10 bdGrayT bdGrayL bgWhite pCell10 bdclps wf')
        table_child = tables_child[0]
        years = table_child.find_all('td')[13]
        table_child = tables_child[1]
        address, access, numbers, structure_floors = table_child.find_all('td')[0:4]

        # 取得した情報を辞書に格納
        d ={
            'title':title.text,
            'address':address.text,
            'access':access.text,
            'years':years.text,
            'numbers':numbers.text,
            'structure/floors':structure_floors.text
        }

        d_list.append(d)

df = pd.DataFrame(d_list)

df.to_csv('used_apartment_info_suumo.csv', index=None, encoding='utf-8-sig')