import os
from aip import AipOcr
import json
import sys
import pandas as pd
import csv

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def pic_text_recognition(picname):
    with open(picname, 'rb') as fp:
        image = fp.read()
    dic_result = client.basicAccurate(image)
    return dic_result


if __name__ == '__main__':
    result_file='domain.csv'
    localdir = os.path.split(os.path.realpath(sys.argv[0]))[0]
    allfilenames = os.listdir(localdir)
    with open( result_file , 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        data = ["domain", "main", "png_name"]
        writer.writerow(data)
    for png_name in allfilenames:
        if os.path.splitext(png_name)[1] in ['.png']:
            print(f"当前处理文件为{png_name}")
            data_dict = pic_text_recognition(png_name)['words_result']
            for data in data_dict:
                if data["words"].startswith('域名：'):
                    domain = data["words"]
                if data["words"].startswith('域名持有者'):
                    main = data["words"]
            csv_data = [domain,  main, png_name]
            with open(result_file, 'a',newline="" , encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(csv_data)
    print("文件已保存，开始排序。。。")
    # 开始排序
    df = pd.read_csv(result_file)
    data = pd.DataFrame(df).sort_values(by='main', axis=0)
    data.to_csv(result_file, index=False, encoding='utf-8-sig')
    print("所有操作已结束。。。")
