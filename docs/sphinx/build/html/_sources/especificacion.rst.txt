OERM - Especificación v1
========================


Estructura de un database OpenErm
=================================

Un Database OpenErm es un archivo que almacena reportes electrónicos de forma comprimida y/o 
encriptada. Se representa físicamente por tres archivos básicos:

    * **<database>**.oerm: (o "DATA") Es el archivo físico principal, es simplemente un contenedor 
      de bloques. Los bloques son conjuntos arbitrarios y variables de bytes. Los
      bloques pueden ser de dos tipos

        * Contenedor de metadatos
        * Contenedor de páginas

    * **<database>**.cidx.oerm: índice de bloques. Básicamente es una lista con los offsets o 
      posiciones físicas dónde comienza cada bloque del archivo principal.

    * **<database>**.ridx.oerm: índice de reportes. Es la lista de offsets o posiciones 
      físicas de los bloques contenedores de metadatos de cada uno de los reportes que se
      almacenan en el archivo princiapl.

El archivo principal **<database>**.oerm o "DATA" contiene toda la información fundamental,
tanto el índice de bloques como el de reporte puede ser regenerado en cualquier momento a 
partir de archivo "DATA"

.. code-block:: none 

    Estructura de un <database>.oerm

    +========+
    | "oerm" |              --> "Magic number" (4 bytes)
    +===================+
    |     Bloque 1      |   --> Bytes (longitud variable)
    +===================+
    |                   |
    |     Bloque 2      |   --> Bytes (longitud variable)
    |                   |
    +===================+
    ..
    +===================+
    |     Bloque  N     |   --> Bytes (longitud variable)
    +===================+
    

    Estructura de cualquier Bloque

    +=======================+
    | Long.Total del Bloque |   --> long (4 bytes)
    +=======================+
    | Tipo de Bloque  |         --> int (1 bytes)
    +=================+
    | Alg. Compresión |         --> int (1 bytes)
    +=================+
    | Alg. Cifrado    |         --> int (1 bytes)
    +=======================+
    | Long. de los Datos    |   --> long (4 bytes)
    +=======================+
    |                       |
    |        Datos          |   --> Longitud variable (datos comprimibles)
    |                       |
    +=======================+
    |                       |
    |    Datos variables    |   --> (Opcional) Longitud variable (datos NO comprimibles)
    |                       |
    +=======================+

