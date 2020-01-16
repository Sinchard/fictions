import pymysql
from DBUtils.PooledDB import PooledDB

from fictions.settings import MYSQL_HOST, MYSQL_DB, MYSQL_CHARSET, MYSQL_USER, \
                MYSQL_PASSWD, MYSQL_PORT

pool = PooledDB(creator=pymysql, maxcached=10, maxshared=10, host=MYSQL_HOST,
                user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_DB, port=MYSQL_PORT,
                charset=MYSQL_CHARSET, setsession=['SET AUTOCOMMIT = 1'])


