from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime, timedelta
import os
from gestor_tarea import GestorTareas

app = Flask(__name__)

app.secret_key = "clavececr3ta_xx23"

gestor = GestorTareas()

@app.route('/')
def sesion():
    return render_template('sesion.html')

@app.route('/log', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha = request.form.get('fecha')
        correo = request.form['correo']
        password = request.form['password']
        confirmPassword = request.form.get("confirmPassword")
        if password != confirmPassword:
            flash("Las contraseñas no coinciden", 'error')
            return render_template('log.html')
        usuario_id = gestor.crear_usuario(
            nombre=f"{nombre} {apellido}",
            email=correo,
            password=password
        )
        if not usuario_id:
            flash("Este correo ya está registrado", 'error')
            return render_template('log.html')
        flash(f"Registro exitoso: {nombre}. Ahora puedes iniciar sesión.", 'success')
        return redirect(url_for('sesion'))
    return render_template('log.html')

@app.route('/inicio')
def inicio():
    if not session.get('logueado'):
        return redirect(url_for('sesion'))
    return render_template('inicio.html')

@app.route('/contraseña')
def contraseña():
    return render_template('contraseña.html')
        
@app.route("/sesion")
def iniciar():
    if session.get('logueado'):
        return redirect(url_for('inicio'))
    return render_template('sesion.html')

@app.route('/validaLogin', methods=['GET','POST'])
def validar():
    if request.method == "POST":
        correo = request.form.get("correo", '').strip()
        password = request.form.get("password", '')
        if not correo or not password:
            flash('Por favor ingresa email y contraseña', 'error')
            return render_template('sesion.html')
        
        usuario = gestor.obtener_usuario2(correo, password)
        if usuario:
            session['logueado'] = True
            session['usuario'] = usuario['nombre']
            session['usuario_correo'] = correo
            flash(f'¡Bienvenido {usuario["nombre"]}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Correo o contraseña incorrecta', 'error')
            return render_template('sesion.html')
    
    return redirect(url_for('sesion'))

@app.route('/recuperar', methods=['GET','POST'])
def recuperar():
    if request.method == "POST":
        correo = request.form.get("correo", '').strip()
        if not correo:
            flash('Por favor ingrese su correo', 'error')
            return render_template('contraseña.html')
        usuario = gestor.usuarios.find_one({"email": correo})
        if usuario:
            flash('Se ha enviado un código para recuperar tu contraseña', 'success')
        else:
            flash('Este correo no está registrado', 'error')
            return render_template('contraseña.html')
        return render_template('sesion.html')
@app.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('sesion'))

# Ejemplo de uso
def ejemplo_uso():
    # Inicializar gestor
    gestor = GestorTareas()
    
    # Crear usuario
    usuario_id = gestor.crear_usuario("Ana García", "ana@email.com")
    print(f"Usuario creado con ID: {usuario_id}")
    
    if usuario_id:
        # Crear tareas
        tarea1 = gestor.crear_tarea(
            usuario_id, 
            "Aprender MongoDB", 
            "Completar tutorial de PyMongo",
            datetime.now() + timedelta(days=3)
        )
        print(f"Tarea creada: {tarea1}")
        
        tarea2 = gestor.crear_tarea(
            usuario_id,
            "Hacer ejercicio",
            "Ir al gimnasio 3 veces esta semana"
        )
        
        # Agregar etiqueta
        gestor.agregar_etiqueta(tarea1, "programación")
        gestor.agregar_etiqueta(tarea1, "estudio")
        
        # Listar tareas
        tareas = gestor.obtener_tareas_usuario(usuario_id)
        print(f"\nTareas de {usuario_id}:")
        for t in tareas:
            print(f"  - {t['titulo']} [{t['estado']}]")
        
        # Actualizar estado
        gestor.actualizar_estado_tarea(tarea1, "en_progreso")
        
        # Estadísticas
        stats = gestor.estadisticas_usuario(usuario_id)
        print(f"\nEstadísticas: {stats}")
        
        # Tareas urgentes
        urgentes = gestor.tareas_urgentes(72)
        print(f"\nTareas urgentes próximos 3 días: {len(urgentes)}")
    
    # Cerrar conexión
    gestor.cerrar_conexion()

if __name__ == '__main__':
    app.run(debug=True)