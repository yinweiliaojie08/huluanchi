import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def get_content(target):
    req = requests.get(url = target)
    req.encoding = 'utf-8'
    html = req.text
    bf = BeautifulSoup(html, 'lxml')
    texts = bf.find('div',class_='content')
    content = texts.text.strip().split('\xa0'*4)
    return content



if __name__ == '__main__':
    target = 'https://book.zongheng.com/showchapter/1187484.html'
    book_name = '万界剑尊.txt'
    req = requests.get(url = target)
    req.encoding = 'utf-8'
    html = req.text
    chapter_bs = BeautifulSoup(html, 'lxml')
    chapters = chapter_bs.find('div', class_='container').find('div', class_='volume-list').find_all('a')
    for chapter in tqdm(chapters):
        chapter_name = chapter.string
        url = chapter.get('href')
        try:
            content = get_content(url)
        except Exception as e:
            print(e)
        else:
           with open(book_name, 'a', encoding='utf-8') as f:
                f.write(chapter_name)
                f.write('\n')
                f.write('\n'.join(content))
                f.write('\n')
