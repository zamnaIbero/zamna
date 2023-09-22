# Modelos del sistema

Los modelos utilizados en el sistema tiempo real, se deben indicar los PATHS de los modelos en el archivo mainWin.py, los modelos para el diagnóstico (arquitectura VGG16) no pueden ser añadidos por el peso de los archivos, se encontrarán en el Drive del proyecto, o bien pueden realizarse pruebas para en el re-entrenamiento de los mismos, se recomienda utilizar arquitecturas basadas en TPU y versiones simplificadas de VGG16.

Para este proyecto es importante que los modelos mantengan en su formato .tflite (o al menos se recomienda que así sea) más información sobre este tipo de modelos en: https://www.tensorflow.org/lite/models/convert/convert_models

:)
