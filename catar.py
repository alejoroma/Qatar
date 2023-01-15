import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import PyPDF2
import fnmatch
from alive_progress import alive_bar
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import circlify
import seaborn as sns
import matplotlib.pyplot as plt
import smtplib
import sys
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class Catar:
    prefix_week = ["Lun.", "Mar.", "Mié.", "Jue.", "Vie.", "Sáb.", "Dom."]
    def __init__(self, url, pdf_dir, txt_dir, img_dir):
        """Default constructor

        Args:
            url (string): site to make the web-scraping process
            pdf_dir (string): folder to save PDF type files
            txt_dir (string): folder to save TXT converted from PDF type piles
            img_dir (string): folder to save word-cloud plots
        """
        self._url = url
        self._pdf_dir = pdf_dir
        self._txt_dir = txt_dir
        self._png_dir = img_dir

    def send_remiders(self, link):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        try:
            team_a = soup.find("div", class_="team team-a").find("div", class_="team-name").findChild("span", class_="large").text
            team_b = soup.find("div", class_="team team-b").find("div", class_="team-name").findChild("span", class_="large").text
            game_hour = soup.find("div", class_="cpr-info")
            location = soup.find("li", class_= "data-li-h")
            print(team_a, team_b)
            print(game_hour.findChild("span", "hour").text[0:5])
            print(location.findChild("span", "data-li-txt").text)
            return {
                "vs": team_a +" vs " + team_b,
                "game_hour": game_hour.findChild("span", "hour").text[0:5],
                "location": location.findChild("span", "data-li-txt").text
            }
        except:
            print('something wrong')
            return []

    def reminder(self):
        dt = datetime.now().time()
        curret_hour = int(str(dt.hour) + str(dt.minute))
        print(curret_hour)
        page = requests.get(self._url)
        soup = BeautifulSoup(page.content, 'html.parser')
        mt = datetime.now()
        next_weekDay = 0
        if mt.weekday() == 6:
            next_weekDay = 0
        else:
            next_weekDay = mt.weekday() + 1
        current_day = str(mt.day) + "" + self.prefix_week[mt.weekday()]
        #next_day = str(int(mt.day) + 1) + "" + self.prefix_week[next_weekDay]
        next_day = "13Mar."
        print(next_day)
        try:
            div_next_day = {}
            divs = soup.find_all('td', class_='day')
            for div in divs:
                date_day = div.findChild('div', class_='date').text
                if date_day == next_day:
                    div_next_day = div
                    break
            
            end_matches = div_next_day.findChild('a', class_='marcador no-comenzado marcador')
            if end_matches == None:
                return False
            print(end_matches)
            print(end_matches["href"])
                
            return end_matches["href"]
        except:
            print('something wrong')
            return []

    def generate_resume(self, link):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        try:

            ps_labels = soup.find_all('p', class_='stat-tl ev-fw-tl')
            ps_score = soup.find_all('p', class_='ev-text-aux')
            label_resume = soup.find_all('span', class_='name-large')
            score_resume = soup.find_all('span', class_='scr-hdr__score')
            full_resume = label_resume[0].text.replace("\n", "").strip() + " " +  score_resume[0].text.replace("\n", "").replace(" ", "").strip() + " - " + label_resume[1].text.replace("\n", "").strip() + " "+  score_resume[1].text.replace("\n", "").replace(" ", "").strip()
            exit = [full_resume]
            index = 0
            for p in ps_labels:
                exit.append({
                    "label": p.text,
                    "score": ps_score[index].text
                })
                index = index +  1
                
            return exit
        except:
            print('something wrong')
            return []
        return 0

    def get_urls(self):
        page = requests.get(self._url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        #current_day = str(dt.day) + ""+  self.prefix_week[dt.weekday()]
        current_day = "06Mar."
        print(current_day)
        try:
            div_current_day = {}
            divs = soup.find_all('td', class_='day')
            for div in divs:
                date_day = div.findChild('div', class_='date').text
                if date_day == current_day:
                    div_current_day = div
                    break
            
            end_matches = div_current_day.findChildren('a', class_='marcador finalizado marcador', recursive= True)
            final_links = []
            for ends in end_matches:
                if ends["href"] not in final_links:
                    final_links.append(ends["href"])
                
            return final_links
            
            # marcador finalizado marcador

                # book_url = div.findChild('a', href=True)['href']
                # download_url = self._url + book_url
                # download_page = requests.get(download_url)
                # download_soup = BeautifulSoup(download_page.content, 'html.parser')
                # footer = download_soup.find('div', {'id' : 'footer'})
                # file_name = footer.contents[0]
                # full_url = download_url + file_name
        except:
            print('something wrong')
            return []


    def send_email(self, template, obj_from):
        emails = ['brayansteven64@hotmail.com', 'daniel.contreras@uptc.edu.co', 'jesusalejandro.rodriguez@uptc.edu.co']
        names = [ f'Grupo 6 {obj_from}' ] * len(emails)

        s =smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
        s.starttls()
        s.login('brayansteven67@gmail.com', 'pjom hnko dvvd camw')

        for name, email in zip (names, emails):
            message = MIMEMultipart()

            message["From"] = name
            message["To"] = email
            message['Subject'] = "Suscripción de " + obj_from
            html = """\
                contenido html
            """
            #message.attach(MIMEText("Hola aqui esta el backup del dia de hoy UwU e.e", 'plain'))  
            message.attach(MIMEText(template,'html'))
            # attach1 = MIMEApplication(open(sys.argv[1]).read(), _subtype="txt")
            # attach1.add_header('Content-Disposition', 'attachment', filename=str(
            #     os.path.basename(sys.argv[1])))
            # message.attach(attach1)

            # attach2 = MIMEApplication(open(sys.argv[2]).read(), _subtype="txt")
            # attach2.add_header('Content-Disposition', 'attachment', filename=str(
            # os.path.basename(sys.argv[2])))
            # message.attach(attach2)

            s.send_message(message)
            del message

        s.quit()

if __name__ == '__main__':
    url = 'https://resultados.as.com/resultados/futbol/mundial/calendario/dias/'
    pdf_dir = 'pdf/'
    txt_dir = 'txt/'
    img_dir = 'img/'
    ba = Catar(url, pdf_dir, txt_dir, img_dir)
    link = ba.reminder()
    remider_resume = ba.send_remiders(link)
    html_reminder = f"""\
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Recordatorio</title>
                </head>
                <body>
                    <h1>Partido {remider_resume["vs"]}</h1>
                    <p>Estadio: {remider_resume["location"]}</p>
                    <p>Hora: {remider_resume["game_hour"]}</p>
                </body>
                </html>
            """#.format(vs= remider_resume.vs, location=remider_resume.location , game_hour=remider_resume.game_hour)
    final_links = ba.get_urls()
    for link in final_links:
        resum = ba.generate_resume(link)
        html_resume = f"""\
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Resumen del partido</title>
                    </head>
                    <body>
                        <h1>Resultados {resum.pop(0)}</h1>
        """
        ele_score = """"""
        for obj in resum:
            ele_score = ele_score + f"""
            <hr>
            <p>{obj["label"]}</p>
            <p>{obj["score"]}</p>
            """
        html_resume = html_resume + ele_score + """
        </body>
        </html>
        """
    ba.send_email(html_resume, "resumen")
    ba.send_email(html_reminder, "recordatorio")