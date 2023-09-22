import cv2

import numpy as np

from tensorflow.lite.python.interpreter import Interpreter

def imagen(file):

    imagen = cv2.resize(cv2.imread(filename = file), (512, 512))

    cv2.imshow('image', imagen)

    cv2.waitKey(0)

def iniciarCamara(checkState):

    cam = cv2.VideoCapture(0)
    imH, imW = 480, 640
    umbral = 0.85
    
    modelos = cargarModelos(checkState, umbral)
    
    if np.shape(modelos) == (3,): modelo, height, width = modelos[0], modelos[1], modelos[2]

    while True:

        ret, frame = cam.read() # Obtenemos el frame.

        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            
            break

    cam.release()
    cv2.destroyAllWindows()

def resultados(modelos, frame):

    umbral = 0.85
    input_mean = 127.5
    input_std = 127.5

    if np.shape(modelos) == (5,): 
        
        modelo, height, width, idet, odet = modelos[0], modelos[1], modelos[2], modelos[3], modelos[4]

        frame = cv2.flip(frame, 1) # Lo volteamos, para que no esté en modo espejo.
        rz = cv2.resize(frame, (width, height)) # Resize del frame para la entrada a la red de detección de objetos.
        input = (np.float32(np.expand_dims(rz, axis = 0)) - input_mean)/input_std # Normalizamos la imagen.

        modelo.set_tensor(idet[0]['index'], input)
        modelo.invoke()
        
        boxes = modelo.get_tensor(odet[1]['index'])[0] # Cajas encontradas.
        classes = modelo.get_tensor(odet[3]['index'])[0] # Clases encontradas.
        scores = modelo.get_tensor(odet[0]['index'])[0] # Score del analisis.

        umbralScore = np.where((scores > umbral) == True) # Obtenemos los indices donde nos dio True (encontramos el objeto deseado).
        boxUmbral = [boxes[i] for i in umbralScore[0]]  # Obtenemos las cajas.
        classUmbral = [int(classes[i]) for i in umbralScore[0]] # Obtenemos las clases.

def cargarModelos(checkState, umbral): # Función para determinar que modelos cargar.

    if checkState[-1] == 0: # No está cargado el 4fun.

        print("no todos")

    elif np.sum(checkState) == 2 and checkState[-1] == 2: # Cargado solamente 4 fun.

        print("solo for fun")

        model4funpath = 'C:/Users/abcar/Desktop/casi TODO/ESCUELA/INTERNADO/Modelos/4fun/personas1/detect.tflite'
        
        funInt = Interpreter(model_path = model4funpath)
        funInt.allocate_tensors()

        idet, odet = funInt.get_input_details(), funInt.get_output_details()
        height, width = idet[0]['shape'][1], idet[0]['shape'][2]

        fi = (idet[0]['dtype'] == np.float32)

        return [funInt, height, width, idet, odet]

