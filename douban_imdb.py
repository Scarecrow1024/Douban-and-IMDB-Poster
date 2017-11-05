#-*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import qrcode
from PIL import Image, ImageDraw, ImageFont
import xlrd
import os
import gevent
import time
from gevent import monkey

monkey.patch_all()

def get_info(href):
    html = requests.get(href).text
    doc = pq(html)
    if doc.find("title").text() == '页面不存在':
        return False
    title = doc.find("span[property='v:itemreviewed']").text()
    #return title
    drat = doc.find('strong[property="v:average"]').text()
    year = doc.find('span[class="year"]').text()
    imdb_href = doc.find("span:contains('IMDb链接:')").next().attr('href')
    if imdb_href == None:
        return False
    imdb = requests.get(imdb_href).text
    imdb_doc = pq(imdb)
    irat = imdb_doc.find("span[itemprop='ratingValue']").text()
    #获取海报
    playbill = doc.find("a[class='nbgnbg']").attr('href')
    bill_info = requests.get(playbill).text
    doc_bill = pq(bill_info)
    first_bill = doc_bill.find("div[class='cover'] a").attr('href')
    first_bill_info = requests.get(first_bill).text
    doc_first_bill = pq(first_bill_info)
    bill = doc_first_bill.find("a[class='mainphoto'] img").attr('src')
    bill_img = requests.get(bill).content
    img_name = os.path.join("./douban_imdb/", title.replace(':', '-') + '.jpg')
    with open(img_name, 'wb') as pic:
        pic.write(bill_img)

    img_file = r'./douban_imdb/'+title.replace(':','-')+'_qrcode.jpg'
    img = qrcode.make(imdb_href)
    # 图片数据保存至本地文件
    img.save(img_file)
    #img.show()
    return {'title': title, 'drat': drat, 'year':year, 'irat':irat}

def mergeImg(href, route, comment):
    info = get_info(href)
    if info:
        # 打开电影海报
        moiveImg = Image.open('./douban_imdb/'+info['title'].replace(':','-')+'.jpg')
        # 打开二维码
        QrCodeImg = Image.open('./douban_imdb/' + info['title'].replace(':', '-') + '_qrcode.jpg')
        QrCodeImg = QrCodeImg.resize((200, 200), Image.ANTIALIAS)
        # 获取尺寸
        moiveImgSize = moiveImg.size
        moiveImg.convert("RGBA")

        if comment == " ":
            background = Image.open('./Canvas.jpg')
            metaBox = Image.open('./MetaBox.png')
            background.paste(metaBox, (2, 5, 855+2, 204))
            (x, y) = moiveImgSize
            r_y = y/x*855
            moiveImg = moiveImg.resize((855, int(r_y)), Image.ANTIALIAS)
            background.paste(moiveImg, (2, 210, 855+2, moiveImg.size[1]+210))
            background.paste(QrCodeImg, (650, 230, 850, 430))
            draw = ImageDraw.Draw(background)
            font = ImageFont.truetype(u"./MSYHBD.TTC", 35)
            font2 = ImageFont.truetype(u"./MSYHBD.TTC", 25)
            draw.text((20, 40), info['title'].replace(':','-'), (0, 0, 0), font=font)
            str = ''
            if len(route) > 50:
                str += route[0:50]+'\n'+route[50:]
            else:
                str += route
            draw.text((75, 150), str, (0, 0, 0), font=font2)
            draw.text((20, 80), info['year'], (0, 0, 0), font=font)
            draw.text((800, 18), info['irat'], (0, 0, 0), font=font)
            draw.text((800, 70), info['drat'], (0, 0, 0), font=font)
            del draw
        else:
            commentBg = Image.open('./CommentBox.png')
            background = Image.open('./Canvas_big.png')
            metaBox = Image.open('./MetaBox.png')
            background.paste(metaBox, (2, 5, 855+2, 204))
            background.paste(commentBg, (2, 205, commentBg.size[0]+2, commentBg.size[1]+205))
            (x, y) = moiveImgSize
            r_y = y/x*855
            moiveImg = moiveImg.resize((855, int(r_y)), Image.ANTIALIAS)
            background.paste(moiveImg, (2, 420, 855+2, moiveImg.size[1]+420))
            background.paste(QrCodeImg, (650, 450, 850, 650))
            draw = ImageDraw.Draw(background)
            font = ImageFont.truetype(u"./MSYHBD.TTC", 35)
            font2 = ImageFont.truetype(u"./MSYHBD.TTC", 25)
            draw.text((20, 40), info['title'].replace(':','-'), (0, 0, 0), font=font)
            str = ''
            if len(route) > 50:
                str += route[0:50]+'\n'+route[50:]
            else:
                str += route
            draw.text((75, 150), str, (0, 0, 0), font=font2)
            draw.text((20, 290), comment, (0, 0, 0), font=font)
            draw.text((20, 80), info['year'], (0, 0, 0), font=font)
            draw.text((800, 18), info['irat'], (0, 0, 0), font=font)
            draw.text((800, 70), info['drat'], (0, 0, 0), font=font)
            del draw
        background.save('./douban_imdb/img/' + info['title'].replace(':', '-') + '_merge.png')
        print(info['title'] + '===》海报生成成功')
        return True
    else:
        print(href+'链接失效或者不存在IMDB链接')
        return False

def main(href, route, comment):
    return mergeImg(href, route, comment)

if __name__ == '__main__':
    start = time.time()
    data = xlrd.open_workbook('movie.xlsx')
    table = data.sheets()[0]
    urls = table.col_values(0)
    routes = table.col_values(1)
    comment = table.col_values(2)
    comments = []
    for i in comment:
        if i == '':
            i = ' '
            comments.append(i)
        else:
            comments.append(i)

    list = []
    for k, url in enumerate(urls):
        list.append(gevent.spawn(main,url, routes[k], comments[k]))
    gevent.joinall(list)

    print("总用时："+str(time.time()-start)+"s")
