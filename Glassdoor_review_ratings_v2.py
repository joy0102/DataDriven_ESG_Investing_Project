#!/usr/bin/env python
# coding: utf-8


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pyquery import PyQuery as pq
import csv


# 定义一个类
class glass_door_infos:
    def __init__(self):
        # 公司查询页面
        url = 'https://www.glassdoor.com/Reviews/index.htm'
        self.url = url

        # Initializing the webdriver
        options = webdriver.ChromeOptions()

        # Uncomment the line below if you'd like to scrape without a new Chrome window every time.
        # options.add_argument('headless')

        # Change the path to where chromedriver is in your home folder.
        #exe_path = "D:/python/Scripts/chromedriver.exe"
        exe_path = "./chromedriver"

        self.browser = webdriver.Chrome(executable_path=exe_path, options=options)
        self.browser.set_window_size(1120, 1000)
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长为10s

        # 定义公司链接地址list
        self.company_url_list = []

        # 保存到csv文件
        f1 = open('result.csv', mode='a', encoding='utf-8', newline='')
        self.csv_writer = csv.DictWriter(f1, fieldnames=['companyName', 'title', 'num'])
        self.csv_writer.writeheader()

    # 读取文件信息
    def read_company_csv(self):

        f = open('companyinfo.csv', mode='a', encoding='utf-8', newline='')
        csv_writer = csv.DictWriter(f, fieldnames=['company_name', 'company_url'])
        csv_writer.writeheader()

        # 读取文件信息
        with open('fortune100.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                company_name = row[2] #1->2
                company_url = infos.get_company_url(company_name)
                dic = {
                    'company_name': company_name,
                    'company_url': company_url
                }
                csv_writer.writerow(dic)

    # 获取公司链接
    def get_company_url(self, company_name):
        self.browser.get(self.url)
        WebDriverWait(self.browser, 5)
        time.sleep(2)

        # 获取输入框 company
        search_el = WebDriverWait(self.browser, 10).until(
            EC.visibility_of(self.browser.find_element(by=By.ID, value='KeywordSearch')))
        search_el.send_keys(company_name)

        # 获取查询按钮
        search_button = self.browser.find_element_by_id('HeroSearchButton')
        WebDriverWait(self.browser, 5)
        search_button.click()

        # 等待3s
        time.sleep(3)

        try:
            # 获取第一家公司链接标签
            company_first = WebDriverWait(self.browser, 5).until(
                EC.visibility_of(
                    self.browser.find_element_by_xpath('//*[@id="MainCol"]/div/div[1]/div/div[1]/div/div[2]/h2/a')))
            company_url = company_first.get_attribute('href')
            print(company_name + '公司第一个链接地址为' + company_url)
            self.company_url_list.append(company_url)
        except Exception:
            company_url = self.browser.current_url
            print(company_name + '公司点击搜索后直接进入的详情页面,直接将当前页面的路径【' + company_url + '】保存。')
            self.company_url_list.append(company_url)
        return company_url

    # 获取公司详情信息
    def get_company_info(self):
        self.browser.get(self.url)
        
        # 登陆
        time.sleep(30)
        
        # 读取文件信息
        with open('companyinfo.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                try:
                    print('开始获取【' + row[0] + '】')
                    self.browser.get(row[1])
                    # 模拟点击事件
                    more = WebDriverWait(self.browser, 10).until(
                        EC.visibility_of(self.browser.find_element_by_class_name('eky1qiu1')))
                    more.click()
                    time.sleep(2)

                    # 获取信息
                    html = self.browser.page_source
                    doc = pq(html)
                    items = doc.find('.mb .categoryRaÅting').items()
                    i = 1
                    for item in items:
                        title = item.find('.ratingTrends__RatingTrendsStyle__categoryText').text()
                        if i:
                            num = item.find('.ratingTrends__RatingTrendsStyle__overallRatingNum').text()
                            i = 0
                        else:
                            num = item.find('.ratingTrends__RatingTrendsStyle__ratingNum').text()
                        print('title:' + title + ',num:' + num)
                        dic = {
                            'companyName': row[0],
                            'title': title,
                            'num': num
                        }
                        self.csv_writer.writerow(dic)
                except Exception as e:
                    print(row[0] + '公司获取信息失败' + e)


if __name__ == "__main__":
    # 初始化
    infos = glass_door_infos()

    # 读取csv文件获取公司详情地址 这一步可以执行一次，会将公司的地址写入到companyinfo.csv文件中
    infos.read_company_csv()

    # 获取公司评论信息， 这个一步是获取公司的详情信息，看自己的需求还需要获取啥
    #infos.get_company_info()
