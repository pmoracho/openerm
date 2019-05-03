# OPENERM

* [Página del proyecto](https://pmoracho.github.io/openerm)
* [Proyecto en github](https://github.com/pmoracho/openerm.git)


"OpenERM" es la primera especificación "abierta" para el almacenamiento de
reportes electrónicos. Las siglas OERM hacen referencia a "Open electronic
report management" una forma más moderna de llamar lo que hace algunos años se
conocía como **COLD**, "Computer output to laser disk". Asimismo es la primer
implementación oficial de dicha especificación. 

* [Requisitos iniciales](#markdown-header-requisitos-iniciales)
	* [Preparación del entorno virtual local](#markdown-header-preparacion-del-entorno-virtual)
	* [Otras consideraciones](#markdown-header-otras-consideraciones)


Requisitos iniciales
====================

Antes que nada, necesitaremos:

En Windows:

* [Git for Windows](https://git-scm.com/download/win) instalado y funcionando
* Una terminal de Windows, puede ser `cmd.exe`

En Linux

* Git instalado y funcionando
* Una consola tipo `bash`

Con **Git** instalado, desde la línea de comando y con una carpeta dónde
alojaremos este proyecto, por ejemplo `c:\proyectos` o `~/proyectos`, simplemente:

``` 
c:\> c: 
c:\> cd \proyectos 
c:\> git clone <url del repositorio>
c:\> cd <carpeta del repositorio>
``` 

|                       |                                           |
| --------------------- |-------------------------------------------|
| Repositorio           | https://github.com/pmoracho/openerm.git   |
| Carpeta del proyecto  | .                                         |

## Instalación de **Python**

Para desarrollo de la herramienta es necesario, en primer término, descargar un
interprete Python. **openerm** ha sido desarrollado inicialmnete con la versión 3.4,
debiera funcionar perfectamente bien con cualquier versión de la rama 3x.

**Importante:** Si bien solo detallamos el procedimiento para entornos
**Windows**, el proyecto es totalmente compatible con **Linux**

* [Python 3.6.6 (32 bits)](https://www.python.org/ftp/python/3.6.6/python-3.6.6.exe)
* [Python 3.6.6 (64 bits)](https://www.python.org/ftp/python/3.6.6/python-3.6.6-amd64.exe)

Se descarga y se instala en el sistema el interprete **Python** deseado. A
partir de ahora trabajaremos en una terminal de Windows (`cmd.exe`). Para
verificar la correcta instalación, en particular que el interprete este en el `PATH`
del sistemas, simplemente corremos `python --version`, la salida deberá
coincidir con la versión instalada 

Es conveniente pero no mandatorio hacer upgrade de la herramienta pip: `python
-m pip install --upgrade pip`

## Instalación de `Virtualenv`

[Virutalenv](https://virtualenv.pypa.io/en/stable/). Es la herramienta estándar
para crear entornos "aislados" de **Python**. En nuestro ejemplo **xls2table**,
requiere de Python 3x y de varios "paquetes" adicionales de versiones
específicas. Para no tener conflictos de desarrollo lo que haremos mediante
esta herramienta es crear un "entorno virtual" en una carpeta del proyecto (que
llamaremos `venv`), dónde una vez "activado" dicho entorno podremos instalarle
los paquetes que requiere el proyecto. Este "entorno virtual" contendrá una
copia completa de **Python** y los paquetes mencionados, al activarlo se
modifica el `PATH` al `python.exe` que ahora apuntará a nuestra carpeta del
entorno y nuestras propias librerías, evitando cualquier tipo de conflicto con un
entorno **Python** ya existente. La instalación de `virtualenv` se hará
mediante:

```
c:\..\> pip install virtualenv
```

## Creación y activación del entorno virtual

La creación de nuestro entorno virtual se realizará mediante el comando:

```
C:\..\>  virtualenv venv --clear --prompt=[autoxls] --no-wheel
```

Para "activar" el entorno simplemente hay que correr el script de activación
que se encontrará en la carpeta `.\venv\Scripts` (en linux sería `./venv/bin`)

```
C:\..\>  .\venv\Scripts\activate.bat
[autoxls] C:\..\> 
```

Como se puede notar se ha cambiado el `prompt` con la indicación del entorno
virtual activo, esto es importante para no confundir entornos si trabajamos con
múltiples proyecto **Python** al mismo tiempo.

## Instalación de requerimientos

Mencionábamos que este proyecto requiere varios paquetes adicionales, la lista
completa está definida en el archivo `requirements.txt` para instalarlos en
nuestro entorno virtual, simplemente:

```
[autoxls] C:\..\> pip install -r requirements.txt
```

El proyecto **Openerm** esta construido usando el lenguaje **python** y varios
"packages" o librerías adicionales para dicho lenguaje. Para poder construir
las herramientas del proyecto es necesario preparar antes que nada, un entorno
de desarrollo. A continuación expondremos en detalle cuales son los pasos para
tener preparado el entorno de desarrollo. Este detalle esta orientado a la
implementación sobre Windows 32 bits, los pasos para versiones de 64 bits son
sustancialmente distintos, en particular por algunos de los "paquetes" que se
construyen a partir de módulos en C o C++, de igual forma la instalación sobre
Linux tiene sus grandes diferencias. Eventualmente profundizaremos sobre estos
entornos, pero en principo volvemos a señalar que el siguiente detalle aplica a
los ambientes Windows de 32 bits:


Notas:
======

* Hay dependecias que son fácilmente instalables mediante el comando `pip` y
  otras que no se instalan de la misma forma tan fácilmente. Estás últimas son
  librerías o proyectos en C o C++ que requieren de la compilación de distintos
  módulos, estos "paquetes", para poder instalarse mediante `pip` requieren que
  dispongamos de un compilador C/C++, algo que no siempre ocurre e incluso para
  ser más exactos, deberíamos contar con la misma versión del compilador que
  usa nuestra distribución python. Por esto hemos optado por incluir los
  paquetes ya compilados en su distribución binaria. Los requerimientos de este
  tipo podrán ser encontrados en la carpeta wheels.

* Es recomendable y cómodo, pero entiendo que no es mandatorio, contar con un
  entorno estilo "Linux", por ejemplo [MinGW](http://www.mingw.org/), tal como
  dice la página del proyecto: "MinGW provides a complete Open Source
  programming tool set which is suitable for the development of native
  MS-Windows applications, and which do not depend on any 3rd-party C-Runtime
  DLLs. (It does depend on a number of DLLs provided by Microsoft themselves,
  as components of the operating system; most notable among these is
  MSVCRT.DLL, the Microsoft C runtime library. Additionally, threaded
  applications must ship with a freely distributable thread support DLL,
  provided as part of MinGW itself)." De este entorno requerimos algunas
  herramientas de desarrollo: Bash para la línea de comandos y Make para la
  automatización de varias tareas del proyecto. 

