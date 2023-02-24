from glob import glob
import os;
import sqlite3;
import time;
import requests;
import subprocess;
import threading;
import schedule;
_db_address = '/etc/x-ui-english/x-ui-english.db'
_max_allowed_connections = 0
_user_last_id = 0
_telegrambot_token = '5087116886:AAHJn3aktKodUAlUJuLU8rbjXO3fYPFqa6Y'
_telegram_chat_id = '1667734198' # you can get this in @cid_bot bot.
def getUsers():
    global _user_last_id
    global users_list
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select id,remark,port from inbounds where id > {_user_last_id}");
    users_list = [];
    for c in cursor:
        users_list.append({'name':c[1],'port':c[2]})
        _user_last_id = c[0];
    conn.close();
    return users_list
    
def checkNewUsers():
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select count(*) from inbounds WHERE id > {_user_last_id}");
    new_counts = cursor.fetchone()[0];
    conn.close();
    if new_counts > 0:
        init()

def init():
    users_list = getUsers();
    for user in users_list:
        thread = AccessChecker(user)
        thread.start()
        print("starting checker for : " + user['name'])
class AccessChecker(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user;
    def run(self):
        #global _max_allowed_connections; <<if you get variable error uncomment this.
        user_remark = self.user['name'];
        user_port = self.user['port'];
        while True:
            netstate_data =  os.popen("netstat -np 2>/dev/null | grep :"+str(user_port)+" | awk '{if($3!=0) print $5;}' | cut -d: -f1 | sort | uniq -c | sort -nr | head").read();
            netstate_data = str(netstate_data)
            connection_count =  len(netstate_data.split("\n")) - 1;
            print("c "+str(user_port) + "-"+ str(connection_count))
            if connection_count > _max_allowed_connections:
                requests.get(f'https://api.telegram.org/bot{_telegrambot_token}/sendMessage?chat_id={_telegram_chat_id}&text={user_port}%20%7c%20connection%3d{connection_count}&20%7c%20UserPort%3d{user_port}')
            print(f"inbound with port {user_port} connection {connection_count}")
            time.sleep(1800)
            #else:
            
init()
while True:
    schedule.run_pending()
    schedule.every(2).minutes.do(init)
    schedule.every(2).minutes.do(checkNewUsers)
    time.sleep(36000)

