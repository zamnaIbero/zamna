import matplotlib

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.colors import hsv_to_rgb

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from loadImage.modelLoader import cvModel, diagnosticModel, segmentationModel

import cv2

import numpy as np

import time

class histograma(FigureCanvasQTAgg):

    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):

        fig = Figure(figsize = (width, height), dpi = dpi)
        self.ax = fig.add_subplot(111)

        super(histograma, self).__init__(fig)

class mainWin(QMainWindow):

    def __init__(self, camara):
        
        super(mainWin, self).__init__()
        self.camara = camara # Indice de la cámara que será utilizada.

        self.diag = 0 # Banderas de diagnóstico y segmentación iniciadas en 0.
        self.seg = 0
        self.invertir = 0

        self.configHistograma()
        self.win()

    def win(self): # Ventana principal.

        self.sc = histograma(self, width = 5, height = 4, dpi = 100) # Estimación.
        self.sc.ax.set_title(" ")
        #sc.ax.plot([0,1,2,3,4], [10,1,20,3,40])

        uic.loadUi('APP/UI/zamna.ui', self)

        self.imagen = self.findChild(QLabel, 'label') # Imagen detectada.
        self.framehist = self.findChild(QVBoxLayout, 'verticalLayout') # Contiene el histograma.
        self.framehist.addWidget(self.sc)

        # CheckBoxes.

        self.radTorax_check = self.findChild(QCheckBox, 'checkBox') # Checkbox de la radiografia de torax.
        self.mast_check = self.findChild(QCheckBox, 'checkBox_3')
        self.fundus_check = self.findChild(QCheckBox, 'checkBox_2')

        # CheckBoxes diag-seg

        self.diag_check = self.findChild(QCheckBox, 'checkBox_5')
        self.seg_check = self.findChild(QCheckBox, 'checkBox_6')

        # GroupBoxes

        self.hist_gp = self.findChild(QGroupBox, 'groupBox_4')

        # Acciones del menubar.

        self.invertirAc = self.findChild(QAction, 'actionInvertir_imagen')
        self.invertirAc.triggered.connect(self.invertirImagen) 

        self.radTorax_check.stateChanged.connect(self.checkImagenes)
        self.mast_check.stateChanged.connect(self.checkImagenes)
        self.fundus_check.stateChanged.connect(self.checkImagenes)

        self.diag_check.stateChanged.connect(self.checkModo)
        self.seg_check.stateChanged.connect(self.checkModo)

        # SpinBox

        self.max_imagenes = self.findChild(QSpinBox, 'spinBox')

        # Visualizador.

        self.v = visualizador(self, self.camara)
        self.v.show()

        self.show() # Mostramos la ventana.

    def invertirImagen(self):

        if self.invertir == 1: self.invertir = 0
        elif self.invertir == 0: self.invertir = 1

        print(self.invertir)

    def checkImagenes(self, e):

        if self.sender() == self.radTorax_check:

            print("rad")

        if self.sender() == self.mast_check:

            print("mast")

        if self.sender() == self.fundus_check:

            print("fundus")

    def checkModo(self, e):

        if self.sender() == self.diag_check:

            if self.diag_check.isChecked(): self.diag = 1
        
            elif self.diag_check.isChecked() is not True: self.diag = 0

        if self.sender() == self.seg_check:

            if self.seg_check.isChecked(): self.seg = 1

            elif self.seg_check.isChecked() is not True: self.seg = 0

    def configHistograma(self):

        num = 20
        delta = 180/num

        grados, self.hexa = [delta*i for i in range(0, num)], []

        for i in grados:

            rgb = hsv_to_rgb((i/360, 0.47, 0.95))
            self.hexa.append('#{:X}{:X}{:X}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))

    def actualizarHistograma(self, titulo, resultado, labels):

        # El título está conformado por el tipo de imagen y la exactitud de estimación.

        self.framehist.removeWidget(self.sc)
        
        num = 20
        div = 1/num
        
        ind = [i for j in range(0, len(resultado)) for i in range(0, num) if resultado[j] >= div * i and resultado[j] < div * (i + 1)]
        coloresbarras = [self.hexa[i] for i in ind] # Colores finales para la gráfica.

        self.sc = histograma(self, width = 5, height = 4, dpi = 100)
        self.sc.ax.set_title(titulo)
        self.sc.ax.bar(labels, resultado, color = coloresbarras)

        self.sc.ax.set_xticks([i for i in range(0, len(resultado))], labels, fontsize = 7)

        self.framehist.addWidget(self.sc)

    def actualizarImagen(self, f):

        f = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), (self.imagen.width(), self.imagen.height()))
        h, w, ch = f.shape
        qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888)
        self.imagen.setPixmap(QPixmap.fromImage(qtf))

""" Clase """

class visualizador(QMainWindow):

    def __init__(self, main, camara):

        super(visualizador, self).__init__()

        self.main = main
        self.camara = camara

        self.imH, self.imW = 480, 640
        self.ntime = 0
        self.prevtime = 0

        self.configVisualizador()

        self.redMadre = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/imMed5/imMed.tflite'

        self.redDiagPulmones = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/diagPulmones_tflite/modelo001_5.tflite'
        self.redDiagFondo = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/diagFondo_tflite/modeloTPU.tflite'

        self.redSegPulmones = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/segPulmones_tflite/segPulmones.tflite'
        self.redSegFondo = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/segFondo_tflite/detect.tflite'
        self.redSegCT = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/pulmonesCT2_tflite/segCT2.tflite'

        self.modeloCV = cvModel(self.redMadre, 0.80)
        self.diagRT = diagnosticModel(self.redDiagPulmones) # Red de diagnóstico de radiografía de tórax.
        self.diagFd = diagnosticModel(self.redDiagFondo) # Red de diagnóstico de fondo de ojo.

        self.segRT = segmentationModel(self.redSegPulmones) # Red de segmentación radiografía de tórax.
        self.segCT = segmentationModel(self.redSegCT) # Red de segmentación ct.
        self.segFo = segmentationModel(self.redSegFondo) # Red de segmentación de fondo de ojo.

        self.dimssegRT = (self.segRT.getDims()[0], self.segRT.getDims()[1])
        self.dimssegCT = (self.segCT.getDims()[0], self.segCT.getDims()[1])
        self.dimssegFo = (self.segFo.getDims()[0], self.segCT.getDims()[1])

        self.dimsdiagRT = (self.diagRT.getDims()[0], self.diagRT.getDims()[1])
        self.dimsdiagFd = (self.diagFd.getDims()[0], self.diagFd.getDims()[1]) # Dimensiones de entrada.

        self.dimsModeloCV = (self.modeloCV.getDims()[0], self.modeloCV.getDims()[1])

        self.max_detect = self.main.max_imagenes.value()
        self.main.max_imagenes.valueChanged.connect(self.valuechanged)

        self.etiquetas = ['Mast. Der', 'Mast. Izq', 'MRI Cerebro', 'Rad. Torax', 'CT', 'Fondo'] # Posibles imágenes médicas.

    def valuechanged(self):

        self.max_detect = self.main.max_imagenes.value()
        print(self.max_detect)

    def configVisualizador(self):

        uic.loadUi('APP/UI/visualizador.ui', self)

        self.label = self.findChild(QLabel, 'label')

        r, f = self.camara.read()
        f = cv2.resize(cv2.cvtColor(cv2.flip(f,1), cv2.COLOR_BGR2RGB), (self.label.width(), self.label.height()))

        h, w, ch = f.shape
        qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qtf))

        # Inicializamos los qtimer, uno para modificar la imagen, otro para el diagnóstico.

        t = QTimer(self)
        t.timeout.connect(self.actualizaImagen) # Actualizamos la imagen cada 100 ms.
        t.start(100)

        self.show()

    def genTitulo(self, clase, umbral):

        umbral = str(np.round(umbral[0] * 100, 3)) + " %"

        etiquetas = ['Mast. Der', 'Mast. Izq', 'MRI Cerebro', 'Rad. Torax', 'CT', 'Fondo']
        clase = etiquetas[int(clase[0])]

        titulo = clase + " " + umbral

        return titulo
    
    def segmentacion(self, imagen, clase):

        if clase[0] == 3: # Pulmones.
            
            dimOutput = (self.segRT.getOutputDims()[0], self.segRT.getOutputDims()[1])
            contornos = self.segRT.predict(cv2.resize(imagen, self.dimssegRT))
            
        if clase[0] == 4:

            dimOutput = (self.segCT.getOutputDims()[0], self.segCT.getOutputDims()[1])
            contornos = self.segCT.predict(cv2.resize(imagen, self.dimssegCT))

        if clase[0] == 5:

            dimOutput = (self.segFo.getOutputDims()[0], self.segFo.getOutputDims()[1])
            contornos = self.segFo.predict(cv2.resize(imagen, self.dimssegFo))

        return contornos, dimOutput

    def diagnostico(self, imagen, clase, umbral):

        if clase[0] == 3: # Radiografía de tórax

            labels = ['Normal', 'P. inflamatorio', 'Mayor densidad', 'Menor densidad', 'Enf. Degenerativas', 'Enf. Obstructivas']

            resultado = self.diagRT.predict(cv2.resize(imagen, self.dimsdiagRT)) # Dimensionamos
            self.main.actualizarHistograma(self.genTitulo(clase, umbral), resultado, labels)

            return labels[np.argmax(resultado)], np.round(resultado[np.argmax(resultado)] * 100, 3)

        if clase[0] == 5: # Fondo de ojo.

            labels = ['Normal', 'Ret. diabetica', 'Glaucoma', 'Catarata', 'Miopia']

            resultado = self.diagFd.predict(cv2.resize(imagen, self.dimsdiagFd))
            self.main.actualizarHistograma(self.genTitulo(clase, umbral), resultado, labels)

            return labels[np.argmax(resultado)], np.round(resultado[np.argmax(resultado)] * 100, 3)

    #  TODO: INVERTIR LA IMAGEN CUANDO SE HACE UNA SEGMENTACIÓN.

    def actualizaImagen(self):

        r, f = self.camara.read()
        f = cv2.flip(f, 1)

        if r:

            self.ntime = time.time()
            umbral, box, clases = self.modeloCV.findBoxes(cv2.resize(f, self.dimsModeloCV))

            try:

                if self.max_detect == 1: # Detectamos una imagen.

                    f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)

                    ymin, ymax = int(max(1, (box[0][0] * self.imH))), int(min(self.imH,(box[0][2] * self.imH)))
                    xmin, xmax = int(max(1, (box[0][1] * self.imW))), int(min(self.imW,(box[0][3] * self.imW)))

                    nombre = "{} : {} %".format(self.etiquetas[int(clases[0])], np.round(umbral[0] * 100, 2))
                    
                    cv2.rectangle(f, (xmin, ymin), (xmax, ymax), (0, 0, 0), 2) # Dibujamos el rectángulo.

                    contornear = f[ymin:ymax, xmin:xmax] # Imagen a ser analizada.

                    self.main.hist_gp.setTitle(self.etiquetas[int(clases[0])])

                    imagen = cv2.cvtColor(f[ymin:ymax, xmin:xmax], cv2.COLOR_RGB2GRAY)
                    imagen = imagen/np.max(imagen)

                    # IF's para ver si diagnosticamos o segmentamos o ambos.
                    # Primero enviamos la imagen a la ventana principal.

                    if self.main.diag == 1 and self.main.seg == 1: 

                        n, a = self.diagnostico(imagen, clases, umbral) # Regresa el nombre y la accuracy.
                        contornos, dimOutput = self.segmentacion(imagen, clases)

                        aux = cv2.resize(contornear, dimOutput)

                        cv2.drawContours(aux, contornos, -1, (255, 25, 25), 1)
                        
                        if self.main.invertir == 1: self.main.actualizarImagen(cv2.flip(aux, 1))
                        elif self.main.invertir == 0: self.main.actualizarImagen(aux)

                    elif self.main.diag == 1 and self.main.seg == 0: # Solamente existe el diagnóstico.

                        n, a = self.diagnostico(imagen, clases, umbral) # Regresa el nombre y la accuracy.

                        if self.main.invertir == 1: self.main.actualizarImagen(cv2.flip(contornear, 1)) # Colocamos la imagen en la ventana principal.
                        elif self.main.invertir == 0: self.main.actualizarImagen(contornear)

                    elif self.main.diag == 0 and self.main.seg == 1:

                        contornos, dimOutput = self.segmentacion(imagen, clases)
                        aux = cv2.resize(contornear, dimOutput)
                        cv2.drawContours(aux, contornos, -1, (255, 25, 25), 1)
                        
                        if self.main.invertir == 1: self.main.actualizarImagen(cv2.flip(aux, 1))
                        elif self.main.invertir == 0: self.main.actualizarImagen(aux)

                    # Dibujamos la imagen en la ventana principal, el visualizador #
                    # DIAGNÓSTICO #

                    if self.main.diag == 0: # Solamente un cuadrado blanco con la etiqueta de la imagen.
                        
                        cv2.rectangle(f, (xmin, ymax + 2), (xmax, ymax + 25), (255, 255, 255), cv2.FILLED) # Dibujamos el rectángulo de la etiqueta.
                        cv2.putText(f, nombre, (xmin + 5, ymax + 14), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 0, 0), 1) # Dibujamos el texto.

                    elif self.main.diag == 1: 

                        diag = "Diag: {} , cert. {} %".format(n, a) # Diagnóstico y la certeza de dicho diagnóstico como string.
                        
                        cv2.rectangle(f, (xmin, ymax + 2), (xmax, ymax + 35), (255, 255, 255), cv2.FILLED)
                        cv2.putText(f, nombre, (xmin + 5, ymax + 14), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 0, 0), 1) # Dibujamos el texto.
                        cv2.putText(f, diag, (xmin + 5, ymax + 26), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0, 0, 0), 1)

                    f = cv2.resize(f, (self.label.width(), self.label.height())) 
                    
                    # Ajustamos la imagen

                    if self.main.invertir == 1: f = cv2.flip(f, 1) # Verificamos si se tiene que invertir la imagen.
                    elif self.main.invertir == 0: f = f

                    h, w, ch = f.shape
                    qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888)
                    self.label.setPixmap(QPixmap.fromImage(qtf))

                    self.prevtime = time.time()
                    print(self.prevtime - self.ntime)

                elif self.max_detect > 1:

                    contornear = []
                    f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)

                    for i in range(0, self.max_detect):

                        ymin, ymax = int(max(1, (box[i][0] * self.imH))), int(min(self.imH,(box[i][2] * self.imH)))
                        xmin, xmax = int(max(1, (box[i][1] * self.imW))), int(min(self.imW,(box[i][3] * self.imW)))

                        nombre = "{} : {} %".format(self.etiquetas[int(clases[i])], np.round(umbral[i] * 100, 2))
             
                        detectada = cv2.cvtColor(cv2.resize(f[ymin:ymax, xmin:xmax], (256, 256)), cv2.COLOR_RGB2GRAY) # Crop y dimensionamos.
                        contornear.append(detectada/np.max(detectada)) # Normalizamos.
                        
                        cv2.rectangle(f, (xmin, ymin), (xmax, ymax), (0, 0, 0), 3)

                        if self.main.diag == 0:

                            cv2.rectangle(f, (xmin, ymax + 2), (xmax, ymax + 25), (255, 255, 255), cv2.FILLED) # Dibujamos el rectángulo de la etiqueta.
                            cv2.putText(f, nombre, (xmin + 5, ymax + 14), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 0, 0), 1) # Dibujamos el texto.

                    f = cv2.resize(f, (self.label.width(), self.label.height())) 
                            
                    if self.main.invertir == 1: f = cv2.flip(f, 1) # Verificamos si se tiene que invertir la imagen.
                    elif self.main.invertir == 0: f = f

                    h, w, ch = f.shape
                    qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888)
                    self.label.setPixmap(QPixmap.fromImage(qtf))

                    self.prevtime = time.time()
                    print(self.prevtime - self.ntime)

            except Exception as e:

                self.main.hist_gp.setTitle(" ")
                self.main.imagen.setText("No se ha detectado ninguna imagen")

                f = cv2.resize(f, (self.label.width(), self.label.height()))

                if self.main.invertir == 1: f = cv2.flip(f, 1)
                elif self.main.invertir == 0: f = f

                h, w, ch = f.shape
                qtf = QImage(f.data, w, h, ch*w, QImage.Format_RGB888) # qtf es la imagen que nos interesa.
                self.label.setPixmap(QPixmap.fromImage(qtf))

                self.prevtime = time.time()               
                print(self.prevtime - self.ntime)
