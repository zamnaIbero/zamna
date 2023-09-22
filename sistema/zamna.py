from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer

from mainWin import mainWin as mw
from mainWin import visualizador as v

import sys
import cv2

class zamna(QMainWindow):

    def __init__(self):

        super(zamna, self).__init__()

        self.indice = 0

        self.camarasDisponibles()
        self.seleccionaCamara()

    def camarasDisponibles(self):

        for i in range(0, 6): # Hasta 5 cámaras conectadas.

            prueba = cv2.VideoCapture(i) # Cambiamos la cámara.
            r, f = prueba.read()

            if r:

                pass
                
            else:

                break

        self.camaras = ['Cámara {}'.format(j + 1) for j in range(0, i)]

    def configCamara(self):

        self.cam = cv2.VideoCapture(self.indice) # Inicializamos la cámara.

    def actualizaImagen(self):

        r, f = self.cam.read()

        if r:

            f = cv2.resize(cv2.cvtColor(cv2.flip(f, 1), cv2.COLOR_BGR2RGB), (self.imagen.width(), self.imagen.height()))
            h, w, ch = f.shape
            qtf = QImage(f.data, w, h , ch*w, QImage.Format_RGB888)
            self.imagen.setPixmap(QPixmap.fromImage(qtf))

    def seleccionaCamara(self):

        uic.loadUi('APP/UI/cam.ui', self) # Cargamos la UI.

        self.baceptar = self.findChild(QPushButton, 'bAceptar') # El botón para inicializar.
        self.imagen = self.findChild(QLabel, 'imagen') # Label donde irá la imagen.
        self.combo = self.findChild(QComboBox, 'comboCamara') # Combo box de la cámara.
        
        self.baceptar.clicked.connect(self.iniciarZamna)
        self.combo.currentIndexChanged.connect(self.ind)
        self.combo.addItems(self.camaras)

        self.configCamara()

        r, f = self.cam.read() # Lectura de la cámara.
        f = cv2.resize(cv2.cvtColor(cv2.flip(f, 1), cv2.COLOR_BGR2RGB), (self.imagen.width(), self.imagen.height()))

        h, w, ch = f.shape
        qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888)
        self.imagen.setPixmap(QPixmap.fromImage(qtf)) # Ponemos la primera imagen.

        # Inicializamos el qtimer.

        t = QTimer(self)
        t.timeout.connect(self.actualizaImagen)
        t.start(150) # Actualizamos la imagen cada 80 ms.

        self.show()

    # Funciones.

    def ind(self, value): 
        
        self.indice = value
        self.configCamara()

    def iniciarZamna(self):
        
        # Instanciar mainWin.
        
        self.close() # Cerramos la ventana de configuración.

        self.mainZamna = mw(self.cam) # Ventana de principal del programa.
        self.mainZamna.show()

app = QApplication(sys.argv)
win = zamna()
sys.exit(app.exec())