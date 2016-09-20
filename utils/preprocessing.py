import os
import pandas as pd
import psycopg2
import paramiko

def save_netflow():
    for filename in os.listdir("./netflow/"):
        if filename.endswith('.binetflow'):
            name = filename.split('.')
            name = name[0]
            name = name + '.csv'
            os.rename(os.path.join('./netflow/',filename), os.path.join('./netflow/',name))
            fname = name

    data = pd.read_csv(os.path.join('./netflow/',fname))
    del data['Label']
    data.to_csv('./netflow/{}'.format(fname), header=None, index=None)

    try:
        conn = psycopg2.connect(host='192.168.0.26', port='5432',user="postgres", password='mec050710', dbname='testdb')
    except:
        print 'Falha ao se conectar com o banco'

    cur = conn.cursor()
    f = open('{}'.format(os.path.join('./netflow/',fname)), 'r')
    f.seek(0)
    cur.copy_from(f, 'netflow', sep=',')
    conn.commit()
    os.remove(os.path.join('./netflow/', fname))

def preprocessor():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.0.26', port=7777, username='machado', password='lucas')
    stdin, stdout, stderr = ssh.exec_command('cd /home/cristopher/pfc/classifier; ./preprocessor bothunter.conf; ./classifier bothunter.conf;')
    # stdin, stdout, stderr = ssh.exec_command('ls')
    print stdout.readlines()
