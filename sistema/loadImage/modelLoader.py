import cv2
import numpy as np
import tensorflow as tf

from tensorflow.lite.python.interpreter import Interpreter

class cvModel():

    def __init__(self, path, umbral):

        self.umbral = umbral

        self.path = path
        self.inter = Interpreter(self.path)
        self.inter.allocate_tensors()

        self.input = self.inter.get_input_details()
        self.output = self.inter.get_output_details()

        self.input_h = self.input[0]['shape'][1]
        self.input_w = self.input[0]['shape'][1]

    def getDims(self): return self.input_h, self.input_w # Regresa las dimensiones.

    def findBoxes(self, input):

        input_mean = 127.5
        input_std = 127.5
        input = (np.float32(np.expand_dims(input, axis = 0)) - input_mean)/input_std

        self.inter.set_tensor(self.input[0]['index'], input)
        self.inter.invoke()
        
        boxes = self.inter.get_tensor(self.output[1]['index'])[0] # Cajas encontradas.
        classes = self.inter.get_tensor(self.output[3]['index'])[0] # Clases encontradas.
        scores = self.inter.get_tensor(self.output[0]['index'])[0] # Score del analisis.
        
        umbralScore = np.where((scores > self.umbral) == True) # Obtenemos los indices donde nos dio True (encontramos el objeto deseado).
        
        scoresUmbral = [scores[i] for i in umbralScore[0]] # Obtenemos los scores.
        boxUmbral = [boxes[i] for i in umbralScore[0]]  # Obtenemos las cajas.
        classUmbral = [classes[i] for i in umbralScore[0]] # Obtenemos las clases.

        return scoresUmbral, boxUmbral, classUmbral

class segmentationModel():

    def __init__(self, path):

        self.path = path
        self.inter = Interpreter(self.path)
        self.inter.allocate_tensors()

        self.input = self.inter.get_input_details()
        self.output = self.inter.get_output_details()

        self.input_h = self.input[0]['shape'][1]
        self.input_w = self.input[0]['shape'][2]
        
        self.output_h = self.output[0]['shape'][1]
        self.output_w = self.output[0]['shape'][2]

    def getDims(self): return self.input_h, self.input_w

    def getOutputDims(self): return self.output_h, self.output_w

    def predict(self, entrada, contornos = True):

        entrada = np.float32(entrada[tf.newaxis, ...][..., tf.newaxis])

        self.inter.set_tensor(self.input[0]['index'], entrada)
        self.inter.invoke() # Mandamos a llamar al modelo.

        resultado = self.inter.get_tensor(self.output[0]['index'])[0]
        _, thresh = cv2.threshold(resultado, 0.2, 1, cv2.THRESH_BINARY)

        if contornos == True:
        
            c, _ = cv2.findContours(np.uint8(thresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            return c # Los contornos.
        
        elif contornos == False: return np.uint8(thresh) # La máscara como un uint8.

class diagnosticModel():

    def __init__(self, path) -> None:

        self.path = path
        self.inter = Interpreter(self.path)
        self.inter.allocate_tensors()

        self.input = self.inter.get_input_details()
        self.output = self.inter.get_output_details()

        self.h, self.w = self.input[0]['shape'][1], self.input[0]['shape'][2]

    def getDims(self): return self.h, self.w

    def predict(self, entrada):

        entrada = np.float32(entrada[tf.newaxis, ...][..., tf.newaxis])
        self.inter.set_tensor(self.input[0]['index'], entrada)
        self.inter.invoke()

        resultado = self.inter.get_tensor(self.output[0]['index'])[0]
        
        return resultado

