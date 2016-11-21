# OPENERM

* [Requisitos iniciales](#markdown-header-requisitos-iniciales)
	* [Preparación del entorno virtual local](#markdown-header-preparacion-del-entorno-virtual)
	* [Otras consideraciones](#markdown-header-otras-consideraciones)


Requisitos iniciales
====================

El proyecto **Openerm** esta construido usando el lenguaje **python** y varios "packages" o librerías adicionales para dicho lenguaje. Para poder construir las herramientas del proyecto es necesario preparar antes que nada, un entorno de desarrollo. A continuación expondremos en detalle cuales son los pasos para tener preparado el entorno de desarrollo. Este detalle esta orientado a la implementación sobre Windows 32 bits, los pasos para versiones de 64 bits son sustancialmente distintos, en particular por algunos de los "paquetes" que se construyen a partir de módulos en C o C++, de igual forma la instalación sobre Linux tiene sus grandes diferencias. Eventualmente profundizaremos sobre estos entornos, pero en principo volvemos a señalar que el siguiente detalle aplica a los ambientes Windows de 32 bits:

* Obviamente en primer lugar necesitaremos [Python](https://www.python.org/ftp/python/3.4.0/python-3.4.0.msi), por ahora únicamente la versión 3.4. La correcta instalación se debe verificar desde la línea de comandos: `python --version`. Si todo se instaló correctamente se debe ver algo como esto `Python 3.4.0`, sino verificar que Python.exe se encuentre correctamente apuntado en el PATH.

* Es conveniente pero no mandatorio hacer upgrade de la herramienta pip: `python -m pip install --upgrade pip`

* [Virutalenv](https://virtualenv.pypa.io/en/stable/). Es la herramienta estándar para crear entornos "aislados" de python. En nuestro ejemplo **Openerm**, requiere de Ptython 3.4 y de varios "paquetes" adcionales de versiones especifícas. Para no tener conflictos de desarrollo lo que haremos mediante esta herramienta es crear un "entorno virtual" de python en una carpeta del projecto (venv), dónde una vez "activado" dicho entorno podremos instalarle los paquetes que requiere el proyecto. Este "entorno virtual" contendrá una copia completa de Python y los paquetes mencionados, al activarlo se modifica el PATH al python.exe que apuntará ahora a nuestra carpeta del entorno y nuestras propias librerías, evitando cualquier tipo de conflicto con un entorno Python ya existente. La instalación de virtualenv se hara mediante `pip install virtualenv`

* Descargar el proyecto desde [Bitbucket](https://bitbucket.org/pmoracho/openerm/overview), se puede descargar desde la página el proyecto como un archivo Zip, o si contamos con [Git](https://git-for-windows.github.io/) sencillamente haremos un `git clone https://pmoracho@bitbucket.org/pmoracho/openerm.git`.

* El proyecto una vez descomprimido o luego del clonado del repositorio tendrá una estructura de directorios similar a la siguiente:

```
openerm
   |-build
   |-dist
   |-doc
   |-openerm
   |-tests
   |-tools
   |-var
   |-wheels
```

Preparación del entorno virtual local
=====================================

Para poder ejecutar, o crear la distribución de la herramientas, lo primero que deberemos hacer es armar un entorno python "virtual" que alojaremos en una subcarpeta del directorio principal que llamarems "venv". En el proyecto incorporamos una herramienta de automatización de algunas tareas básicas. Se trata de `make.py`, la forma de ejecutarlo es la siguiente: `python tools\make.py` la ejecución si parámetros arrojará una salida como lo que sigue:

```
Automatización de tareas para el proyecto Openerm
(c) 2016, Patricio Moracho <pmoracho@gmail.com>

Uso: make <command> [<args>]

Los comandos más usados:
   devcheck   Hace una verificación del entorno de desarrollo
   devinstall Realiza la instalación del entorno de desarrollo virtual e instala los requerimientos
   clear      Elimina archivos innecesarios
   test       Ejecuta todos los tests definidos del proyecto
   tools      Construye la distribución binaria de las herramientas del proyecto

make.py: error: los siguientes argumentos son requeridos: command
```
Para preparar el entorno virtual simplemente haremos `python tools\make.py devinstall`, este proceso si resulta exitoso deberá haber realizado las siguientes tareas:

* Creación de un entorno pyhton virtual en la carpeta "venv", invocable mediante `venv\Scripts\activate.bat` en Windows o `source venv/Scripts/activate` en entornos Linux o Cygwin/Mingw (en Windows)
* Instalado todas las dependencias necesarias


# Notas:

* Hay dependecias que son fácilmente instalables mediante el comando `pip` y otras que no se instalan de la misma forma tan fácilmente. Estás últimas son librerías o proyectos en C o C++ que requieren de la compilación de distintos módulos, estos "paquetes", para poder instalarse mediante `pip` requieren que dispongamos de un compilador C/C++, algo que no siempre ocurre e incluso para ser más exactos, deberíamos contar con la misma versión del compilador que usa nuestra distribución python. Por esto hemos optado por incluir los paquetes ya compilados en su distribución binaria. Los requerimientos de este tipo podrán ser encontrados en la carpeta wheels.


* Es recomendable y cómodo, pero entiendo que no es mandatorio, contar con un entorno estilo "Linux", por ejemplo [MinGW](http://www.mingw.org/), tal como dice la página del proyecto: "MinGW provides a complete Open Source programming tool set which is suitable for the development of native MS-Windows applications, and which do not depend on any 3rd-party C-Runtime DLLs. (It does depend on a number of DLLs provided by Microsoft themselves, as components of the operating system; most notable among these is MSVCRT.DLL, the Microsoft C runtime library. Additionally, threaded applications must ship with a freely distributable thread support DLL, provided as part of MinGW itself)." De este entorno requerimos algunas herramientas de desarrollo: Bash para la línea de comandos y Make para la automatización de varias tareas del proyecto. 

Otras consideraciones
=====================

* Usar "soft tabs": Con cualquier editor que usemos configurar el uso del <tab> en vez de los espacios, yo prefiero el <tab> puro al espacio, entiendo que es válido el otro criterio pero ya los fuentes están con esta configuración, por lo que para evitar problemas al compilar los .py recomiendo seguir usando este criterio. Asimismo configurar en 4 posiciones estos <tab>.

* * *
