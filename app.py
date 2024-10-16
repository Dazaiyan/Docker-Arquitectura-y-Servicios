from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del archivo .env

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')

# Configuración de MySQL
app.config['MYSQL_HOST'] = getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = getenv('MYSQL_DB')

mysql = MySQL(app)

# Ruta de inicio
@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Inicio de sesión de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        password = user_details['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Usuarios WHERE username = %s", [username])
        user = cur.fetchone()
        cur.close()
        
        if user and user[2] == password:  # Compara la contraseña en texto plano
            session['loggedin'] = True
            session['username'] = user[1]
            return redirect(url_for('dashboard'))  # Cambia esto si tu ruta es diferente
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Proyectos")
        proyectos = cur.fetchall()
        cur.close()
        return render_template('dashboard.html', proyectos=proyectos)
    return redirect(url_for('login'))

# Gestión de Proyectos
@app.route('/proyectos')
def proyectos():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Proyectos")
        proyectos = cur.fetchall()
        cur.close()
        return render_template('proyectos.html', proyectos=proyectos)
    return redirect(url_for('login'))

@app.route('/proyectos/nuevo', methods=['GET', 'POST'])
def nuevo_proyecto():
    if 'loggedin' in session:
        if request.method == 'POST':
            proyecto_details = request.form
            nombre = proyecto_details['nombre']
            descripcion = proyecto_details['descripcion']
            fecha_inicio = proyecto_details['fecha_inicio']
            fecha_fin = proyecto_details['fecha_fin']
            estado = proyecto_details['estado']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Proyectos(nombre, descripcion, fecha_inicio, fecha_fin, estado) VALUES(%s, %s, %s, %s, %s)", (nombre, descripcion, fecha_inicio, fecha_fin, estado))
            mysql.connection.commit()
            cur.close()
            flash('Proyecto Agregado Satisfactoriamente', 'success')
            return redirect(url_for('proyectos'))
        return render_template('nuevo_proyecto.html')
    return redirect(url_for('login'))

@app.route('/proyectos/editar/<int:id>', methods=['GET', 'POST'])
def editar_proyecto(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Proyectos WHERE id = %s", [id])
        proyecto = cur.fetchone()

        if request.method == 'POST':
            proyecto_details = request.form
            nombre = proyecto_details['nombre']
            descripcion = proyecto_details['descripcion']
            fecha_inicio = proyecto_details['fecha_inicio']
            fecha_fin = proyecto_details['fecha_fin']
            estado = proyecto_details['estado']

            cur.execute("""
                UPDATE Proyectos
                SET nombre = %s, descripcion = %s, fecha_inicio = %s, fecha_fin = %s, estado = %s
                WHERE id = %s
            """, (nombre, descripcion, fecha_inicio, fecha_fin, estado, id))
            mysql.connection.commit()
            cur.close()
            flash('Proyecto Actualizado Satisfactoriamente', 'success')
            return redirect(url_for('proyectos'))

        return render_template('editar_proyecto.html', proyecto=proyecto)
    return redirect(url_for('login'))

@app.route('/proyectos/eliminar/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Proyectos WHERE id = %s", [id])
        mysql.connection.commit()
        cur.close()
        flash('Proyecto Eliminado Satisfactoriamente', 'success')
        return redirect(url_for('proyectos'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
