import os
import pandas as pd
import psycopg2
import paramiko

def save_netflow(hostname, port, user, password, dbname ):
    for filename in os.listdir("./netflow/"):
        if filename.endswith('.binetflow'):
            name = filename.split('.')
            name = name[0]
            name = name + '.csv'
            os.rename(os.path.join('./netflow/',filename), os.path.join('./netflow/',name))
            fname = name

    data = pd.read_csv(os.path.join('./netflow/',fname))
    if data['Label']:
        del data['Label']

    data.to_csv('./netflow/{}'.format(fname), header=None, index=None)
    try:
        conn = psycopg2.connect(host=hostname, port=port, user=user, password=password, dbname=dbname)
    except:
        print 'Falha ao se conectar com o banco'
        os.remove(os.path.join('./netflow/', fname))

    cur = conn.cursor()
    f = open('{}'.format(os.path.join('./netflow/',fname)), 'r')
    f.seek(0)
    cur.copy_from(f, 'netflow', sep=',')
    conn.commit()
    os.remove(os.path.join('./netflow/', fname))

def preprocessor(hostname, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, int(port), username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command('cd /etc/classifier; ./preprocessor bothunter.conf; ./classifier bothunter.conf;')
