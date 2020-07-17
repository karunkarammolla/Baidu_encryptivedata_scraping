from datetime import datetime, timedelta
import pandas as pd
import requests
import json
import os

COOKIES = 'BIDUPSID=08DAE6217CDAF5DB15998F1DB2156AD6; PSTM=1594132556; BAIDUID=08DAE6217CDAF5DBFC44776364B2FD60:FG=1; BDUSS=prdFBvcU5QT3JFRDJMNUxSWTFYZ1J0OTR6a1Jpa1JIdlhDMU9Rb2F4T2dHQzFmRVFBQUFBJCQAAAAAAQAAAAEAAADiVs0eYWN1aXR5a3BiZWoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKCLBV-giwVfTG; bdindexid=l6qi0gf6j6q3ucjt478cdb8m23; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1594257579,1594315885,1594420244,1594438842; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1594439279; RT="z=1&dm=baidu.com&si=ndbl4und5so&ss=kch2w151&sl=5&tt=1dsb&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"'

headers = {
    'Host': 'index.baidu.com',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}
all_kind = ['all', 'pc', 'wise']


def delete_files_from_folder(folderpath):
    for root, dirs, files in os.walk(folderpath):
        for f in files:
            os.unlink(os.path.join(root, f))


def get_result(keyword, start_date_tuple, end_date_tuple):
    index_value_list = []
    encrypt_datas, uniqid = get_encrypt_datas(keyword, start_date_tuple, end_date_tuple)
    key = get_key(uniqid)
    startDate = encrypt_datas[0]['all']['startDate']
    for encrypt_data in encrypt_datas:
        for kind in all_kind:
            encrypt_data[kind]['data'] = decrypt_func(key, encrypt_data[kind]['data'])
            index_value_list.append(encrypt_data[kind]['data'])
    final_list = date_range_maping(len(encrypt_datas[0]['all']['data']), index_value_list[0], startDate, keyword)
    return final_list


def get_encrypt_datas(keyword, start_date_tuple, end_date_tuple):
    url = 'http://index.baidu.com/api/SearchApi/index?area=0&word=[[%7B%22name%22:%22' + keyword + \
          '%22,%22wordType%22:1%7D]]&startDate='+str(start_date_tuple)+'&endDate='+str(end_date_tuple)
    html = http_get_request(url, cookies=COOKIES)
    try:
        datas = json.loads(html)

        uniqid = datas['data']['uniqid']

        encrypt_datas = []
        for single_data in datas['data']['userIndexes']:
            encrypt_datas.append(single_data)
    except:
        encrypt_datas = []
        uniqid = None
        pass
    return (encrypt_datas, uniqid)


def get_key(uniqid):
    url = 'http://index.baidu.com/Interface/api/ptbk?uniqid=%s' % uniqid
    html = http_get_request(url)
    datas = json.loads(html)
    key = datas['data']
    return key


def http_get_request(url, cookies=COOKIES):
    headers['Cookie'] = cookies
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


def decrypt_func(key, data):
    """
    decrypt data
    """
    a = key
    i = data
    n = {}
    s = []

    for o in range(len(a)//2):
        n[a[o]] = a[len(a)//2 + o]

    for r in range(len(data)):
        s.append(n[i[r]])

    return ''.join(s).split(',')


def date_range_maping(time_len, index_value_list, start_date, keyword):
    date_list = []
    cur_date = datetime.strptime(start_date, '%Y-%m-%d')
    for i in range(time_len):
        date_list.append(cur_date.strftime('%Y-%m-%d'))
        cur_date += timedelta(days=1)
    result = [[i, j, keyword] for i, j in zip(date_list, index_value_list)]
    return result


# delete_files_from_folder(os.getcwd() + "\\Baidu_Output" + "\\")

#
# df_keyword_list = pd.read_excel('keywords.xlsx')
# for keyword in df_keyword_list['Keywords'].values.tolist():
#     try:
#         final_data = []
#         if '&' in str(keyword):
#             keyword = keyword.replace('&', '%26')
#         else:
#             keyword = keyword
#         date_tuples = [('2018-01-01', '2019-01-01'), ('2019-01-02', '2020-01-01'), ('2020-01-02', '2020-12-01')]
#         for date_group in date_tuples:
#             start_date_tuple = date_group[0]
#             end_date_tuple = date_group[1]
#             data = get_result(keyword, start_date_tuple, end_date_tuple)
#             final_data.extend(get_result(keyword, start_date_tuple, end_date_tuple))
#
#         df = pd.DataFrame(final_data, columns=['Date', 'Index', 'Keyword'])
#         file_path = r'C:\Users\nimmi\PycharmProjects\untitled\Baidu_Scraping_Code\Baidu_Output\\'
#         file_name = 'Baidu_Scraping' + '_' + keyword + '.csv'
#         file = file_path + file_name
#         df.to_csv(file, index=False)
#         print('File generated for Keyword ', keyword)
#     except:
#         print('File not generated for Keyword', keyword)


# # Merging all csv files
path = r'C:\Users\nimmi\PycharmProjects\untitled\Baidu_Scraping_Code\previous_output\\'
output_path = r'C:\Users\nimmi\PycharmProjects\untitled\Baidu_Scraping_Code\Merged_File\\'
outfname = 'Baidu_2.5_output_all.xlsx'
output = output_path + outfname
main_df = pd.DataFrame()
for root, dirs, files in os.walk(path):
    for fname in files:
        try:
            print(fname)
            df = pd.DataFrame()
            df = pd.read_csv(path+fname)
            main_df = main_df.append(df)
        except:
            pass

main_df.to_excel(output, index=False, encoding="utf_8_sig")

