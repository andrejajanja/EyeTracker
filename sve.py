import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '400,200'

#moji fileovi
from shaderi import *
from klase import *

#skinute biblioteke sa neta
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
from pyrr import Vector3
import math
from cv2 import cv2
import time
import dlib
from imutils import face_utils
import pyautogui
pyautogui.FAILSAFE = False

#KONSTANTE:
#boje su BGR sistemu
zelena = (0,255,0)
plava = (255,0,0)
crvena = (0,0,255)
k = 360.0/6.28
tackice_monitor = [
    [8.0, 4.5, -0.257459855079651],
    [-8.0, 4.5, -0.257459855079651],
    [-8.0, -4.5, -0.257459855079651],
    [8.0, -4.5, -0.257459855079651]
    ]

koec = 3
podes = 0

#FUNKCIJE:

def ucitaj_sliku(naziv):
    slika = cv2.imread(naziv)
    slika = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)
    slika = cv2.flip(slika, 0)
    slika_data = np.array(slika, dtype = np.float32)
    return slika_data, slika.shape[0], slika.shape[1]

def ucitaj_texturu(tex, naziv):
    slika_data, sirina, visina = ucitaj_sliku(naziv)

    glBindTexture(GL_TEXTURE_2D, tex)

    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, sirina, visina, 0, GL_RGB, GL_UNSIGNED_BYTE, slika_data)
    return tex

def ucitaj_teksturu_sa_kamere(tex, slika, rot_code = -10):
    '''
    \nrot_code:\n
    0 - po verticali flip\n
    1 - po horizontali flip\n
    -1 - flip i po vertikali i po horiznotali\n
    '''
    if not rot_code == -10:
        slika = cv2.flip(slika, rot_code)

    slika = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)

    slika_data = np.array(slika)

    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 640,480, 0, GL_RGB, GL_UNSIGNED_BYTE, slika_data)
    return tex

def ucitaj_model_opengl(vertarobj, vertbuffobj, tacke):
    glBindVertexArray(vertarobj)
    glBindBuffer(GL_ARRAY_BUFFER, vertbuffobj)
    glBufferData(GL_ARRAY_BUFFER, tacke.nbytes, tacke, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(20))

def ucitaj_liniju(vertarobj, vertbuffobj, tacke):
    glBindVertexArray(vertarobj)
    glBindBuffer(GL_ARRAY_BUFFER, vertbuffobj)
    glBufferData(GL_ARRAY_BUFFER, tacke.nbytes, tacke, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 3, ctypes.c_void_p(0))

def pozovi_ucitan_model_opengl(veratobj, teks, pozicija, shader_lok, ieksii, zastavica):
    '''
    veratobj - VAO za taj model\n
    teks - tekstura za taj model\n
    pozicija - pozicija koju daje korisnik, matrica\n
    shader_lok - argument za poziciju u samom vertex shaderu\n
    ieksii - indeksi dati ucitavanjem modela\n
    \nzastavica: FLAG za glDrawArrays
    '''
    glBindVertexArray(veratobj)
    glBindTexture(GL_TEXTURE_2D, teks)
    glUniformMatrix4fv(shader_lok, 1, GL_FALSE, pozicija)
    glDrawArrays(zastavica, 0 , len(ieksii))

def pozovi_liniju(veratobj, pozicija, shader_lok):
    glBindVertexArray(veratobj)
    glUniformMatrix4fv(shader_lok, 1, GL_FALSE, pozicija)
    glDrawArrays(GL_LINES, 0 , 2)

def pozicija_rotacija_razmera_modela(P = Vector3([0.0,0.0,0.0]), Teta = [0.0,0.0,0.0], S = 0.1):
    '''
    \nARGUMENTI:\n
    P je argument tipa Vector3 za poziciju.\n
    Teta - lista sa float uglovima u stepenima\n
    S je float scalar za koliko se scaluje dati model.\n

    \nVraca matrix44 tip podatka koji se direktno koristi kao pozicija modela.
    '''

    if not len(Teta) == 3:
        raise Exception("Niste lepo uneli listu za uglove rotacije modela.")

    #Rotacija
    k = 6.28/360
    rotacija_x= pyrr.matrix44.create_from_x_rotation(k*Teta[0])
    rotacija_y= pyrr.matrix44.create_from_y_rotation(k*Teta[1])
    rotacija_z= pyrr.matrix44.create_from_z_rotation(k*Teta[2])
    rotacija = pyrr.matrix44.multiply(rotacija_y, rotacija_z)
    rotacija = pyrr.matrix44.multiply(rotacija_x, rotacija)

    #pozicija i razmera
    pozicija = pyrr.matrix44.create_from_translation(P)
    razmera = pyrr.matrix44.create_from_scale(pyrr.Vector3([S,S,S]))

    #master
    model = pyrr.matrix44.multiply(razmera, rotacija)
    model = pyrr.matrix44.multiply(model, pozicija)

    return model

def pravouganik_oko_face(slika, lice, boja, debljina):
    x1 = lice.left()
    y1 = lice.top()
    x2 = lice.right()
    y2 = lice.bottom()
    cv2.rectangle(slika, (x1,y1), (x2,y2), boja, debljina)
    return slika
    
def krugovi(slika, oznake, bojaa, debljina):
    oznake = face_utils.shape_to_np(oznake)
    boja = bojaa
    deb = debljina
    niz = []
    #stavljanje tacaka
    for (x,y) in oznake:
        #if a != 1 and a != 4:
            #y -= 10
        niz.append((x,y))
        cv2.circle(slika, (x,y), deb+1,boja,-1)

    return slika, niz

def niz_tacke(oznake):
    oznake = face_utils.shape_to_np(oznake)
    niz = []
    for (x,y) in oznake:
        niz.append((x,y))
    return niz

def koef_krugovi(slika, niz, boja, debljina, koef, adj):
    pd = (niz[0][1]+niz[2][1])/2
    pl = (niz[3][1]+niz[5][1])/2
    razd = niz[1][1] - pd + 5
    razl = niz[4][1] - pl + 5 
    
    niz[0] = (niz[0][0], niz[0][1] + adj)
    niz[1] = (niz[1][0], int(pd + razd*koef))
    niz[2] = (niz[2][0], niz[2][1] + adj)
    niz[3] = (niz[3][0], niz[3][1] + adj)
    niz[4] = (niz[4][0], int(pl + razl*koef))
    niz[5] = (niz[5][0], niz[5][1] + adj)

    for (x,y) in niz:
        cv2.circle(slika, (x,y), debljina+1,boja,-1)
    return slika, niz

def pokazi_sliku(slika):
    while True:
        cv2.imshow('Q za gasenje prozora', slika)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def provuci_kroz_ai(detector, predictor, slika, z):
    slika = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)
    kopija = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
    lica = detector(kopija)
    niz = []

    for l in lica:
        slika = pravouganik_oko_face(slika, l, zelena, 1)
        oznake = predictor(kopija,l)
        slika, niz = krugovi(slika, oznake, zelena, 2)

    niz = skelet_koordinate_x_y_z(niz,z)

    return cv2.cvtColor(slika, cv2.COLOR_RGB2BGR), niz

def provuci_kroz_ai_koef(detector, predictor, slika, z, koef, ad):
    slika = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)
    kopija = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
    lica = detector(kopija)
    niz = []

    for l in lica:
        slika = pravouganik_oko_face(slika, l, zelena, 1)
        oznake = predictor(kopija,l)
        slika, niz = koef_krugovi(slika, niz_tacke(oznake), zelena, 2, koef, ad)

    niz = skelet_koordinate_x_y_z(niz,z)

    return cv2.cvtColor(slika, cv2.COLOR_RGB2BGR), niz

def skelet_koordinate_x_y_z(niz, z):
    '''
    Vraca prostorne koordinate tacaka spremnih da se koriste za pozicioniranje sfera\n
    !!KORISTI FUNKCIJU kord_zenice(niz, index_levo, centar,index_desno, z)!!
    '''
    if niz == []:
        niz = [
            (0.0,480.0),
            (80.0,480.0),
            (160.0,480.0),
            (320.0,480.0),
            (480.0,480.0),
            (560.0,480.0)]

    koordinate = []
    for (x,y) in niz:
        koordinate.append((float(x)/100.0-3.2,2.4-float(y)/100,z))

    koordinate[1] = kord_zenice(koordinate,0,1,2,z)
    koordinate[4] = kord_zenice(koordinate,3,4,5,z)
    return koordinate

def pozovi_ucitane_sfere_opengl(niz, z, raz, veratobj, teks, shader_lok, ieksii, zastavica):
    for kord in niz:
        lokacija = pozicija_rotacija_razmera_modela(P = Vector3(kord),S = raz)
        pozovi_ucitan_model_opengl(veratobj, teks, lokacija,shader_lok, ieksii, zastavica)

def d_2D(a,b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x*x + y*y)

def jednako_2D(a,b):
    '''
    Vraca koordinate tacke koja je podjenako udeljana od ponudjene dve\n
    (x,y)
    '''
    x = (a[0]+b[0])/2
    y = (a[1]+b[1])/2 
    return (x,y+0.1)

def kord_zenice(niz, index_levo, centar,index_desno, z):
    '''
    Vraca prostorne koordinate tacke koja predstavlja centar zenice\n
    (x,y,z)
    '''
    Ct = niz[centar]
    r = d_2D(niz[index_levo], niz[index_desno])/2
    At = jednako_2D(niz[index_levo], niz[index_desno])
    a = At[0]-Ct[0]
    c = At[1]-Ct[1]
    #print(r*r, c*c, a*a)
    k = math.sqrt(r*r - c*c - a*a)

    Ct = [Ct[0], Ct[1], z + k]
    return Ct

def prava_preko_z(At,Ct):
    '''
    Vraca k i n za dve 2D prave koji se koriste za generisanje 3D prave:\n
    xk, yk, xn, yn
    '''
    xk = (Ct[0]-At[0])/(Ct[2]-At[2])
    yk = (Ct[1]-At[1])/(Ct[2]-At[2])
    xn = At[0] - Ct[2]*xk 
    yn = At[1] - Ct[2]*xk 
    return xk,yk, xn, yn

def vrati_offsete_kord(Ct,At, Tm, z_mon):
    '''
    Ct - zenica\n
    At - centar oka\n
    Tm - tacka sa koordinatama ugla monitora\n
    '''
    xk,yk, xn, yn = prava_preko_z(At,Ct)
    x = xk*z_mon + xn
    y = yk*z_mon + yn
    ofsetx = Tm[0] - x 
    ofsety = Tm[1] - y
    return ofsetx, ofsety, x, y

def upisi_offsete(niz_oci, index_z1, index_z2, z_polca, z_monitor, tac, radi_li, prozor, f):

    if not radi_li:
        return False, tac
    
    Tm = tackice_monitor[tac]
    x,y = jednako_2D(niz_oci[index_z1-1], niz_oci[index_z1+1])
    At = (x,y,z_polca)
    Ct = niz_oci[index_z1]
    offset_x, offset_y, baza_x, baza_y = vrati_offsete_kord(Ct, At, Tm, z_monitor)
    #print(offset_x, offset_y, baza_x, baza_y)
    f.write("{} {} {} {}\n".format(offset_x, offset_y, baza_x, baza_y))

    x,y = jednako_2D(niz_oci[index_z2-1], niz_oci[index_z2+1])
    At = (x,y,z_polca)
    Ct = niz_oci[index_z2]
    offset_x, offset_y, baza_x, baza_y = vrati_offsete_kord(Ct, At, Tm, z_monitor)
    #print(offset_x, offset_y, baza_x, baza_y)
    f.write("{} {} {} {}\n".format(offset_x, offset_y, baza_x, baza_y))
    return False, tac + 1

def duzina_vektora(vektor):
    return math.sqrt(vektor[0]*vektor[0] + vektor[1]*vektor[1])

def izdvoj_x(o):
    mo = []
    for a in range(0,len(o)):
        if a%2 == 0:
            mo.append(o[a])
    return mo

def izdvoj_y(o):
    mo = []
    for a in range(0,len(o)):
        if a%2 != 0:
            mo.append(o[a])
    return mo

def ucitaj_offsete_i_baze(fajl):
    '''
    \nCita sve podatke iz tekstualnog filea i ubacuje ih u 4 liste:\n
    Loffseti: offseti za levo oko\n
    Doffseti: offseti za desno oko\n
    Lbaze: baze za levo oko\n
    Dbaze: baze za desno oko\n
    '''
    offseti, baze = [], []

    f = open(fajl, "r")
    linije = f.readlines()
    f.close()

    for l in linije:
        l = l.split()
        offseti.append((float(l[0]), float(l[1])))
        baze.append((float(l[2]), float(l[3])))

    Loffseti = izdvoj_x(offseti)
    Doffseti = izdvoj_y(offseti)

    Lbaze = izdvoj_x(baze)
    Dbaze = izdvoj_y(baze)

    Lduzi = ucitaj_duzi_elemente_oka(Lbaze)
    Dduzi = ucitaj_duzi_elemente_oka(Dbaze)

    return Loffseti, Doffseti, Lbaze, Dbaze, Lduzi, Dduzi

def razlika_tacaka(t1, t2):
    rx = t1[0] - t2[0]
    ry = t1[1] - t2[1]
    return (rx, ry)

def ucitaj_duzi_elemente_oka(baze):
    '''
    \nSMESTA DUZINE SVIH DUZI JEDNOG OKA U JEDNU LISTU\n\n
    \nduzine svih bitnih duzi u listi "duzi":\n
    0 - AB\n
    1 - BC\n
    2 - CD\n
    3 - DA\n
    4 - BD\n
    5 - AC\n
    '''
    duzi = []

    duzi.append(duzina_vektora(razlika_tacaka(baze[0], baze[1])))
    duzi.append(duzina_vektora(razlika_tacaka(baze[2], baze[1])))
    duzi.append(duzina_vektora(razlika_tacaka(baze[2], baze[3])))
    duzi.append(duzina_vektora(razlika_tacaka(baze[3], baze[0])))
    duzi.append(duzina_vektora(razlika_tacaka(baze[1], baze[3])))
    duzi.append(duzina_vektora(razlika_tacaka(baze[2], baze[0])))

    return duzi

def izracunaj_offset(x, y, offseti, duzi, baze):
    t = (x,y)
    at = duzina_vektora(razlika_tacaka(baze[0], t))
    bt = duzina_vektora(razlika_tacaka(baze[1], t))
    ct = duzina_vektora(razlika_tacaka(baze[2], t))
    dt = duzina_vektora(razlika_tacaka(baze[3], t))

    off = []
    off.append(pomnozi_listu(offseti[0], (1-at/duzi[5])*(1-at/duzi[0])*(1-at/duzi[3])))
    off.append(pomnozi_listu(offseti[1], (1-bt/duzi[4])*(1-bt/duzi[0])*(1-bt/duzi[1])))
    off.append(pomnozi_listu(offseti[2], (1-ct/duzi[5])*(1-ct/duzi[1])*(1-ct/duzi[2])))
    off.append(pomnozi_listu(offseti[3], (1-dt/duzi[4])*(1-dt/duzi[2])*(1-dt/duzi[3])))

    return saberi_listu(off)

def sfera_sa_kord(x, y, z_monitor, VAO, shader_lok, tekstura, indeksi):
    kords = pozicija_rotacija_razmera_modela(P = Vector3([x,y,z_monitor]),S = 0.003)
    pozovi_ucitan_model_opengl(VAO, tekstura, kords, shader_lok, indeksi, GL_TRIANGLES)

def nacrtaj_sferu_na_monitoru_sa_offsetom(niz, index_zenice, z_polca, z_monitor, VAO, shader_lok, tekstura, indeksi, offseti, duzi, baze):
    '''
    \nArgumenti:\n
    niz - niz sa svih 6 obradjenih tacaka koje je dao AI\n
    index_zenice - index na kom se nalazi tacka centra levog ili desnog oka\n
    z - (float) z komponenta koordinata ploce\n
    '''
    x,y = jednako_2D(niz[index_zenice-1], niz[index_zenice+1])

    Ct = niz[index_zenice]
    At = (x,y,z_polca)
    xk ,yk, xn, yn = prava_preko_z(At,Ct)

    x = xk*z_monitor + xn
    y = yk*z_monitor + yn

    dx, dy = izracunaj_offset(x, y, offseti, duzi, baze)
    x += dx
    y += dy

    kords = pozicija_rotacija_razmera_modela(P = Vector3([x,y,z_monitor]),S = 0.003)
    pozovi_ucitan_model_opengl(VAO, tekstura, kords, shader_lok, indeksi, GL_TRIANGLES)

    return (x,y)

def mis_offset(niz, index_zenice, z_polca, z_monitor, offseti, duzi, baze):
    x,y = jednako_2D(niz[index_zenice-1], niz[index_zenice+1])

    Ct = niz[index_zenice]
    At = (x,y,z_polca)
    xk ,yk, xn, yn = prava_preko_z(At,Ct)

    x = xk*z_monitor + xn
    y = yk*z_monitor + yn

    dx, dy = izracunaj_offset(x, y, offseti, duzi, baze)
    x += dx
    y += dy
    return (x,y)

def nacrtaj_sferu_na_monitoru(niz, index_zenice, z_polca, z_monitor, VAO, shader_lok, tekstura, indeksi):
    '''
    \nArgumenti:\n
    niz - niz sa svih 6 obradjenih tacaka koje je dao AI\n
    index_zenice - index na kom se nalazi tacka centra levog ili desnog oka\n
    z - (float) z komponenta koordinata ploce\n
    '''
    x,y = jednako_2D(niz[index_zenice-1], niz[index_zenice+1])

    Ct = niz[index_zenice]
    At = (x,y,z_polca)
    xk ,yk, xn, yn = prava_preko_z(At,Ct)

    x = xk*z_monitor + xn
    y = yk*z_monitor + yn

    kords = pozicija_rotacija_razmera_modela(P = Vector3([x,y,z_monitor]),S = 0.003)
    pozovi_ucitan_model_opengl(VAO, tekstura, kords, shader_lok, indeksi, GL_TRIANGLES)

def ispisi_listu(lista):
    for i in range(len(lista)):
        print(lista[i])

def saberi_listu(ofset):
    x, y = 0.0,0.0
    for elem in ofset:
        x += elem[0]
        y += elem[1]
    return x,y

def pomnozi_listu(lista, k):
    return [element * k for element in lista]

def podeli_listu(lista, k):
    return [element / k for element in lista]

def provera_x_y(x, y):
    if x > 1920:
        x = 1920
    if x < 0:
        x = 0
    if y > 1080:
        y = 1080
    if y < 0:
        y = 0
    return x,y

#REZERVA
#slika, niz = provuci_kroz_ai_koef(detector, predictor, slika, z_ploca, koec, podes)