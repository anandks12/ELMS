from flask import g
import sqlite3 
def connect_to_database():
    sql = sqlite3.connect('manager.db')
    sql.row_factory = sqlite3.Row
    return sql 
def get_database():
    if not hasattr(g, 'manager_db'):
        g.manager_db = connect_to_database()
    return g.manager_db


