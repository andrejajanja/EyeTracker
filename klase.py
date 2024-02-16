from numpy import radians
import numpy as np
from pyrr import Vector3, vector, vector3, matrix44
from math import sin, cos, radians

class Kamera:
    def __init__(self, x, y, z, yaw, osetljivost, napred, desno):
        '''
        x,y,z - inicijalna pozicija kamere\n
        yaw - yaw\n
        osetljivost - osetljivost misa
        '''
        self.pozicija = Vector3([x,y,z])
        self.napred = napred
        self.gore = Vector3([0.0,1.0,0.0])
        self.desno = desno

        self.osetljivost = osetljivost
        self.yaw = yaw
        self.pitch = 0
    
    def vrati_matricu_pogleda(self):
        return matrix44.create_look_at(self.pozicija, self.pozicija + self.napred, self.gore)

    def pomeranje_misa(self, xoffset, yoffset, limitiraj_pitch = True):
        xoffset *= self.osetljivost
        yoffset *= self.osetljivost
        self.yaw += xoffset
        self.pitch += yoffset

        if limitiraj_pitch:
            if self.pitch > 45:
                self.pitch = 45
            if self.pitch < -45:
                self.pitch = -45

        self.osvezi_vektore_kamere()

    def osvezi_vektore_kamere(self):
        napred = Vector3([0.0,0.0, 0.0])
        napred.x = cos(radians(self.yaw)) * cos(radians(self.pitch))
        napred.y = sin(radians(self.pitch))
        napred.z = sin(radians(self.yaw)) * cos(radians(self.pitch))

        self.napred = vector.normalise(napred)
        self.desno = vector.normalise(vector3.cross(self.napred, Vector3([0.0, 1.0, 0.0])))
        self.gore = vector.normalise(vector3.cross(self.desno, self.napred))

    def tastaturaZaWSAD(self, smer, brzina):
        if smer == "napred":
            self.pozicija[0] += self.napred[0]*brzina
            self.pozicija[2] += self.napred[2]*brzina

        if smer == "nazad":
            self.pozicija[0] -= self.napred[0]*brzina
            self.pozicija[2] -= self.napred[2]*brzina

        if smer == "levo":
            self.pozicija -= self.desno*brzina

        if smer == "desno":
            self.pozicija += self.desno*brzina

class Ucitavanje_obj:

    buffer = []

    @staticmethod
    def izvuci_brojeve_iz_liste(lista, zavrsava, tip):
        '''
        Argumenti:\n
        Lista <- lista odakle da se izvuku brojevi\n
        zavrsava <- lista u koju se ubacuju izvuceni brojevi\n
        tip <- (string) kog tipa brojevi treba da budu (float/int)\n
        '''
        for element in lista:
            if tip == 'float':
                zavrsava.append(float(element))
            elif tip == 'int':
                zavrsava.append(int(element)-1)

    @staticmethod
    def sortiran_vertex_buffer(cale, tack, teks, norm):
        '''
        OVA FUNKCIJA SE KORISTI KADA SE ZA CRTANJE OBLIKA KORISTI glDrawArrays()
        \nArgumenti:\n
        cale <- lista u kojoj su smestene vrednosti iz kolona koje pocinju sa f u .obj file-u\n
        tack <- lista sa kord svih tacaka\n
        tesk <- lista sa kord svih tekstura\n
        norm <- lista sa kord svih normala\n
        buffer <- lista koja ce se koristiti da se napuni OpenGLov buffer\n\n

        \nOblik buffera nakon izvrsavanja ove fje:\n
        Tac-x, Tac-y, Tac-z, Tex-u, Tex-v, Norm-x, Norm-y, Norm-z
        '''
        for i, index in enumerate(cale):
            if i%3 == 0:
                pocetak = index*3
                kraj = pocetak + 3 
                Ucitavanje_obj.buffer.extend(tack[pocetak:kraj])
            if i%3 == 1:
                pocetak = index*2
                kraj = pocetak + 2 
                Ucitavanje_obj.buffer.extend(teks[pocetak:kraj])
            if i%3 == 2:
                pocetak = index*3
                kraj = pocetak + 3 
                Ucitavanje_obj.buffer.extend(norm[pocetak:kraj])

    @staticmethod
    def nesortiran_vertex_buffer(cale, tack, teks, norm):
        print("Mora se uradi.")

    @staticmethod
    def ispisi_buffer():
        b = Ucitavanje_obj.buffer
        print("uradi")

    @staticmethod
    def ucitaj_obj(ime, sortirano = True, ispisi = False):
        '''
        \nSta radi:\n
        Ucitava .obj file u promenljive koje su spremne da se daju OpenGlu da nacrta sadrzaj datog filea.\n
        \nArgumenti:\n
        ime <- (string) ime .obj fila sa njegovom lokacijom\n
        \nsortirano <- (bool)(opciono)\n 
        True - output je prilagodjen koriscenju glDrawArray() \n
        False - output je prilagodjen koriscenju glDrawElements()\n
        \nispisi <- (bool)(opciono) \n
        True - ispisuje ceo buffer na terminal\n
        Flase - upisuje baffer u dve promenljive (tacke, indeksi)\n
        '''

        buffer = []

        f = open(ime, "r")
        linije = f.readlines()
        f.close()

        tacke = []
        teksture = []
        normale = []

        sve = []
        indeksi = []

        for linija in linije:
            linija = linija.split()
            if linija == []:
                continue
            if linija[0] == 'v':
                Ucitavanje_obj.izvuci_brojeve_iz_liste(linija[1:], tacke, 'float')
            elif linija[0] == 'vn':
                Ucitavanje_obj.izvuci_brojeve_iz_liste(linija[1:],normale, 'float')
            elif linija[0] == 'vt':
                Ucitavanje_obj.izvuci_brojeve_iz_liste(linija[1:-1],teksture, 'float')
            elif linija[0] == 'f':
                for l in linija[1:]:
                    l = l.split('/')
                    Ucitavanje_obj.izvuci_brojeve_iz_liste(l, sve, 'int')
                    indeksi.append(int(l[0])-1)

        if sortirano:
            Ucitavanje_obj.sortiran_vertex_buffer(sve, tacke, teksture, normale)
        else:
            Ucitavanje_obj.nesortiran_vertex_buffer(sve, tacke, teksture, normale)

        if ispisi:
            Ucitavanje_obj.ispisi_buffer()
        else:

            b = Ucitavanje_obj.buffer.copy()

            Ucitavanje_obj.buffer = []

            tacke = np.array(b, dtype=np.float32)
            indeksi = np.array(indeksi, dtype=np.uint32)
            return tacke, indeksi