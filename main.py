import re
import sqlite3
import requests
from codecs import *

from PIL import Image
# root
root = "http://lb.wikipedia.org/"
api_get_url = "w/api.php?action=query&format=json&list=allpages&aplimit=500&apfilterredir=nonredirects&rawcontinue&apfrom="
api_image_info = "w/api.php?action=query&prop=images&format=json&imlimit=500&pageids="
api_article_info = "w/api.php?action=query&prop=info&format=json&inprop=url&pageids="
# name of article on which stopped
last_article = "1619"

# db connection
con = sqlite3.connect("articles.db")
cur = con.cursor()


class OffLineExplorer:
    @staticmethod
    def check_db():
        cur.execute(
            "CREATE TABLE IF NOT EXISTS articlesInfo (id INTEGER PRIMARY KEY, title TEXT, url TEXT, countOfImage INTEGER)")
        con.commit()


    @staticmethod
    def create_html():
        cur.execute("""SELECT title, url, countOfImage
        FROM   articlesInfo
        WHERE  countOfImage=(SELECT MAX(countOfImage) FROM articlesInfo)""")
        # cur.execute("SELECT MAX(countOfImage) FROM articlesInfo")
        arr = (cur.fetchall())
        con.commit()
        file_html = open('index.html', 'w', "utf-8")
        file_html.write("""
        <!DOCTYPE html>
        <h1>Articles with maximum number of images in %s</h1>
        """ % (root,))
        for article in arr:
            # file_html.write('<a href="%s">%s</a> — count = %s <br>' % ((article[1]).encode(), (article[0]).encode(), (article[2])))
            print('<a href="%s">%s</a> - count = %s <br>' % (str(article[1]), str(article[0]), str(article[2])), file = file_html)


class WebSurfer:
    @staticmethod
    def start_analyzer():
        flag = 1
        next_article = last_article
        counter = 0
        while flag == 1:
            # information_json = urllib.request.urlopen(root + api_get_url + next_article).read()
            # print(str(information_json)[1:])
            counter = counter + 1
            information = requests.get(root + api_get_url + next_article).json()
            #print(information)
            try:
                next_article = information["query-continue"]["allpages"]["apcontinue"]
            except:
                flag = 0
            for page in information["query"]["allpages"]:
                WebSurfer.check_page(page["pageid"])

    @staticmethod
    def get_image_size(url):
        img = Image.open(url)
        return img.size

    @staticmethod
    def check_page(id):
        imgs = requests.get(root + api_image_info + str(id)).json()
        article_info = requests.get(root + api_article_info + str(id)).json()
        print(article_info["query"]["pages"][str(id)]["fullurl"])
        imgCount = 0;
        try:
            imgCount = len(imgs["query"]["pages"][str(id)]["images"])
            try:
                img_continue = imgs["query-continue"]["images"]["imcontinue"]
                while img_continue != "":
                    imgs = requests.get(root + api_image_info + str(id)+"&imcontinue="+img_continue).json()
                    imgCount += len(imgs["query"]["pages"][str(id)]["images"])
                    img_continue = imgs["query-continue"]["images"]["imcontinue"]
            except:
                img_continue = ""
        except:
            imgCount = 0
        WebSurfer.save_page_info(imgs["query"]["pages"][str(id)]["title"], imgCount, article_info["query"]["pages"][str(id)]["fullurl"])

    @staticmethod
    def save_page_info(title, img_count, url):

        #title = title.replace('\'', ' ')
        #title = title.replace('\"', ' ')
        title = re.sub('(\")','\\\\"' ,title)
        title = re.sub('(\')',"\\\\'",title)
        title = "`" + title + "`"
        counter = cur.execute("SELECT count(id) FROM articlesInfo WHERE url = ?",(url,))
        # print(counter.fetchall()[0][0])
        if counter.fetchall()[0][0] > 0:
            cur.execute("DELETE FROM articlesInfo WHERE url = ?", (url,))
            print("Deleted")
        cur.execute("INSERT INTO articlesInfo (title, url, countOfImage) VALUES (?,?,?)",(title, url, img_count))
        con.commit()

OffLineExplorer.check_db()
WebSurfer.start_analyzer()
OffLineExplorer.create_html()
con.close()
