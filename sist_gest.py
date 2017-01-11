# encoding=utf-8
from flask import Flask, render_template, request, url_for, redirect, session
from flaskext.mysql import MySQL
import hashlib

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123'
app.config['MYSQL_DATABASE_DB'] = 'don_bosco'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.secret_key = "Estodeberiaserandom"


@app.route('/', methods=['GET','POST'])
def index():
	error = None
	if request.method == 'POST':
		hashinput_user = hashlib.sha256(str(request.form['username']).encode('utf-8')).hexdigest() #Le hice encriptacion sha256
		hashinput_password = hashlib.sha256(str(request.form['password']).encode('utf-8')).hexdigest() #Le hice encriptacion sha256
		#Si entra un usuario comun
		print (hashinput_password)
		if ("b20b0f63ce2ed361e8845d6bf2e59811aaa06ec96bcdb92f9bc0c5a25e83c9a6" != hashinput_user) or ("a280f9c1266fc6a4aea482b8206f367bbd96a76a075140cd67ef4e92c01e3142" != hashinput_password) :
			error = "Usuario o contraseña erróneos. Por favor, intente de nuevo."
		else:
			session['logged_in'] = request.form['username']
			return redirect(url_for('seleccionar'))

	return render_template("index.html", err=error)

@app.route('/seleccion')
def seleccionar():
	if session.get('logged_in'):
		session.pop('logged_in',None)
		return render_template("ano_escolar.html")
	else:
		return redirect(url_for('index'))

# FALTA HACER UN ALERT PARA CONFIRMAR!
@app.route('/agregar', methods=['GET','POST'])
def agregar():
	if request.method == 'POST': 
		inicio = request.form['inicial']
		final = request.form['final']
		con = mysql.connect()
		cursor = con.cursor()
		if (inicio[0] == '2') and (inicio[1] == '0') and (final[0] == '2') and (final[1] == '0') and (len(final)==4) and (len(inicio)==4) and (final > inicio):
			cursor.execute("""INSERT INTO anos_escolares (inicial, final, eliminada) VALUES (%s, %s, '0')""", (inicio,final))
			con.commit()
			session['logged_in'] = "newform" 
			return redirect(url_for('seleccionar'))
		else:
			error="Año invalido"
			return render_template("agregar_ano.html", error=error)
	else:
		return render_template("agregar_ano.html")


@app.route('/estudiantes_ano')
def def_estudiantes():
	print("NET")
	return render_template("estudiantes.html")


# Al darle a seleccionar busco todos los anos y los mando al html
@app.route('/seleccionar')
def seleccion_ano():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from anos_escolares WHERE eliminada='0'")
	data = cursor.fetchall()
	return render_template("escoger_ano.html", datos=data)


@app.route('/eliminar')
def eliminar_ano():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from anos_escolares WHERE eliminada='0'")
	data = cursor.fetchall()
	return render_template("eliminar_ano.html", datos=data)	


@app.route('/eliminar_ano', methods=['POST'])
def eliminar_anos():
	real_id = request.form['real_id']
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("UPDATE anos_escolares SET eliminada = 1 WHERE ID=%s",(int(real_id)))
	conn.commit()
	return redirect(url_for('eliminar_ano'))


@app.route('/recuperar')
def recuperar_ano():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from anos_escolares WHERE eliminada='1'")
	data = cursor.fetchall()
	return render_template("recuperar_ano.html", datos=data)		

@app.route('/recuperar_ano', methods=['POST'])
def recuperar_anos():
	real_id = request.form['real_id']
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("UPDATE anos_escolares SET eliminada = 0 WHERE ID=%s",(int(real_id)))
	conn.commit()
	return redirect(url_for('recuperar_ano'))			


if __name__ == "__main__":
	app.run(debug=True, port=3000)