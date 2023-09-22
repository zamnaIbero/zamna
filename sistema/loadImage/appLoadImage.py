from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic

import sys

import numpy as np

import cv2

import tensorflow as tf

from modelLoader import cvModel, segmentationModel

class appImagenes(QMainWindow):

    def __init__(self):

        modelo_im = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/imMed/detect.tflite'
        modelo_seg = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/segPulmones_tflite/detect.tflite'

        self.modeloCV = cvModel(modelo_im, 0.95)
        self.modeloSeg = segmentationModel(modelo_seg)

        self.cv_h, self.cv_w = self.modeloCV.getDims() # Obtenemos las dimensiones del modelo.
        self.seg_h, self.seg_w = self.modeloSeg.getDims() # Obtenemos las dimensiones del modelo.

        print(self.seg_h)

        self.modeloSeg = segmentationModel(modelo_seg)

        super(appImagenes, self).__init__()

        uic.loadUi('APP/loadImage/visualizadorImagen.ui', self) # Cargamos la interfaz.

        self.abrirImagen = self.findChild(QAction, 'actionAbrir_imagen') # Acción de cargar imagen.
        self.abrirImagen.triggered.connect(self.abrirImagenF) # Conectamos la acción.

        self.imagenLabel = self.findChild(QLabel, 'label')

        self.show()

    def abrirImagenF(self): # Abrir ventana para encontrar archivos.

        file = QFileDialog.getOpenFileName(self, 'Abrir  imagen...', 'C:\\',
                                           'All Files (*);;JPEG Files (*.jpeg);;JPG Files (*.jpg);;PNG Files (*.png)')
            
        if file[0] != '': # Intentamos leer la imagen.

            original = cv2.imread(file[0])

            imH, imW = 800, 800 # Dimensiones para mostrar en pantalla.

            umbral, box, clase = self.modeloCV.findBoxes(cv2.resize(original, (self.cv_h, self.cv_w))) # Estima la imagen que está observando.
            ymin, ymax = int(max(1, (box[0][0] * imH))), int(min(imH,(box[0][2] * imH)))
            xmin, xmax = int(max(1, (box[0][1] * imW))), int(min(imW,(box[0][3] * imW)))

            imagen = cv2.resize(original, (imH, imW)) # Resize para mostrar la imagen.
            h, w, ch = imagen.shape # Shape de la imagen.

            contornear = imagen[ymin:ymax, xmin:xmax]

            cont = cv2.cvtColor(cv2.resize(original, (self.seg_h, self.seg_w)), cv2.COLOR_BGR2GRAY)
            cont = cont/np.max(cont)

            aux = np.float32(cont[tf.newaxis, ...])

            contornos = self.modeloSeg.predict(np.expand_dims(aux, axis = 3))
            aux = cv2.resize(contornear, (self.seg_h, self.seg_w))
            cv2.drawContours(aux, contornos, -1, (25, 255, 255), 1)

            aux = cv2.resize(aux, (np.shape(contornear)[1], np.shape(contornear)[0]))

            imagen[ymin:ymax, xmin:xmax] = aux

            qtFormat = QImage(imagen.data, w, h, ch*w, QImage.Format_BGR888)
            q = qtFormat.scaled(w, h)

            px = QPixmap.fromImage(q)

            self.imagenLabel.setPixmap(px) # Añadimos la imagen.

    def click(self):

        print("hola")

app = QApplication(sys.argv)
ventana = appImagenes()

sys.exit(app.exec())

