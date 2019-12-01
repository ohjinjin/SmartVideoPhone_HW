import sys
from PIL import Image
import requests
from io import BytesIO

import pymysql.cursors

 
conn = pymysql.connect(host='192.168.219.106',
        user='root',
        password='1234',
        db='smartvideophone',
        charset='utf8mb4')
response = requests.get("http://192.168.219.104:8090/?action=snapshot")
img = Image.open(BytesIO(response.content))
#image = Image.open("C:\\Users\\Oh\\Desktop\\images.jpg")
blob_value = BytesIO(response.content).getvalue()
try:
    with conn.cursor() as cursor:
        sql = 'INSERT INTO visit_log (image) VALUES (%s)'
        cursor.execute(sql, (blob_value,))
    conn.commit()
    print(cursor.lastrowid)
    # 1 (last insert id)
finally:
    conn.close()
