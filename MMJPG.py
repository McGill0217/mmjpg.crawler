#!/usr/bin/python3
# coding: utf-8

import os
import sys
import time
import random
import requests
import logging  # 日志处理
from urllib import request  # request
from lxml import etree  # xpath

# 日志格式: 日期 - 时间 ### 日志
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# 日志处理基本设置
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
logging_formatter = logging.Formatter(LOGGING_FORMAT)
# 设置日志文件
log_file = logging.FileHandler('log.txt')
log_file.setLevel(level=logging.DEBUG)
log_file.setFormatter(logging_formatter)
# 设置控制台
console = logging.StreamHandler(stream=sys.stdout)
console.setLevel(level=logging.DEBUG)
console.setFormatter(logging_formatter)

logger.addHandler(log_file)
logger.addHandler(console)


# 下载模特图片
def model_picture_download(url_each_girl, model_picture_url, model_dir, each_girl_text):
    model_picture_url_split = model_picture_url.split('/', -1)
    model_picture_file_name = model_picture_url_split[-1]
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            headers = {
                'Referer': url_each_girl,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
            }
            html_model_picture = requests.get(
                model_picture_url, headers=headers, timeout=30)
            with open(model_dir + '/' + model_picture_file_name, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                logger.info('下载成功！图片 = ' + model_picture_file_name)
        except Exception:
            err_status += 1
            random_int = random.randint(30, 60)
            time.sleep(random_int)
            logger.debug('出现异常！睡眠 ' + str(random_int) + ' 秒')


# 遍历模特相关网页，查找出所有图片URL
def model_picture_findall(each_girl_href, each_girl_text):
    model_dir = 'E:/MMJPG/' + each_girl_text
    # 建立文件夹
    if os.path.exists(model_dir) is False:
        os.makedirs(model_dir, 0o777)
    # 日志记录
    logger.info('------------------------------')
    logger.info('创建目录成功！目录 = ' + each_girl_text)
    picture_index = 1
    last_picture = False
    while last_picture is False:
        url_each_girl = each_girl_href + '/' + str(picture_index)
        model_picture_findout = False
        err_status = 0
        while model_picture_findout is False and err_status < 10:
            try:
                http_response_model = request.urlopen(
                    url_each_girl, timeout=30)
                html_model = http_response_model.read().decode('utf-8')
                tree_model = etree.HTML(html_model)
                # 提取图片地址
                model_picture_data = tree_model.xpath(
                    '//div[@class="content"]/a/img')
                model_picture_url = model_picture_data[0].attrib['src']
                # 提取图片下方按钮数据
                model_picture_navigation_data = tree_model.xpath(
                    '//div[@class="page"]/a')
                # 找出该MM的图片数量
                model_picture_num = model_picture_navigation_data[-2].text

                # 下载本张图片
                model_picture_download(
                    url_each_girl, model_picture_url, model_dir, each_girl_text)
                # 下载成功，索引+1
                picture_index += 1
                model_picture_findout = True
                # time.sleep(1)
            except Exception:
                err_status += 1
                random_int = random.randint(30, 60)
                time.sleep(random_int)
                logger.debug('出现异常！睡眠 ' + str(random_int) + ' 秒')
        # 判断已下载图片张数
        if picture_index <= int(model_picture_num):
            last_picture = False
        else:
            last_picture = True


# 遍历网站，查找出所有模特URL
def model_findall(url_prefix, page_num):
    for page_index in range(74, page_num+1, 1):
        if page_index == 1:
            url_page = url_prefix
        else:
            url_page = url_prefix + 'home/' + str(page_index)

        model_findout = False
        err_status = 0
        while model_findout is False and err_status < 10:
            try:
                http_response_page = request.urlopen(
                    url_page, timeout=30)   # 超时时间：30 S
                html_page = http_response_page.read().decode('utf-8')
                tree_page = etree.HTML(html_page)
                girl_data = tree_page.xpath('//span[@class="title"]/a')
                for each_girl in girl_data:
                    each_girl_href = each_girl.attrib['href']
                    each_girl_text = each_girl.text
                    # 日志记录
                    logger.info('###################################')
                    logger.info('网址：' + url_page)
                    logger.info(each_girl_href + ' : ' + each_girl_text)
                    model_picture_findall(each_girl_href, each_girl_text)
                    model_findout = True
            except Exception:
                err_status += 1
                random_int = random.randint(30, 60)
                time.sleep(random_int)
                logger.debug('出现异常！睡眠 ' + str(random_int) + ' 秒')
        if page_index % 2 == 0:
            time.sleep(1800)
            logger.info('下载暂停！睡眠1800秒')


if __name__ == '__main__':
    model_findall('http://www.mmjpg.com/', 107)
