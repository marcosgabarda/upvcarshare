Despliegue en CentOS
====================

Instrucciones para la instalación de poliCar en un servidor **CentOS 7.2**.

Dependencias de yum
-------------------

.. code-block:: console

    $ sudo yum install libjpeg-devel zlib-devel gcc python-devel libcap-devel supervisor gdal \
    gdal-devel yum-utils

Instalar Python 3
-----------------

El proyecto requiere de **Python 3** para funcionar. Se puede instalar usando las fuentes,
siguiendo estos pasos:

.. code-block:: console

    $ sudo yum-builddep python
    $ wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
    $ tar xf Python-3.5.2.tgz
    $ cd Python-3.5.2
    $ ./configure
    $ make
    $ sudo make install


Instalar Node
-------------

Para la gestión de los ficheros estáticos se necesita tener instalado **Node**. Para instalarlo desde
el código fuente, basta seguir los siguientes pasos:

.. code-block:: console

    $ wget https://nodejs.org/dist/v6.9.1/node-v6.9.1.tar.gz
    $ tar xvzf node-v6.9.1.tar.gz
    $ cd node-v6.9.1
    $ ./configure
    $ make
    $ sudo make install


Instalar virtualenv
--------------------

Para instalar las dependencias de Python, se recomienda usan un entorno virtual en vez de instalarlas
directamente en el sistema. Para crear el entorno virtual y facilitar la gestión de este, se recomienda
instalar y configurar ``virtualenvwrapper``.

.. code-block:: console

    $ sudo pip install virtualenv virtualenvwrapper

Hay que añadir lo siguiente al fichero ``.bashrc`` del usuario que se vaya a usar para instalar el proyecto, **no**
en el de root.

.. code-block:: bash

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/bin/virtualenvwrapper.sh

Para que los cambios tengan efecto, recargamos el fichero ``.bashrc``:

.. code-block:: console

    $ source ~/.bashrc

Instalar proyecto
-----------------

Para instalar el proyecto, primero creamos su entorno virtual:

.. code-block:: console

    $ mkvirtualenv --python=/usr/local/bin/python3 carshare

Luego, clonamos el código fuente del proyecto:

.. code-block:: console

    (carshare) $ git clone git@git.upv.es:GIT_CARSHARE/carshare-project.git
    (carshare) $ cd carshare-project

Luego, instalamos las dependencias de Python:

.. code-block:: console

    (carshare) $ pip install -r requirements/production.txt

Y por último, las dependencias de Javascript:

.. code-block:: console

    (carshare) $ npm install


Configuración del proyecto
--------------------------

La configuración del proyecto se realiza mediante el uso de variables de entorno. Se pueden declarar en
varios lugares, pero se recomienda crear el fichero ``.env`` en la carpeta raíz del código fuente.

.. code-block:: bash

    # poliCar project environment variables
    # ------------------------------------------------------------------------------

    ORACLE_SID=ZETATEST

    DJANGO_SETTINGS_MODULE=config.settings.production
    DJANGO_ALLOWED_HOSTS=host
    DJANGO_SECRET_KEY=some-seed
    DATABASE_URL=oraclegis://{username}:{password}@{host}:{port}/{database}
    DJANGO_DEBUG=False

    UPV_LOGIN_DATA_USERNAME=user
    UPV_LOGIN_DATA_PASSWORD=password

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


Actualización del proyecto
--------------------------

Tanto si se han hecho **cambios en el código fuente**, como si se trata de la primera vez que se instala, hay una
serie de pasos que se tienen que ejecutar para asegurarse de que los cambios tienen efecto, siempre asumiendo que se
está en la raíz del código fuente.

Activar el entorno virtual:

.. code-block:: console

    $ workon carshare

Aplicar las migraciones de la base de datos:

.. code-block:: console

    (carshare) $ ./manage.py migrate

Compilar los ficheros estáticos:

.. code-block:: console

    (carshare) $ npm run build

Recopilar los ficheros estáticos:

.. code-block:: console

    (carshare) $ ./manage.py collectstatic


uWSGI
-----

La aplicación poliCar sigue el `PEP 333 <https://www.python.org/dev/peps/pep-0333/>`_ para aplicaciones web hechas con Python,
por lo que cualquier servidor de aplicaciones WSGI sería compatible con la aplicación.

Sin embargo, se recomienda el uso de ``uWSGI`` como servidor de aplicaciones WSGI, que es el que se instala junto al
resto de dependencias. Para configurarlo, hay que crear un fichero ``uwsgi.ini``, con el siguiente contenido,
cambiando las rutas de los ficheros si fuera necesario:


.. code-block:: ini

    [uwsgi]
    chdir           = /home/carshare/carshare-project/upvcarshare
    module          = config.wsgi
    home            = /home/carshare/.virtualenvs/carshare
    env             = DJANGO_SETTINGS_MODULE=config.settings.production
    master          = true
    processes       = 5
    socket          = /home/carshare/carshare.sock
    chmod-socket    = 666
    vacuum          = true
    stats           = /home/carshare/carshare_stats.sock


.. note::

    Asegúrate que el usuario que vaya a ejecutar nginx pueda acceder al fichero ``carshare.sock``.

Supervisor
----------

Para que la gestión del proceso de uWSGI sea más sencilla, se recomienda usar ``supervisord``, que se instala
con las dependencias de yum. Para ello, hay que crear el fichero ``/etc/supervisord.d/carshare.ini``
con los siguientes datos:

.. code-block:: ini

    [program:carshare]
    user                    = carshare
    command                 = /home/carshare/.virtualenvs/carshare/bin/uwsgi --ini /home/carshare/uwsgi.ini
    environment             = PATH="/home/carshare/.virtualenvs/carshare/bin"
    topsignal               = HUP
    stderr_logfile          = /var/log/carshare/carshare.log
    stderr_logfile_maxbytes = 50MB
    stderr_logfile_backups  = 10
    loglevel                = info

Para cargar la nueva configuración hay que reiniciar el servicio:

.. code-block:: bash

    $ sudo systemctl restart supervisord

Y para reiniciar el servidor, cuando se requiera que se apliquen nuevos cambios:

.. code-block:: bash

    $ sudo supervisorctl restart carshare

Nginx
-----

Se recomienda utilizar **Nginx** como proxy sobre **uWSGI**, y además, para servir los estáticos
directamente

Para configurarlo, crea el siguiente fichero ``/etc/nginx/conf.d/carshare.conf``, cambiando las rutas que
sean necesarias:

.. code-block:: nginx

    upstream carshare_app {
        server unix:///home/carshare/carshare.sock;
    }

    server {
        listen 80;
        client_max_body_size 0;
        charset utf-8;

        location /media  {
            alias /home/carshare/carshare-project/upvcarshare/media;
        }

        location /static {
            alias /home/carshare/carshare-project/upvcarshare/public;
        }

        location / {
            uwsgi_pass  carshare_app;
            uwsgi_read_timeout 600;
            uwsgi_param  QUERY_STRING       $query_string;
            uwsgi_param  REQUEST_METHOD     $request_method;
            uwsgi_param  CONTENT_TYPE       $content_type;
            uwsgi_param  CONTENT_LENGTH     $content_length;
            uwsgi_param  REQUEST_URI        $request_uri;
            uwsgi_param  PATH_INFO          $document_uri;
            uwsgi_param  DOCUMENT_ROOT      $document_root;
            uwsgi_param  SERVER_PROTOCOL    $server_protocol;
            uwsgi_param  REMOTE_ADDR        $remote_addr;
            uwsgi_param  REMOTE_PORT        $remote_port;
            uwsgi_param  SERVER_ADDR        $server_addr;
            uwsgi_param  SERVER_PORT        $server_port;
            uwsgi_param  SERVER_NAME        $server_name;
            uwsgi_param UWSGI_SCHEME        http;
        }
    }
