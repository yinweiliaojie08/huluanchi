import requests
import re
import json
import os

session = requests.session()

def fetch_url(url):
    return session.get(url).content.decode('utf-8')

def get_doc_id(url):
   if re.findall('.html', url):
      doc_id = re.findall('view/(.*).html', url)[0]
   else:
      doc_id = re.findall('view/(.*)\?', url)[0]
   return doc_id

def parse_title(content):
    return re.findall(r"title.*?\:.*?\"(.*?)\"\,", content)[0]

def save_file(filename, content):
    with open(filename, 'w', encoding='utf8') as f:
        f.write(content)
        print('已保存为:' + filename)

def parse_txt(doc_id):
    content_url = 'https://wenku.baidu.com/api/doc/getdocinfo?callback=cb&doc_id=' + doc_id
    content = fetch_url(content_url)
    md5 = re.findall('"md5sum":"(.*?)"', content)[0]
    pn = re.findall('"totalPageNum":"(.*?)"', content)[0]
    rsign = re.findall('"rsign":"(.*?)"', content)[0]
    content_url = 'https://wkretype.bdimg.com/retype/text/' + doc_id + '?rn=' + pn + '&type=txt' + md5 + '&rsign=' + rsign
    content = json.loads(fetch_url(content_url))
    result = ''
    for item in content:
        for i in item['parags']:
            result += i['c'].replace('\\r', '\r').replace('\\n', '\n')
    return result

if __name__ == "__main__":
   url = input('请输入要下载的文库URL地址: ')
   content = fetch_url(url)
   doc_id = get_doc_id(url)
   title = parse_title(content)
   print(parse_txt(doc_id))
   result = parse_txt(doc_id)
   save_file(title + '.txt', result)
