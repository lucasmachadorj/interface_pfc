========================================
                  README
========================================

## Instalação da interface

### Pré-requisitos

- python v2.7

### Procedimento de instalação

- instalar o gerenciador de pacotes python:
  - sudo apt-get install python-pip python-dev libpq-dev build-essential
  - sudo pip install --upgrade pip

- instalar os pacotes flask, sqlalchemy, psycopg2, paramiko e pandas
   - sudo pip install Flask
   - sudo pip install SQLAlchemy
   - pip install psycopg2
   - pip install paramiko
   - pip install pandas

 - O diretório classifier que contém os executáveis preprocessor e classifier deve
 ser colocado no caminho /etc.

### Execução

A partir do diretório /interface, executar o comando: ./flaskr.py

Após isso, a interface estará rodando no endereço localhost:5000
