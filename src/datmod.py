import sqlite3

class Dam():
    def __init__(mod, create_time, alert_time, title, email, ticket, ceiling, floor, price):
        mod.create_time = create_time
        mod.alert_time = alert_time
        mod.title = title
        mod.email = email
        mod.ticket = ticket
        mod.ceiling = ceiling
        mod.floor = floor
        mod.price = price

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_alerts_with_ticket(title_g, ticket_g):
    alerts = [] #list of data models
    conn = get_db_connection()
    results = conn.execute('SELECT p.created, a.alert_time, p.title, p.email, p.ticket, p.ceilings, p.floors, a.price \
    FROM alerts a JOIN posts p on p.title = a.title AND p.ticket = a.ticket WHERE a.title = ? and a.ticket = ?', (title_g, ticket_g)).fetchall()
    for row in results:
        create_time = row[0]
        alert_time = row[1]
        title = row[2]
        email = row[3]
        ticket = row[4]
        ceiling = row[5]
        floor = row[6]
        price = row[7]
        data_model = Dam(create_time, alert_time, title, email, ticket, ceiling, floor, price)
        alerts.append(data_model)
#     print(f"Create Time: {data_model.create_time}, Alert Time: {data_model.alert_time}, Title: {data_model.title}, Email: {data_model.email}, Ticket: {data_model.ticket}, \
# Ceiling: {data_model.ceiling}, Floor: {data_model.floor}, Price: {data_model.price}")
    return alerts

def get_alerts_with_title(title_g):
    alerts = [] #list of data models
    conn = get_db_connection()
    results = conn.execute('SELECT p.created, a.alert_time, p.title, p.email, p.ticket, p.ceilings, p.floors, a.price \
    FROM alerts a JOIN posts p on p.title = a.title AND p.ticket = a.ticket WHERE a.title = ?', ([title_g])).fetchall()
    for row in results:
        create_time = row[0]
        alert_time = row[1]
        title = row[2]
        email = row[3]
        ticket = row[4]
        ceiling = row[5]
        floor = row[6]
        price = row[7]
        data_model = Dam(create_time, alert_time, title, email, ticket, ceiling, floor, price)
        alerts.append(data_model)
#         print(f"Create Time: {data_model.create_time}, Alert Time: {data_model.alert_time}, Title: {data_model.title}, Email: {data_model.email}, Ticket: {data_model.ticket}, \
# Ceiling: {data_model.ceiling}, Floor: {data_model.floor}, Price: {data_model.price}")
    return alerts

#get_alerts_with_ticket('Alerticus', 'ADBE')
#get_alerts_with_title('Alerticus')