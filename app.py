from flask import Flask, render_template, request, redirect, flash, url_for, session
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__) # Creating our Flask Instance
app.secret_key ="gizi"

# mysql config
app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12594574'
app.config['MYSQL_PASSWORD'] = 'mXns4f3zdK'
app.config['MYSQL_DB'] = 'sql12594574'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('antro'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('antro'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/database')
def antro():
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM antro''')
    antro = cursor.fetchall()
    cursor.close()

    return render_template('database.html', antro=antro)

@app.route('/database/hasil')
def hasil():
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM antro''')
    antro = cursor.fetchall()
    cursor.close()

    return render_template('database_hasil.html', antro=antro)

@app.route('/database/delete/<int:id>', methods=['GET'])
def deletepasien(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM antro 
        WHERE id=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()
        flash('pasien deleted','success')
        return redirect(url_for('antro'))

    return render_template('database.html')

@app.route('/database/tambah', methods=['GET'])
def tambah():

    return render_template("index.html")


@app.route('/database/tambah/operation_result/', methods=['POST'])
def operation_result():
    """Route where we send calculator form input"""
    
    error = None
    result = None



    # request.form looks for:
    # html tags with matching "name= "
    jk_a = request.form['jk']  
    age_a = request.form['age']
    pb_a = request.form['pb']
    bb_a = request.form['bb']
    lingkar_a = request.form['lingkar']
    Lila_a = request.form['Lila']

    try:
        jk = jk_a
        age_int = int(age_a) + 1
        pb_int = float(pb_a)
        bb_int = float(bb_a)
        lingkar_int = float(lingkar_a)
        Lila_int = float(Lila_a)
        
        #fungsi PB fro Age------------------------------------------------------------------------------------------------------
        median_pb = "pb_for_age.xlsx"
        df_median_pb = pd.read_excel(median_pb, sheet_name=jk ,usecols="C", nrows=age_int)
        last_item_pb = df_median_pb.to_numpy()
        data_median_pb = last_item_pb[-1]

        df_sd_pb = pd.read_excel(median_pb, sheet_name=jk ,usecols="J", nrows=age_int)
        last_item_pb = df_sd_pb.to_numpy()
        data_sd_pb = last_item_pb[-1]

        df_sdneg_pb = pd.read_excel(median_pb, sheet_name=jk ,usecols="H", nrows=age_int)
        last_item_pb = df_sdneg_pb.to_numpy()
        data_sdneg_pb = last_item_pb[-1]


        if pb_int<data_median_pb:
            zScore_pb = (pb_int-data_median_pb)/(data_median_pb-data_sdneg_pb)
        else :
            zScore_pb = (pb_int-data_median_pb)/(data_sd_pb-data_median_pb)
    
        if zScore_pb<-3:
            kondisi_pb = "Sangat Pendek (Severely Stunted)"
        elif -3<=zScore_pb<-2:
            kondisi_pb = "Pendek (Stunted)"
        elif -2<=zScore_pb<3:
            kondisi_pb = "Normal"
        else :
            kondisi_pb ="Tinggi"
        #-----------------------------------------------------------------------------------------------------------
        
        #fungsi BB for Age-----------------------------------------------------------------------------------------------------------------
        median_bb = "bb_for_age.xlsx"
        df_median_bb = pd.read_excel(median_bb, sheet_name=jk ,usecols="C", nrows=age_int)
        last_item_bb = df_median_bb.to_numpy()
        data_median_bb = last_item_bb[-1]

        sd_bb = "bb_for_age.xlsx"
        df_sd_bb = pd.read_excel(median_bb, sheet_name=jk ,usecols="I", nrows=age_int)
        last_item_bb = df_sd_bb.to_numpy()
        data_sd_bb = last_item_bb[-1]

        sdneg_bb = "bb_for_age.xlsx"
        df_sdneg_bb = pd.read_excel(median_bb, sheet_name=jk ,usecols="G", nrows=age_int)
        last_item_bb = df_sdneg_bb.to_numpy()
        data_sdneg_bb = last_item_bb[-1]


        if bb_int<data_median_bb:
            zScore_bb = (bb_int-data_median_bb)/(data_median_bb-data_sdneg_bb)
        else :
            zScore_bb = (bb_int-data_median_bb)/(data_sd_bb-data_median_bb)
            
        if zScore_bb<-3:
            kondisi_bb = "Sangat Badan Sangat Kurang (Severely Underweight)"
        elif -3<=zScore_bb<-2:
            kondisi_bb = "Berat Badan Kurang (Underweight)"
        elif -2<=zScore_bb<1:
            kondisi_bb = "Berat Badan Normal"
        else :
            kondisi_bb ="Resiko berat badan lebih"
        #------------------------------------------------------------------------------------------------------------------------------------------------------------
        #fungsi BB for PB------------------------------------------------------------------------------------------------------------------
        median = "bb_for_pb.xlsx"
        df_median = pd.read_excel(median, sheet_name=jk ,usecols="A,C")
        df = df_median.set_index('LENGTH')
        data_index = df.loc[pb_int]
        data_median = data_index.to_numpy()

        sd = "bb_for_pb.xlsx"
        df_sd = pd.read_excel(sd, sheet_name=jk ,usecols="A,I")
        df = df_sd.set_index('LENGTH')
        data_index = df.loc[pb_int]
        data_sd = data_index.to_numpy()

        sdneg = "bb_for_pb.xlsx"
        df_sdneg = pd.read_excel(sd, sheet_name=jk ,usecols="A,I")
        df = df_sdneg.set_index('LENGTH')
        data_index = df.loc[pb_int]
        data_sdneg = data_index.to_numpy()


        if bb_int<data_median:
            zScore = (bb_int-data_median)/(data_median-data_sdneg)
        else :
            zScore = (bb_int-data_median)/(data_sd-data_median)
            
        if zScore<-3:
            kondisi = "Gizi Buruk"
        elif -3<=zScore<-2:
            kondisi = "Gizi Kurang"
        elif -2<=zScore<1:
            kondisi = "Gizi Baik (Normal)"
        elif 1<zScore<=2:
            kondisi = "Beresiko Gizi Lebih"
        elif 2<zScore<=3:
            kondisi = "Gizi Lebih"
        else :
            kondisi ="Obesitas"


        #-------------------------------------------------------------------------------------------------------

        #Fungsi Lila---------------------------------------------------
        if Lila_int < 11.5 :
            kondisi_Lila = "Gizi Buruk"
        elif 11.5 <= Lila_int < 12.4 :
            kondisi_Lila = "Gizi Kurang"
        else :
            kondisi_Lila = "Gizi Baik"
        
        #fungsi lingkar Kepala-------------------------------------------------------------
        median_lingkar = "pb_for_age.xlsx"
        df_median_lingkar = pd.read_excel(median_lingkar, sheet_name=jk ,usecols="C", nrows=age_int)
        last_item_lingkar = df_median_lingkar.to_numpy()
        data_median_lingkar = last_item_lingkar[-1]

        sd_lingkar = "pb_for_age.xlsx"
        df_sd_lingkar = pd.read_excel(median_lingkar, sheet_name=jk ,usecols="J", nrows=age_int)
        last_item_lingkar = df_sd_lingkar.to_numpy()
        data_sd_lingkar = last_item_lingkar[-1]

        sdneg_lingkar = "pb_for_age.xlsx"
        df_sdneg_lingkar = pd.read_excel(median_lingkar, sheet_name=jk ,usecols="H", nrows=age_int)
        last_item_lingkar = df_sdneg_lingkar.to_numpy()
        data_sdneg_lingkar = last_item_lingkar[-1]


        if pb_int<data_median_lingkar:
            zScore_lingkar = (lingkar_int-data_median_lingkar)/(data_median_lingkar-data_sdneg_lingkar)
        else :
            zScore_lingkar = (lingkar_int-data_median_lingkar)/(data_sd_lingkar-data_median_lingkar)
            
        if zScore_lingkar<-3:
            kondisi_lingkar = "Sangat kecil"
        elif -3<=zScore_lingkar<-2:
            kondisi_lingkar = "Kecil"
        elif -2<=zScore_lingkar<=2:
            kondisi_lingkar = "Normal"
        else :
            kondisi_lingkar ="Sangat Besar"

        nama = request.form['nama']
        usia = request.form['age']
        jenis_k = request.form['jk']
        panjang_b = request.form['pb']
        berat_b = request.form['bb']
        kepala = request.form['lingkar']
        Lila = request.form['Lila']
            
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO antro(nama,usia,jenis_k,panjang_b,berat_b,kepala,Lila,zScore_pb,kondisi_pb,zScore_bb,kondisi_bb,zScore,kondisi,zScore_lingkar,kondisi_lingkar,kondisi_Lila) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(nama,usia,jenis_k,panjang_b,berat_b,kepala,Lila,zScore_pb,kondisi_pb,zScore_bb,kondisi_bb,zScore,kondisi,zScore_lingkar,kondisi_lingkar,kondisi_Lila))
        mysql.connection.commit()
        cursor.close()
        #flash('Data added successfully','success')
        #return redirect(url_for('database'))

        return render_template(
            'results.html',
            kondisi_pb=kondisi_pb,
            kondisi_bb=kondisi_bb,
            kondisi=kondisi,
            kondisi_Lila=kondisi_Lila,
            kondisi_lingkar=kondisi_lingkar,
            zScore_pb=zScore_pb,
            zScore_bb=zScore_bb,
            zScore=zScore,
            zScore_lingkar=zScore_lingkar,
            calculation_success=True
        )
        
    except ZeroDivisionError:
        return render_template(
            'index.html',
            calculation_success=False,
            error="You cannot divide by zero"
        )
        
    except ValueError:
        return render_template(
            'index.html',
            calculation_success=False,
            error="Cannot perform numeric operations with provided input"
        )


if __name__ == '__main__': app.run(debug=True)
