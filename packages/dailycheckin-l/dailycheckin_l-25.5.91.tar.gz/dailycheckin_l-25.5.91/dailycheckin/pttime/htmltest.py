import os
import unittest
import re

from bs4 import BeautifulSoup


class MyTestCase(unittest.TestCase):


    def test_something(self):
        html_file_path = os.path.join(os.path.dirname(__file__), "tmp-success.html")

        # 读取HTML文件内容
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取用户信息
        user_info = soup.find('span', class_='medium left').text.strip()
        user_name = soup.find('a', class_='EliteUser_Name').text.strip()
        user_id = soup.find('a', class_='EliteUser_Name')['href'].split('=')[-1]

        # 提取用户等级
        # 使用正则表达式提取等级
        pattern = r'\[UID=\d+\]\[(.*?)\]'
        match = re.search(pattern, user_info)

        if match:
            user_level = match.group(1)
        else:
            user_level = 'UNKnow'

        # 提取签到记录
        attendance_info = soup.find('table', class_='mainouter mt5').findChild("td", class_="embedded")

        # 初始化变量
        first_checkin = ''
        days_since_first_checkin = ''
        current_consecutive_start = ''

        for span in attendance_info:
            text = span.text.strip()
            if '第一次签到：' in text:
                first_checkin = text.split('：')[1]
            elif '距今：' in text:
                days_since_first_checkin = text.split('：')[1]
            elif '本次连续签到开始时间：' in text:
                current_consecutive_start = text.split('：')[1]

        # 解析签到记录
        checkin_result = attendance_info.find('p').text
        if '今日签到成功' == checkin_result:
            current_checkin_info = attendance_info.find('ul').find('li').findAll('b')
            total_days = current_checkin_info[0].text
            consecutive_days = current_checkin_info[1].text
            magic_points = current_checkin_info[2].text
            checkin_level = attendance_info.find('span', class_='ml10').find('b').text
            msg = [
                {"name": "用户名", "value": user_name},
                {"name": "用户ID", "value": user_id},
                {"name": "用户等级", "value": user_level},
                {"name": "签到结果", "value": checkin_result},
                {"name": "本次获取魔力", "value": magic_points},
                {"name": "总签到天数", "value": total_days},
                {"name": "连续签到天数", "value": consecutive_days},
                {"name": "第一次签到", "value": first_checkin},
                {"name": "距今", "value": days_since_first_checkin},
                {"name": "本次连续签到开始时间", "value": current_consecutive_start},
                {"name": "签到等级", "value": checkin_level},
            ]
        else:
            msg = [
                {"name": "用户名", "value": user_name},
                {"name": "用户ID", "value": user_id},
                {"name": "用户等级", "value": user_level},
                {"name": "签到结果", "value": "请勿重复签到"},
                {"name": "第一次签到", "value": first_checkin},
            ]

        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        print(msg)


if __name__ == '__main__':
    unittest.main()
