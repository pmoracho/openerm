# OPENERM

* [Página del proyecto](https://pmoracho.github.io/openerm)
* [Proyecto en github](https://github.com/pmoracho/openerm.git)


**`OpenERM`** es la primera especificación "abierta" para el almacenamiento de
reportes electrónicos. Las siglas `OERM` hacen referencia a _Open electronic
report management_ una forma moderna de llamar lo que hace algunos años se
conocía como **`COLD`**, _Computer output to laser disk_. Asimismo es la primer
implementación oficial de dicha especificación. 

* [Requisitos iniciales](#markdown-header-requisitos-iniciales)
    * [Instalación de python](#instalacion_de_python)
    * [Descarga e instalación del repositorio del proyecto](#descarga_e_instalacion_del_repositorio_del_proyecto)
	* [Preparación del entorno virtual local](#markdown-header-preparacion-del-entorno-virtual)
	* [Otras consideraciones](#markdown-header-otras-consideraciones)


## Requisitos iniciales

Para poder empezar a usar este proyecto, tanto para desarrollo como para
ejecutar las herramientas, el primer paso es "clonar" este repositorio en
nuestro sistema. Para esto, necesitaremos **[Git](https://git-scm.com/)** y una
consola de sistema:

En Windows:

* [Git for Windows](https://git-scm.com/download/win) instalado y funcionando
* Una terminal de Windows, puede ser el clásico `cmd.exe`.

En Linux

* Git instalado y funcionando, hoy en día es raro que no venga instalado por
  defecto. Si fuera el caso consultar la documentación del SO para ver como
  instalarlo.
* Una consola tipo `bash`.

Para verificar la instalación, simplemente, desde la consola, podremos hacer: 

```sh
# > git -- version
# > git version 2.7.4
```

### Instalación de **Python**

Para desarrollo de la herramienta es necesario, en primer término, descargar un
interprete Python. **openerm** ha sido desarrollado inicialmnete con la versión 3.4,
pero debiera funcionar perfectamente bien con cualquier versión de la rama `3x`.

**En Windows**

* [Python 3.6.6 (32 bits)](https://www.python.org/ftp/python/3.6.6/python-3.6.6.exe)
* [Python 3.6.6 (64 bits)](https://www.python.org/ftp/python/3.6.6/python-3.6.6-amd64.exe)

1.  Se descarga y se instala en el sistema el interprete **Python** deseado. A
    partir de ahora trabajaremos en una terminal de Windows (`cmd.exe`). Para
    verificar la correcta instalación, en particular que el interprete este en
    el `PATH` del sistemas, simplemente corremos `python --version`, la salida
    deberá coincidir con la versión instalada.

2.  Es conveniente pero no mandatorio hacer upgrade de la herramienta pip:
    `python -m pip install --upgrade pip`

**En Linux**

Consultar la documentación de su SO. 


### Descarga e instalación del repositorio del proyecto

Teniendo una carpeta base o "root" para el proyecto, digamos por ejemplo:
`c:\proyectos` o `~/proyectos`, simplemente haremos:

```sh
# > cd proyectos 
# > git clone https://github.com/pmoracho/openerm.git openerm.git
# > cd openerm.git
```

(*) por las dudas, respetar el nombre del proyecto `openerm.git` para la
carpeta destino.

### Instalación de `Virtualenv`

Para poder ejecutar cualquiera de las herramientas del proyecto, ya vimos que
necesitamos un interprete de **`Python`**, sin embargo es una mala práctica
depender directamente de la instalación inicial. Es más óptimo generar un
entorno de **`Python`**, exclusivo para este proyecto. De esta forma logramos
una estabilidad en el interprete y sobre todo en los paquetes adicionales o
dependencias del proyecto.

[Virutalenv](https://virtualenv.pypa.io/en/stable/). Es la herramienta estándar
para crear entornos "aislados" de **Python**. Este proyecto, requiere de Python
3x y de varios "paquetes" adicionales de versiones específicas. Para no tener
conflictos de desarrollo lo que haremos mediante esta herramienta es crear un
"entorno virtual" en una carpeta del proyecto (que llamaremos `venv`), dónde
una vez "activado" dicho entorno podremos instalarle los paquetes que requiere
el proyecto. Este "entorno virtual" contendrá una copia completa de
**`Pytho`n** y los paquetes mencionados, al activarlo se modifica el `PATH` al
interprete `python.exe` de modo que apunte a nuestra carpeta del entorno y
nuestras propias librerías, evitando cualquier tipo de conflicto con un entorno
**`Python`** ya existente o futuro, así como cualquier eventual cambio a
niveSO. La instalación de `virtualenv` se hará mediante:

```
# > pip install virtualenv
```

### Creación y activación del entorno virtual

Una vez instalado [Virutalenv](https://virtualenv.pypa.io/en/stable/),
deberemos crear nuestro entorno virtual dentro de la carpeta del proyecto, que
es lo más recomendable, aunque podría ser cualquier otra carpeta. La creación
se realizará mediante el comando:

```sh
# > virtualenv -p python3 venv --clear --prompt=[openerm]
```

Para "activar" el entorno simplemente hay que correr el script de activación
que se encontrará en la carpeta `.\venv\Scripts` (en linux sería `./venv/bin`)

Por ejemplo:

```sh
C:\..\>  .\venv\Scripts\activate.bat
[openerm] C:\..\> 
```

Como se puede notar se ha cambiado el `prompt` con la indicación del entorno
virtual activo, esto es importante para no confundir entornos si trabajamos con
múltiples proyecto **`Python`** al mismo tiempo. El `prompt` puede variar de
sistema a sistema, pero es útil verificar que el `PATH` a el interprete, esté
apuntando a la carpeta del proyecto.


### Instalación de requerimientos

Mencionábamos que este proyecto requiere varios paquetes adicionales, la lista
completa está definida en el archivo `requirements.txt` para instalarlos en
nuestro entorno virtual, simplemente:

```
[openerm] C:\..\> pip install -r requirements.txt
```

