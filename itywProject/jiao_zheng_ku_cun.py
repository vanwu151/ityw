import pymysql

conn = pymysql.connect(
    host='172.18.99.183',
    port=3307,
    user='root',
    passwd='19**abAB',
    db='ityw',
)

cur = conn.cursor()
item_kind_list = []
item_location_list = []
try:
    cur.execute(
    "SELECT * FROM ITYW_itemstock WHERE item_stock_num <> 0 OR item_destory_num <> 0;"
)
    # print('Count:', cur.rowcount)
    row = cur.fetchone()
    while row:
        # print(row[1])
        item_kind_list.append(row[1])
        item_location_list.append(row[3])
        # print(row[3])
        row = cur.fetchone()
except Exception as e:
    print('Error:', e)

item_stock_info_list = zip(item_kind_list, item_location_list)
for item_kind, item_location in item_stock_info_list:
    # print(item_kind, item_location)
    cur.execute(
    "SELECT count(*) FROM ITYW_iteminfo WHERE item_kind = '{}' AND item_statu = '报废' AND item_location = '{}';".format(item_kind, item_location)
)
    des_num = cur.fetchone()[0]
    # print('des_num', item_kind, item_location, des_num)
    cur.execute(
    "SELECT count(*) FROM ITYW_iteminfo WHERE item_kind = '{}' AND item_statu = '闲置' AND item_location = '{}';".format(item_kind, item_location)
)
    free_num = cur.fetchone()[0]
    # print('free_num', item_kind, item_location, free_num)
    cur.execute(
    "UPDATE ITYW_itemstock SET item_destory_num = {}, item_stock_num = {} WHERE item_kind = '{}' AND item_stock_location = '{}';".format(des_num, free_num, item_kind, item_location)
)
# print('报损数:',des_num,'闲置数:', free_num, item_kind, item_location)

conn.commit()
cur.close()
conn.close()