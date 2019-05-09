.. Openerm documentation master file, created by
   sphinx-quickstart on Mon Sep 12 17:42:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#######
Openerm
#######


**OpenERM** es la primera especificación "abierta" para el almacenamiento de
reportes electrónicos. Las siglas *OERM* hacen referencia a *Open electronic
report management* una forma moderna de llamar lo que hace algunos años se
conocía como **COLD**, *Computer output to laser disk*. Asimismo es la primer
implementación oficial de dicha especificación. 


Un poco de historia
===================

Desde los inicios y en todo tipo de apliciones informaticas, se han generado
enormes cantidades de informes, estos reportes terminaban su ciclo de vida en
el papel, informes de 80 o 132 columnas, de formato habitualmente tabular.
Millones de hojas de papel fueron impresas y distribuídas de esta forma en todo
tipo de empresa a lo largo y ancho del mundo. Sin embargo el acceso a la
información mediante el "papel", en poco tiempo hizo notar sus limitaciones.
Surge una teconolgía, que tuvo su esplendor en las decada del 80 y del 90, se
trata de lo que en ese entonces se habia bautizado como *"COLD"*, es decir
*"Computer output to laser disk"*. El concepto era simple, se "capturaba" la
salida hacia la impresora de los sistemas centralizados, normalmente
"Mainframes" o grandes computadores, y esta salida era guardada en archivos
electrónicos, almacenada, indizada y distribuída mediante discos ópticos (laser
disk), pudiendo luego ser visualizada mediante un software *"COLD"* en PCs u
otras mini computadoras.

Este "paradigma", un gran computador central, aplicaciones que
explotan la información en reportes de tipo texto, distribución final
en papel, tuvo una larga vida. Sin embargo los cambios en la
tecnología, el abaratamiento de los costos y otros factores han dejado
de lado este "modelo" por otros. Los sistemas "COLD" han ido langideciendo
de a poco, sin embargo sigue existiendo un "nicho" importante para este 
tipo de herramientas: aún hoy existen empresas que apoyan la gestión
de su negocio en grande computadores o "Mainframes" y siguen generando
enormes cantidades de listados. 


Estatus del proyecto a abril 2019
=================================

Esta es la situación actual del proyecto. 

    Definiciones:

    * Estructura fisica dónde salvar los reportes
    
    Funcionalidad:

    * Varios algoritmos de compresión, ver: :class:`openerm.Compressor`
    * Cifrado (Spritz y Fernet), ver: :class:`openerm.Cipher`
    * Se implementó una clase para el guardado y recuperación de los reportes y sus páginas, ver: :class:`openerm.Database`

    Herramientas:

    * Spl2oerm - Procesador básico de spooles:

      - Procesamiento de spooles ASCII/EBCDIC de registro de longitud fija, ver: :class:`openerm.SpoolFixedRecordLength`
      - Procesamiento de spooles ASCII/EBCDIC de registro de longitud variable con info de canal, ver: :class:`openerm.SpoolHostReprint`
      - Identificación de páginas, por texto de salto de página o info de canal
      - Identificación simple de reportes por texto encontrado en página
      - Configuración completa del proceso definido en archivo de configuración yaml
      - Salvado de los reportes en el Database final

    * readoermdb - Lectura de un database OERM:

      * Lectura de un Database
      * Recuperación de reportes
      * Lectura de cualquier reporte
      * Extracción de páginas
      
    To do:
    
    * Mejorar la identificación de reportes
    * Mas opciones, multiples textos a ubicar
    * Configurar ventanas de búsquedas (cabeceras/footers)
    * Optimizar identificación mediante algún algoritmo mejorado
    * Paralelizar el proceso del spool, separando la lectura de páginas de la identificación de archivos y el salvado final
    * Captura de datos (fecha, sistema, aplicación, etc) desde el mismo reporte
    * Definir mejor los datos adicionales de los reportes. Hoy el único dato real que identifica un reporte el el nombre del mismo



Openerm - API
=============

Estos son los módulos principales

.. toctree::
   :maxdepth: 2

   especificacion.rst 
   openerm.rst


Herramientas
============
.. toctree::
   :maxdepth: 2

   splprocessor.rst
   spl2oerm.rst
   catalogrepo.rst
   checkoermdb.rst
   make.rst
   oerm_hostreprint_processor.rst
   readoermdb.rst

Desarrollo
==========

Algunos puntos importantes para el desarrollador

.. toctree::
   :maxdepth: 2

   desarrollo.rst




Indices y tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

