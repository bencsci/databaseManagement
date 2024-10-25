from flask import Flask, render_template, request, redirect, url_for
import MySQLdb

app = Flask(__name__)

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'u0'
DB_NAME = 'u0'
DB_PASSWORD = ''

# App config
PORT = 18723 #provide a unique integer value instead of XXXX, e.g., PORT = 15657


def get_db_connection():
    conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# Show table based off a user input
@app.route('/show-tables', methods=['GET', 'POST'])
def show_tables():
    conn = get_db_connection()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        table_name = request.form['table'].strip()
        if table_name:  # Check if table_name is not empty
            cur.execute(f"SELECT * FROM {table_name.lower()}")
            data = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('show_tables.html', table_name=table_name, table_data=data)
        else:
            return render_template('show_tables.html', table_name=None, table_data=None)
    else:
        return render_template('show_tables.html', table_name=None, table_data=None)

#Add suppliers
@app.route('/add-supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            details = request.form
            # Check if _id already exists
            cur.execute("SELECT COUNT(*) FROM suppliers WHERE _id = %s", (details['id_'],))
            result = cur.fetchone()
            if result[0] > 0:
                return render_template('error.html', error=f"Supplier with id {details['id_']} already exists.")
            else:
                # Insert new supplier
                cur.execute("INSERT INTO suppliers(_id, name, email) VALUES (%s, %s, %s)", 
                            (details['id_'], details['name'], details['email']))
                conn.commit()
                cur.close()
                conn.close()
                return render_template('suppliers.html')
        except MySQLdb.Error as e:
            return render_template('error.html', error=str(e))
    else:
        return render_template('suppliers.html')

# Annual expenses for parts
@app.route('/annual-expenses', methods=['GET', 'POST'])
def annual_expenses():
    if request.method == 'POST':
        start_year = int(request.form['start_year'])
        end_year = int(request.form['end_year'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT YEAR(o.when_date) AS year, SUM(i.qty * p.price) AS total_expenses FROM orders o JOIN items i ON o.order_id = i.order_id JOIN parts p ON i.part_id = p._id WHERE YEAR(o.when_date) BETWEEN %s AND %s GROUP BY YEAR(o.when_date) ORDER BY YEAR(o.when_date)", (start_year, end_year))
        data = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('annual_expenses.html', start_year=start_year, end_year=end_year, expenses_data=data)
    else:
        return render_template('annual_expenses.html')

# Budget projection
@app.route('/budget-proj', methods=['GET', 'POST'])
def budget_projection():
    if request.method == 'POST':
        nYears = int(request.form['nYears'])
        inf_rate = float(request.form['inf_rate'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT YEAR(o.when_date) AS year, SUM(i.qty * p.price) AS total_expenses FROM orders o JOIN items i ON o.order_id = i.order_id JOIN parts p ON i.part_id = p._id WHERE YEAR(o.when_date) = (SELECT MAX(YEAR(when_date)) FROM orders) GROUP BY YEAR(o.when_date)")
        data = cur.fetchall()
        
        if data:
            # access the year of data
            year = int(data[0][0])

            # access the total_expenses of data
            total_expenses = int(data[0][1])
        else :
            year: None
            total_expenses: None

        futureData = {}
        for x in range(nYears):
            futureData[year + x + 1] = total_expenses * ((1 + inf_rate)**(x + 1))
    
        cur.close()
        conn.close()

        return render_template('budget_proj.html', year=year, nYears=nYears, total_expenses=total_expenses, futureData=futureData)
    else:
        return render_template('budget_proj.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
