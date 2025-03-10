# Sistema de Historias Clínicas Electrónicas - GRUNECO

## Descripción
El **Sistema de Historias Clínicas Electrónicas (HCE) de GRUNECO** es una plataforma avanzada diseñada para la gestión eficiente y segura de la información médica de los pacientes dentro del marco de investigaciones clínicas y biomédicas. Permite almacenar, organizar y analizar datos de salud en un entorno digital, garantizando la trazabilidad, accesibilidad y confidencialidad de la información.

Este sistema es utilizado por el **Grupo de Investigación en Neuropsicología y Conducta (GRUNECO)** con fines investigativos, facilitando la recolección y gestión de datos médicos de pacientes en diversos estudios.

## Tecnologías Utilizadas
- **Django** (Framework web en Python)
- **MySQL** (Base de datos relacional)
- **Bootstrap** (Diseño responsivo)
- **HTML, CSS y JavaScript** (Interfaz de usuario)

## Requisitos de Instalación
Asegúrate de tener instalados los siguientes componentes en tu sistema:

1. **Python 3.11**
2. **pip** (Administrador de paquetes de Python)
3. **MySQL Server**
4. **Virtualenv** (Opcional, pero recomendado)

## Configuración del Entorno
Ejecuta los siguientes comandos en tu terminal para configurar el entorno y ejecutar el proyecto:

```bash
# Clonar el repositorio
$ git clone https://github.com/usuario/proyecto-hce.git
$ cd proyecto-hce

# Crear un entorno virtual (opcional pero recomendado)
$ python -m venv venv
$ source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
$ pip install -r requirements.txt

# Configurar la base de datos en settings.py
# Modifica la sección DATABASES con tus credenciales de MySQL

# Aplicar migraciones
$ python manage.py migrate

# Crear un superusuario para acceder al panel de administración
$ python manage.py createsuperuser

# Ejecutar el servidor
$ python manage.py runserver
```

## Configuración de la Base de Datos
Asegúrate de que MySQL Server esté en ejecución y crea una base de datos con el siguiente comando:
```sql
CREATE DATABASE gruneco_hce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Luego, edita el archivo `settings.py` en la sección `DATABASES` y agrega la configuración de la base de datos:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ateneagrunecodb',
        'USER': 'root',
        'PASSWORD': 'Tu_Contraseña,
        'HOST': 'localhost',  
        'PORT': '3306',  
    }
}
```

## Uso del Sistema
- Accede al sistema en [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Inicia sesión en el panel de administración en [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Características
- Registro y gestión de pacientes
- Almacenamiento seguro de historias clínicas
- Interfaz intuitiva y fácil de usar
- Generación de reportes y análisis de datos

## Contribución
Si deseas contribuir a este proyecto, sigue estos pasos:
1. Realiza un fork del repositorio
2. Crea una nueva rama con `git checkout -b feature-nueva`
3. Realiza tus cambios y haz commit con `git commit -m "Descripción del cambio"`
4. Sube los cambios con `git push origin feature-nueva`
5. Abre un pull request

## Contacto
Para más información, puedes contactarnos a **juan.restrepo183@udea.edu.co** o visitar nuestro sitio web [GRUNECO](https://www.gruneco.com.co).

---
Este proyecto es de uso exclusivo para investigación dentro del grupo GRUNECO y está sujeto a regulaciones éticas y de privacidad de datos.

