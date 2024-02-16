from sve import *

ofseti, baze, duzi = [],[],[]
kords = []
z_ploca = -15.0
z_monitora = -0.257

Loffseti, Doffseti, Lbaze, Dbaze, Lduzi, Dduzi = ucitaj_offsete_i_baze("resursi/kalibracija.txt")

snimak = cv2.VideoCapture(0)
detector = dlib.simple_object_detector("resursi/d.svm")
predictor = dlib.shape_predictor("resursi/d.dat")

while True:
    _,slika = snimak.read()
    slika, niz = provuci_kroz_ai(detector, predictor, slika, z_ploca)
    
    cv2.imshow("Q za gasenje", slika)

    kor = mis_offset(niz, 1, z_ploca, z_monitora, Loffseti, Lduzi, Lbaze)
    kords.append(kor)
    kor = mis_offset(niz, 4, z_ploca, z_monitora, Doffseti, Dduzi, Dbaze)
    kords.append(kor)

    kords = saberi_listu(kords)
    kords = podeli_listu(kords, 2)
    kords = razlika_tacaka(tackice_monitor[0],kords)

    x = kords[0]/16.0*1920
    y = kords[1]/9.0*1080

    x,y = provera_x_y(x,y)

    pyautogui.moveTo(int(x),int(y))
    kords = []

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

snimak.release()
cv2.destroyAllWindows()