from sve import *

detector = dlib.simple_object_detector("resursi/d.svm")
predictor = dlib.shape_predictor("resursi/d.dat")
niz = []
brojac = 0
cap = cv2.VideoCapture(0)

while True:
    ret, slika = cap.read()
    kopija = cv2.cvtColor(slika,cv2.COLOR_BGR2GRAY)
    #pocetak = time.time()
    lica = detector(kopija)
    
    for l in lica:            
        #slika = pravouganik_oko_face(slika, l, zelena, 1)
        oznake = predictor(kopija,l)
        slika, niz = krugovi(slika, oznake, zelena, 2)

    slika = cv2.flip(slika, 1)
    cv2.imshow('DET:',slika)   
    #print("{:.2f}".format(time.time()-pocetak))
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    if cv2.waitKey(10) & 0xFF == ord('e'):
        cv2.imwrite("{}.jpg".format(brojac), slika)
        brojac += 1
    

cap.release()
cv2.destroyAllWindows()