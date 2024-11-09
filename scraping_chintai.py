from time import sleep
from bs4 import BeautifulSoup
import requests
import pandas as pd

# requestsでurlにアクセスしてHTML解析
# 大阪市福島区のSUUMOサイト
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=060&bs=040&ta=27&sc=27207&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1&page={}'

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
print(page_numbers)

for i in range(1, page_numbers):
    print('ページサイズ', i)
    print('d_listの大きさ', len(d_list))

    target_url = url.format(i)
    #print(taget_url)

    r = requests.get(target_url)
    
    # サーバーに負荷をかけないため
    sleep(1)
    soup = BeautifulSoup(r.text)

    # soupから情報を取得
    contents = soup.find_all('div', class_='cassetteitem')

    for content in contents:
        # 物件, 部屋情報
        detail = content.find('div', class_='cassetteitem-detail')
        table = content.find('table', class_='cassetteitem_other')

        # 物件名, 住所, アクセス情報, 築年数, 階数の格納
        title = detail.find('div', class_='cassetteitem_content-title').text
        address = detail.find('li', class_='cassetteitem_detail-col1').text
        access = detail.find('li', class_='cassetteitem_detail-col2').text
        age = detail.find('li', class_='cassetteitem_detail-col3').text

        # 部屋情報を格納
        tr_tags = table.find_all('tr', class_='js-cassette_link')

        for tr_tag in tr_tags:
            floor, price, first_fee, capacity = tr_tag.find_all('td')[2:6]

            # 賃料, 管理費, 敷金, 礼金, 間取り, 面積を格納
            fee, management_fee = price.find_all('li')
            deposit, gratuity = first_fee.find_all('li')
            madori, menseki = capacity.find_all('li')

            # 詳細リンクを取得
            link = tr_tag.find_all('td')[8]

            a = link.find('a')
            href = a.get('href')
            detail_link = 'https://suumo.jp' + href
            print(detail_link)

            # 詳細リンクにアクセス
            r_child = requests.get(detail_link)

            # サーバーに負荷をかけないため
            sleep(1)
            soup_child = BeautifulSoup(r_child.text)

            # `contents_child` に要素があるかを確認
            contents_child = soup_child.find_all('div', class_='section l-space_small')
            if len(contents_child) > 1:
                content_child = contents_child[1]
                table_child = content_child.find('table', class_='data_table table_gaiyou')

                # 構造, 階数, 築年月
                structure, floors, year = table_child.find_all('td')[1:4]
                # 総戸数
                numbers = table_child.find_all('td')[14]

                # 取得した情報を辞書に格納
                d = {
                    'title': title,
                    'address': address,
                    'access': access,
                    'age': age,
                    'floor': floor.text,
                    'fee': fee.text,
                    'management_fee': management_fee.text,
                    'deposit': deposit.text,
                    'gratuity': gratuity.text,
                    'madori': madori.text,
                    'menseki': menseki.text,
                    'structure': structure.text,
                    'floors': floors.text,
                    'year': year.text,
                    'numbers': numbers.text
                }

                # 取得した辞書をリストに追加
                d_list.append(d)
            else:
                print(f"エラーリンクです: {detail_link} をスキップします")

df = pd.DataFrame(d_list)

df.to_csv('chintai_info_suumo.csv', index=None, encoding='utf-8-sig')
