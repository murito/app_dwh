# app_dwh
Aplicación para gestión de reportes para datawarehouse

# Software requerido
bower https://bower.io/#install-bower

# Instalción

Primero clonamos el repositorio en la carpeta local

`git clone https://github.com/murito/app_dwh.git .`

luego instalamos las dependencias estáticas

`bower install`

# Creando el entorno virtual

Necesitamos crear el entorno virtual para ejecutar el proyecto con un Django separado para el proyecto

`mkvirtualenv project_name`

Eso creará el nuevo entorno virtual e iniciará a trabajar dentro del mismo, eso lo sabemos por que el prompt cambia:

de `usuario$` a `(project_name)usuario$`

# Configuraciones Iniciales

Deben tener ya creada la base de datos, de otro modo habría que hacer las migraciones de los modelos creados en el código

Es necesario configurar en `datawarehouse/settings.py` el acceso a la base de datos

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nombre_de_su_base_de_datos_local',
        'USER': 'usuario_de_su_base_de_datos',
        'PASSWORD': 'password_de_su_base_de_datos',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```


# Dependencias

Necesitamos instalar las dependencias del projecto para eso usamos el  `pip`

`pip install django  mysqlclient`

Una vez que tenemos todo esto ya podemos ejecutar el servidor de desarrollo de django

`./manage.py runserver`


y accedemos a la ruta `http://localhost:8000`
