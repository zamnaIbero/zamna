# Uso del sistema

TODOS LOS ARCHIVOS de esta carpeta deberán estar juntos, este es un proyecto modular. Ejecutar el archivo zamna.py dará inicio a todo el sistema. 

#### Paso 0:

Descargar e instalar cada una de las dependencias (paquetes) utilizadas en el sistema, se recomienda el uso de pip, verificar que la PC (Raspberry, Jetson, ...) en la que se ejecutará el Zamná cuente con al menos una cámara. Dicha cámara será accesada vía OpenCV.

Si el sistema no se ejecuta correctamente, verificar: la ubicación de los archivos, de los modelos y/o los drivers de las cámaras que se planean utilizar.

#### Paso 1:

Se deberá de seleccionar una cámara (la primera ventana que aparecerá), si se está utilizando los lentes Lenovo ThinkReality A3, deberás de instalar el software de los mismos antes de esto.

#### Paso 2:

Se harán visibles dos ventanas más, una de ellas contendrá información relevante de la imagen que se visualiza o será visualizada, al lado izquierdo cuenta con checkbox para la activación del modo diagnóstico y modo segmentación (o ambos). Además puedes ajustar el número de imágenes a ser detectadas, sólo por diversión.

#### Known issues:

Existen checkboxes de cada imagen, no tienen ninguna función, puede ser eliminados desde el archivo .ui de la GUI del sistema, para ello es buena idea utilizar el PyQt designer.
