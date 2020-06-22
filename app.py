from bs4 import BeautifulSoup
import requests
import lxml.html as lh
import pandas as pd

class ScheduleCrawler():
    def __init__(self, student_code):
        self.classes_code=set()
        self.student_code = student_code
        self.url = "http://sis.hust.edu.vn/ModulePlans/Timetables.aspx"
        self.form = {
            '__EVENTTARGET': '',
            'ctl00$MainContent$Studentid': '{}'.format(self.student_code),
            'ctl00$MainContent$btFind': ''
        }
        self.data = pd.read_excel('20192.xlsx')
        # self.data=pd.read_csv('20192.csv')
    def get_schedule(self):
        page = requests.post(self.url, data = self.form)
        if page.status_code == 200:
            try:
                doc = lh.fromstring(page.text)
                table_elements = doc.xpath('//table[@id="MainContent_gvStudentRegister_DXMainTable"]')[0]
                td_elements = table_elements.xpath('.//tr[@class="dxgvDataRow_SisTheme"]')
                for tr in td_elements:
                    class_code = tr[3].text_content().strip()
                    self.classes_code.add(class_code)
            except:
                return



    def printschedule(self):
        df=pd.DataFrame(columns=['Mã lớp','Mã HP','Tên HP','Ghi chú','Nhóm','Đợt','Tuần','Thứ','Ngày thi','Kíp thi','SLĐK','Phòng thi'])
        # df=pd.DataFrame()
        code=list(self.data['Mã lớp'])
        for class_code in self.classes_code:
            if float(class_code) in code:
                index=code.index(float(class_code))
                print(self.data.loc[index,:])
                a=self.data.loc[index,:]
                df=df.append(a,ignore_index=True)
        df=df.sort_values('Ngày thi')
        df.to_csv('output.csv',encoding='utf-8-sig')


    def convert_time(self,kip):
        time={
            '1':'7:00',
            '2':'9:30',
            '3':'13:00',
            '4':'15:00'
        }
        return time.get(kip)

    def get(self):
        df = pd.DataFrame(
            columns=['Mã lớp', 'Mã HP', 'Tên HP', 'Ghi chú', 'Nhóm', 'Đợt', 'Tuần', 'Thứ', 'Ngày thi', 'Kíp thi',
                     'SLĐK', 'Phòng thi'])
        # df=pd.DataFrame()
        code = list(self.data['Mã lớp'])
        for class_code in self.classes_code:
            if float(class_code) in code:
                index = code.index(float(class_code))
                a = self.data.loc[index, :]
                df = df.append(a, ignore_index=True)
        df = df.sort_values('Ngày thi')
        message=[]
        for i in range(len(df)):
            malop=df.loc[i,'Mã lớp']
            mahp=df.loc[i,'Mã HP']
            ten=df.loc[i,'Tên HP']
            thu=df.loc[i,'Thứ']
            ngay=str(df.loc[i,'Ngày thi']).split(' ')[0].split('-')
            date=ngay[2]+'/'+ngay[1]+'/'+ngay[0]
            kip=self.convert_time(df.loc[i,'Kíp thi'].split(' ')[1])
            phong=df.loc[i,'Phòng thi']
            mess='Mã lớp: {} {}\n{} \nThời gian: {} {} {} \nPhòng thi: {} '.format(int(malop),mahp,ten,kip,thu,date,phong)
            message.append(mess)
        return message

import json
import aiohttp
from os import environ
from aiohttp import web

# fanpage token
PAGE_ACCESS_TOKEN = 'EAAsUcgK3DnYBAO5LqWIz7JB3u33iXqSwN3eHnTFe22Ci3cilViwPTlXIs6ZBEIeLEIiilzeeZAcZCgthaLKmFtc9FYcjjDwPuE9Fg5nZCufe6EfPsrSkq1aE2RA3PDKvGtw1vX98eW0nG7iMxNQd5wf46rQxD4fnP0j6rB149owgiskxp34Ww8rIQpFPbdsZD'
# verify token
VERIFY_TOKEN = 's3Vip8lgh2GEkt60CnmnaZ1SBUYLixlg'

class BotControl(web.View):

    async def get(self):
        query = self.request.rel_url.query
        if(query.get('hub.mode') == "subscribe" and query.get("hub.challenge")):
            if not query.get("hub.verify_token") == VERIFY_TOKEN:
                return web.Response(text='Verification token mismatch', status=403)
            return web.Response(text=query.get("hub.challenge"))
        return web.Response(text='Forbidden', status=403)

    async def post(self):
        data = await self.request.json()
        if data.get("object") == "page":
            await self.send_greeting("Chào bạn. Nhập mã số sinh viên để xem lịch thi nhé.")

            for entry in data.get("entry"):
                for messaging_event in entry.get("messaging"):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        message_text = messaging_event["message"]["text"]

                        ID=message_text.lower()
#                         S= ScheduleCrawler(ID)
#                         contents=S.get_schedule()
#                         # S.printschedule()
#                         # await self.send_message(content)
#                         for content in contents:
#                             self.send_message(content)
                        self.send_message('hee')



        return web.Response(text='ok', status=200)

    async def send_greeting(self, message_text):
        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "setting_type": "greeting",
            "greeting": {
                "text": message_text
            }
        })
        async with aiohttp.ClientSession() as session:
            await session.post("https://graph.facebook.com/v3.0/me/thread_settings", params=params, headers=headers, data=data)

    async def send_message(self, sender_id, message_text):

        params = {
            "access_token": PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": message_text
            }
        })

        async with aiohttp.ClientSession() as session:
            await session.post("https://graph.facebook.com/v3.0/me/messages", params=params, headers=headers, data=data)



routes = [
    web.get('/', BotControl, name='verify'),
    web.post('/', BotControl, name='webhook'),
]

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=environ.get("PORT", 9090))

