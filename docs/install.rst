Instalación local
=================

Spatialite (macOS)
------------------

Instalar Spatialite con brew en macOS::

    brew update
    brew install spatialite-tools
    brew install gdal

Cliente Oracle (macOS)
----------------------

Descargar desde `Oracle <http://www.oracle.com/technetwork/topics/intel-macsoft-096467.html>`_

- instantclient-basic-macos.x64-12.1.0.2.0.zip
- instantclient-sdk-macos.x64-12.1.0.2.0.zip

Crear un directorio ``/usr/local/lib/oracle``::

    export ORACLE_HOME=/usr/local/lib/oracle
    export VERSION=12.1.0.2.0
    export ARCH=x86_64

    mkdir -p $ORACLE_HOME


Descomprimir los dos ficheros y crear los enlaces simbólicos::

    cd $ORACLE_HOME
    tar -xzf instantclient-basic-12.1.0.2.0-macosx-x64.zip
    tar -xzf instantclient-sdk-12.1.0.2.0-macosx-x64.zip
    mv instantclient_12_1/* $ORACLE_HOME
    rmdir instantclient_12_1

    cd /usr/local/lib/
    ln -s $ORACLE_HOME/libclntsh.dylib.12.1 libclntsh.dylib.12.1
    ln -s $ORACLE_HOME/libclntsh.dylib.12.1 libclntsh.dylib
    ln -s $ORACLE_HOME/libocci.dylib.12.1 libocci.dylib.12.1
    ln -s $ORACLE_HOME/libnnz12.dylib libnnz12.dylib


Instalar ``cx_Oracle`` desde PIP::

    env ARCHFLAGS="-arch $ARCH" pip install cx-Oracle==5.2.1

Configuración del proyecto
--------------------------

La configuración del proyecto se realiza mediante el uso de variables de entorno. Se pueden declarar en
varios lugares, pero se recomienda crear el fichero ``.env`` en la carpeta raíz del código fuente.

.. code-block:: bash

    # Poli Car project environment variables
    # ------------------------------------------------------------------------------

    ORACLE_SID=ZETATEST

    DJANGO_SETTINGS_MODULE=config.settings.production
    DJANGO_ALLOWED_HOSTS=carsdes.cc.upv.es
    DJANGO_SECRET_KEY=someseed
    DATABASE_URL=oraclegis://{username}:{password}@{host}:{port}/{database}
    DJANGO_DEBUG=False

    UPV_LOGIN_DATA_USERNAME=carshare
    UPV_LOGIN_DATA_PASSWORD=SW2017-03:dLogin<b

.. glossary::

    ORACLE_SID
        Valor del SID de la base de datos de Oracle.

    DJANGO_SETTINGS_MODULE
        Ruta del módulo de settings que usará el proyecto. Para producción debe de estar siempre
        establecido ``config.settings.production`` como valor.

    DJANGO_ALLOWED_HOSTS
        Dominio desde el que se permitirán las peticiones. Si se intenta acceder con otro nombre, la
        aplicación responderá con un error 400.

    DJANGO_SECRET_KEY
        Semilla que se usa para guardar de forma segura las contraseñas en la base de datos.

    DATABASE_URL
        Credenciales y ruta para acceder a la base de datos. Siempre será de la siguiente forma:
        ``oraclegis://{username}:{password}@{host}:{port}/{database}``, donde ``{username}`` es el nombre de
        usuario de base de datos, ``{password}`` es la contraseña de ese usuario, ``{host}`` es la ruta del servidor,
        ``{port}`` es el puerto y ``{database}`` es el nombre de la base de datos.

    DJANGO_DEBUG
        Activa o desactiva el modo de depuración de la aplicación. Se usa ``True`` para activar y ``False`` para
        desactivar.

    UPV_LOGIN_DATA_USERNAME
        Nombre de usuario para acceder al servicio de login de la UPV.

    UPV_LOGIN_DATA_PASSWORD
        Contraseña para acceder al servicio de login de la UPV.

Ejecutar tests
--------------

Para ejecutar los test usando Docker::

    $ docker-compose -f dev.yml run app python3 manage.py test --settings=config.settings.test

