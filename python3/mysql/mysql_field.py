#!/bin/env python3

"""
自动生成MySQL数据表的数据字典支持多个
目前只支持单库,有兴趣的可以增加一个列表循环
author: zhangjt
date: 2022-06-29
"""

import pymysql
import os
import time


class DataDict(object):
    def __init__(self, conn_list):
        # 数据库连接配置
        self.host_name = conn_list[0]
        self.user_name = conn_list[1]
        self.pwd = conn_list[2]
        self.db_name = conn_list[3]
        self.folder_name = 'mysql_dict'
        self.port = int(conn_list[4])
        self.charset = conn_list[5]

    def run(self, table_list):
        """脚本执行入口"""
        try:
            # 创建一个连接
            conn = pymysql.connect(host=self.host_name, user=self.user_name, password=self.pwd, database=self.db_name, port=self.port, charset=self.charset)
            # 用cursor()创建一个游标对象
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        except Exception:
            print('数据库连接失败，请检查连接信息！')
            exit(1)
        for table_name in table_list:
            # 判断表是否存在
            sql = "SHOW TABLES LIKE '%s'" % (table_name,)
            cursor.execute(sql)
            result_count = cursor.rowcount
            if result_count == 0:
                print('%s数据库中%s表名不存在，无法生成……' % (self.db_name, table_name))
                continue
            # 表注释获取
            print('开始生成表%s的数据字典' % (table_name,))
            sql = "show table status WHERE Name = '%s'" % (table_name,)
            cursor.execute(sql)
            result = cursor.fetchone()
            table_comment = result['Comment']
            # 文件夹和文件处理
            file_path = self.folder_name + os.sep + table_name + '.md'
            self.deal_file(file_path)
            # 打开文件，准备写入
            dict_file = open(file_path, 'a', encoding='UTF-8')
            dict_file.write('#### %s %s' % (table_name, table_comment))
            dict_file.write('\n | 字段名称 | 字段类型 | 默认值 | 字段注释 |')
            dict_file.write('\n | --- | --- | --- | --- |')
            # 表结构查询
            field_str = "COLUMN_NAME,COLUMN_TYPE,COLUMN_DEFAULT,COLUMN_COMMENT"
            sql = "select %s from information_schema.COLUMNS where table_schema='%s' and table_name='%s'" % (field_str, self.db_name, table_name)
            cursor.execute(sql)
            fields = cursor.fetchall()
            for field in fields:
                column_name = field['COLUMN_NAME']
                column_type = field['COLUMN_TYPE']
                column_default = str(field['COLUMN_DEFAULT'])
                column_comment = field['COLUMN_COMMENT']
                info = ' | ' + column_name + ' | ' + column_type + ' | ' + column_default + ' | ' + column_comment + ' | '
                dict_file.write('\n ' + info)
            # 关闭连接
            print('完成表%s的数据字典' % (table_name,))
            dict_file.close()
        cursor.close()
        conn.close()

    def deal_file(self, file_name):
        """处理存储文件夹和文件"""
        # 不存在则创建文件夹
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
        # 删除已存在的文件
        if os.path.isfile(file_name):
            os.unlink(file_name)

    def test_conn(self, conn_info):
        """测试数据库连接"""
        try:
            # 创建一个连接
            pymysql.connect(host=conn_info[0], user=conn_info[1], password=conn_info[2], database=conn_info[3], port=int(conn_info[4]), charset=conn_info[5])
            return True
        except Exception:
            return False


if __name__ == '__main__':
    # 数据库连接信息（ip, user, password, database, port, 字符集）
    conn_list = ["127.0.0.1","root","123456","shinemo","33306","utf8"]
    # 测试数据库连接问题
    dd_test = DataDict(conn_list)
    db_conn = dd_test.test_conn(conn_list)
    print("数据库连接状态为%s" %(db_conn))
    if db_conn == False:
        print("数据库连接失败，请检查!")
        exit(1)

    # 输入数据表名称
    table_s = ["user","user_one","user_table","user_two"]
    dd = DataDict(conn_list)
    dd.run(table_s)
    time.sleep(1)
