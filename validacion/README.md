# Validación de los modelos

Se presentan ejemplos de códigos para utilizados para la validación de cada uno de los modelos, para el cálculo de las diversas métricas fue utiizado sklearn. Para poder hacer la validación es importante tener una selección de imágenes sobre las cuales será evaluado el sistema.

Uno de los códigos más importantes para el funcionamiento de esta sección es el modelLoader.py, esta clase permite cargar y obtener la información de cualquier archivo .tflite que se proporcione (también es importante recordar que los modelos deberán ser convertidos a .tflite, si no es el caso, se deberá rehacer el archivo modelLoader.py)
