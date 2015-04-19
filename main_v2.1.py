import re
import sqlite3
import requests
import urllib
from codecs import *

from PIL import Image
# root
root = "http://he.wikipedia.org/"
api_get_url = "w/api.php?action=query&generator=allpages&gapfilterredir=nonredirects&rawcontinue&prop=images|info&inprop=url&imlimit=500&format=json&gaplimit="
#api_get_url = "w/api.php?action=query&format=json&list=allpages&aplimit=500&apfilterredir=nonredirects&rawcontinue&apfrom="
#api_image_info = "w/api.php?action=query&prop=images&format=json&imlimit=500&pageids="
#api_article_info = "w/api.php?action=query&prop=info&format=json&inprop=url&pageids="


# name of article on which stopped
last_article = ""

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
        ORDER BY countOfImage DESC
        LIMIT 50""")
        # cur.execute("SELECT MAX(countOfImage) FROM articlesInfo")
        arr = (cur.fetchall())
        con.commit()
        file_html = open('index.html', 'w', "utf-8")
        file_html.write("""
        <!DOCTYPE html>
        <meta charset="utf-8">
        <style>

        </style>
        <h1>Articles with maximum number of images in %s</h1>
        <table>
        """ % (root,))
        for article in arr:
            # file_html.write('<a href="%s">%s</a> — count = %s <br>' % ((article[1]).encode(), (article[0]).encode(), (article[2])))
            print('<tr><td><a href="%s">%s</a></td><td>%s</td></tr>' % (str(article[1]), urllib.parse.unquote(str(article[1])[29:]), str(article[2])), file = file_html)
        file_html.write("""</table>""")


class WebSurfer:
    @staticmethod
    def start_analyzer():
        flag = 1
        next_article = last_article
        counter = 0
        gaplimit = 500
        while flag == 1:
            gaplimit = 50;
            # information_json = urllib.request.urlopen(root + api_get_url + next_article).read()
            # print(str(information_json)[1:])
            counter = counter + 1
            information = requests.get(root + api_get_url + str(gaplimit) + "&gapfrom=" + next_article).json()
            #print(information)
            try:
                while gaplimit>9 and information["query-continue"]["images"]["imcontinue"] != "":
                    print(information["query-continue"]["images"]["imcontinue"])
                    gaplimit -= 10
                    if gaplimit == 0:
                        gaplimit = 1
                    information = requests.get(root + api_get_url + str(gaplimit) + "&gapfrom=" + next_article).json()
                    #print(information)
            except:
                gaplimit = 500
            try:
                next_article = information["query-continue"]["allpages"]["gapcontinue"]
            except:
                flag = 0
            write_or = True
            for page in information["query"]["pages"]:
                if write_or:
                    print(information["query"]["pages"][page]["fullurl"])
                    write_or = False
                WebSurfer.check_page(information["query"]["pages"][page])

    @staticmethod
    def check_page(pageInfo):

        img_count = 0
        try:
            img_count = len(pageInfo["images"])
        except:
            img_count = 0
        if img_count > 0:
            WebSurfer.save_page_info(pageInfo["title"], img_count, pageInfo["fullurl"])

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
