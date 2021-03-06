#Importamos as bibliotecas necessárias para manipular um banco MySQL.
import mysql.connector as msql
import pymysql
import pandas as pd
from mysql.connector import Error
from sqlalchemy import create_engine

#Configuração do banco de dados:
usuario = "root"
senha = "sql#123"

#Lemos os arquivos csv e os juntamos num único dataframe pandas.
print("Lendo os arquivos csv")
despesas = pd.read_csv("1T2020.csv", encoding = "ISO-8859-1", sep = ';')
despesas = pd.concat([despesas, pd.read_csv("2T2020.csv", encoding = "ISO-8859-1", sep = ';')])
despesas = pd.concat([despesas, pd.read_csv("3T2020.csv", encoding = "ISO-8859-1", sep = ';')])
despesas = pd.concat([despesas, pd.read_csv("4T2020.csv", encoding = "ISO-8859-1", sep = ';')])
despesas = pd.concat([despesas, pd.read_csv("1T2021.csv", encoding = "ISO-8859-1", sep = ';')])
despesas = pd.concat([despesas, pd.read_csv("2T2021.csv", encoding = "ISO-8859-1", sep = ';')])
despesas = pd.concat([despesas, pd.read_csv("3T2021.csv", encoding = "ISO-8859-1", sep = ';')])

#Transformamos a coluna VL_SALDO_FINAL de string para float.
despesas["VL_SALDO_FINAL"] = despesas["VL_SALDO_FINAL"].replace(',','.', regex = True)
despesas["VL_SALDO_FINAL"] = despesas["VL_SALDO_FINAL"].astype(float)

#Tentaremos nos conectar com o banco MySQL
try:
    conn = msql.connect(host="localhost", user=usuario, password=senha)

    #Caso tenhamos nos conectado ao MySQL com exito, criaremos um banco de dados de nome 'despesasDB'.
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE despesasDB")
        print("Banco de dados criado.")

#Caso não tenhamos conseguido nos conectar com o MySQL imprimimos na tela o erro.
except Error as e:
    print("Error while connecting to MySQL", e)

#Tentaremos nos conectar com o banco de dados com o nome de despesasDB.
try:
    conn = msql.connect(host="localhost", database="despesasDB", user=usuario, password=senha)

    #Caso tenhamos conseguido:
    if conn.is_connected():

        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("Você está conectado ao banco de dados: ", record)
        cursor.execute("DROP TABLE IF EXISTS despesas;")

        #Criaremos uma tabela dentro de despesasDB chamada despesas.
        print("Criando tabela...")
        cursor.execute("CREATE TABLE despesas (DATA CHAR(13),REG_ANS INT(30),CD_CONTA_CONTABIL INT(30),DESCRICAO VARCHAR(200),VL_SALDO_FINAL DECIMAL(20,2))")
        print("Tabela despesas foi criada.")

        #Com a tabela criada inserimos os dados do dataframe despesas nela.
        engine = create_engine("mysql+pymysql://{user}:{password}@localhost/{database}".format(user=usuario, password=senha, database="despesasDB"))
        print("Inserindo dados na tabela despesas...")
        despesas.to_sql("despesas", con = engine, if_exists = "replace", index=False)
        print("Dados inseridos.")
        

        #Query SQL para obtermos uma lista dos registros ANS das operadoras que mais tiveram despesas com 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' no último trimestre.
        sql = "SELECT REG_ANS, ROUND(SUM(VL_SALDO_FINAL),2) tot FROM despesas WHERE STR_TO_DATE(DATA, '%d/%m/%Y') >= '2021-07-01' AND DESCRICAO ='EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR ' GROUP BY REG_ANS, DESCRICAO ORDER BY tot DESC;"
        
        #Executamos a query.
        cursor.execute(sql)
        
        #Pegamos o resultado da query.
        result = cursor.fetchall()
        print()
        print("As 10 operadoras que mais tiveram despesas com 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' no último trimestre em ordem decrescente foram:")
        #Imprimimos o Registro ANS das 10 operadoras que mais tiveram despesas com a descrição requisitada em ordem decrescente.
        j = 1
        for i in result[:10]:
            print(str(j)+". Operadora com registro ANS: "+str(i[0]).zfill(6))
            j = j+1
            
        #Query SQL para obtermos uma lista dos registros ANS das operadoras que mais tiveram despesas com 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' no último ano.
        sql = "SELECT REG_ANS, ROUND(SUM(VL_SALDO_FINAL),2) tot FROM despesas WHERE STR_TO_DATE(DATA, '%d/%m/%Y') >= '2021-01-01' AND DESCRICAO ='EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR ' GROUP BY REG_ANS, DESCRICAO ORDER BY tot DESC;"

        #Executamos a query.
        cursor.execute(sql)
        
        #Pegamos o resultado da query.
        result = cursor.fetchall()
        print()
        print("As 10 operadoras que mais tiveram despesas com 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' no último ano em ordem decrescente foram:")
        #Imprimimos o Registro ANS das 10 operadoras que mais tiveram despesas com a descrição requisitada em ordem decrescente.
        j = 1
        for i in result[:10]:
            print(str(j)+". Operadora com registro ANS: "+str(i[0]).zfill(6))
            j = j + 1

        print()


except Error as e:
    print("Error while connecting to MySQL", e)
