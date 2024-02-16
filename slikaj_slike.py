from sve import *

cap = cv2.VideoCapture(0)

brojac = 0
b = 0

while True:
    _, slika = cap.read()
    cv2.imshow('Fenster',slika)

    #slike za test
    if cv2.waitKey(10) & 0xFF == ord('e'):
        cv2.imwrite("{}.jpg".format(brojac), slika)
        brojac += 1

    #slike za kalibraciju
    if cv2.waitKey(10) & 0xFF == ord('d'):
        cv2.imwrite("kal_{}.jpg".format(b), slika)
        b += 1

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()