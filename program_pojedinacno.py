from sve import *

kamera = Kamera(0.0,4.0,-20.0,90.0,0.25, Vector3([0.0,0.0,1.0]), Vector3([0.0,0.0,1.0]))
#kamera = Kamera(-10.0,2.0,-10.0,0.0,0.25, Vector3([1.0,0.0,0.0]), Vector3([1.0,0.0,0.0]))
#region deklaracija nekih elementarnih stvari
sirina,visina = 1280,720 #prozora u kome je program
poslednjex, poslednjey = sirina/2 , visina/2
prvi_mis = True
fov = 50 #stepeni za inicijalni field of view
brzo = 0.5 #parametar za brzinu pomeranja preko WSAD
ofseti, baze, duzi = [],[],[]
kords = []
#endregion deklaracija nekih elementarnih stvari

#region ucitavanja modela i kalibracionih elemenata
tacke_monitor, indeksi_monitor = Ucitavanje_obj.ucitaj_obj("resursi/monitor.obj")
tacke_ploca, indeksi_ploca = Ucitavanje_obj.ucitaj_obj("resursi/ploca.obj")
tacke_sfera, indeksi_sfera = Ucitavanje_obj.ucitaj_obj("resursi/sfera.obj")

Loffseti, Doffseti, Lbaze, Dbaze, Lduzi, Dduzi = ucitaj_offsete_i_baze("resursi/kalibracija.txt")
#endregion ucitavanja modela i kalibracionih elemenata

#region inicijalizacije svega
napred, nazad, levo, desno = False, False, False, False

def mis_pogled_callback(prozor, xpos, ypos):
    global prvi_mis, poslednjex, poslednjey

    if prvi_mis:
        poslednjex = xpos
        poslednjey = ypos
        prvi_mis = False

    xoffset = xpos - poslednjex
    yoffset = poslednjey - ypos

    poslednjex = xpos
    poslednjey = ypos

    kamera.pomeranje_misa(xoffset,yoffset)

def prozor_promena_velicine(prozor, sirina, visina):
    glViewport(0, 0, sirina, visina)
    projection = pyrr.matrix44.create_perspective_projection_matrix(fov, sirina / visina, 0.1, 100)
    glUniformMatrix4fv(lokacija_pogleda, 1, GL_FALSE, projection)

def pritisak_dugmeta(prozor, dugme, scancode, akcija, mode):
    global napred, nazad, levo, desno

    if dugme == glfw.KEY_ESCAPE and akcija == glfw.PRESS:
        glfw.set_window_should_close(prozor, True)

    if dugme == glfw.KEY_W and akcija == glfw.PRESS:
        napred = True
    if dugme == glfw.KEY_S and akcija == glfw.PRESS:
        nazad = True
    if dugme == glfw.KEY_A and akcija == glfw.PRESS:
        levo = True
    if dugme == glfw.KEY_D and akcija == glfw.PRESS:
        desno = True
    if dugme in [glfw.KEY_W,glfw.KEY_S,glfw.KEY_A,glfw.KEY_D] and akcija == glfw.RELEASE:
        napred, nazad, levo, desno = False, False, False, False
    
def promena_fova(prozor, x, y):
    global fov
    fov -= int(y)

def kretanje():
    if napred == True:
        kamera.tastaturaZaWSAD("napred", brzo)
    if nazad == True:
        kamera.tastaturaZaWSAD("nazad", brzo)
    if levo == True:
        kamera.tastaturaZaWSAD("levo", brzo)
    if desno == True:
        kamera.tastaturaZaWSAD("desno", brzo)

if not glfw.init():
    raise Exception("glfw nije inicijalizovan")

prozor = glfw.create_window(sirina, visina, "Look™ by Janja", None, None)
glfw.make_context_current(prozor)
glfw.set_window_pos(prozor, 400, 200)
glfw.set_window_size_callback(prozor, prozor_promena_velicine)
glfw.set_cursor_pos_callback(prozor, mis_pogled_callback)
glfw.set_key_callback(prozor, pritisak_dugmeta)
glfw.set_scroll_callback(prozor, promena_fova)
glfw.set_input_mode(prozor, glfw.CURSOR, glfw.CURSOR_DISABLED)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
glfw.swap_interval(1)

if not prozor:
    glfw.terminate()
    raise Exception("glfw prozor nije uspeo da se kreira")

snimak = cv2.VideoCapture(0)
shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
VAO = glGenVertexArrays(3)
VBO = glGenBuffers(3)
tekstura = glGenTextures(3)

glUseProgram(shader)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
lokacija_modela = glGetUniformLocation(shader, "model")
mat_projekcije = glGetUniformLocation(shader, "projection")
lokacija_pogleda = glGetUniformLocation(shader, "view")
projekcija = pyrr.matrix44.create_perspective_projection_matrix(fov, sirina/visina, 0.1, 100.0)
glUniformMatrix4fv(mat_projekcije, 1, GL_FALSE, projekcija)

detector = dlib.simple_object_detector("resursi/d.svm")
predictor = dlib.shape_predictor("resursi/d.dat")
#endregion inicijalizacije svega

#region ucitavanje modela i njihovih tekstura
ucitaj_model_opengl(VAO[0],VBO[0], tacke_monitor)
monitor_tex = ucitaj_texturu(tekstura[0], "resursi/monitorColor.jpg")
ucitaj_model_opengl(VAO[1], VBO[1],tacke_ploca)
ucitaj_model_opengl(VAO[2], VBO[2], tacke_sfera)
sfera_tex = ucitaj_texturu(tekstura[2], "resursi/sferaColor.jpg")
#endregion ucitavanje modela i njihovih tekstura

z_ploca = -15.0
z_monitora = -0.257
ploca_poz_modela = pozicija_rotacija_razmera_modela(P = Vector3([0.0,0.0,z_ploca]))
monitor_poz_modela = pozicija_rotacija_razmera_modela()

linija_poz_modela = pozicija_rotacija_razmera_modela(P = Vector3([0.0,0.0,z_ploca]),Teta = [0,0,0])
glClearColor(0.6,0.6,0.6,1)

kords = []
brojac = 0

while not glfw.window_should_close(prozor):
    
    if brojac == 10:
        brojac = 0

    slika = cv2.imread("{}.jpg".format(brojac))
    time.sleep(0.2)
    slika, niz = provuci_kroz_ai(detector, predictor, slika, z_ploca)
    brojac += 1

    ploca_tex = ucitaj_teksturu_sa_kamere(tekstura[1], slika)
    glfw.poll_events()
    kretanje()
    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)
    glUniformMatrix4fv(lokacija_pogleda, 1, GL_FALSE, kamera.vrati_matricu_pogleda())

    projekcija = pyrr.matrix44.create_perspective_projection_matrix(fov, sirina/visina, 0.1, 100.0)
    glUniformMatrix4fv(mat_projekcije, 1, GL_FALSE, projekcija)

    pozovi_ucitan_model_opengl(VAO[0], tekstura[0], monitor_poz_modela, lokacija_modela, indeksi_monitor, GL_TRIANGLES)
    pozovi_ucitan_model_opengl(VAO[1], tekstura[1],ploca_poz_modela,lokacija_modela,indeksi_ploca, GL_QUADS)

    kor = mis_offset(niz, 1, z_ploca, z_monitora, Loffseti, Lduzi, Lbaze)
    kords.append(kor)
    kor = mis_offset(niz, 4, z_ploca, z_monitora, Doffseti, Dduzi, Dbaze)
    kords.append(kor)

    kords = saberi_listu(kords)
    kords = podeli_listu(kords, 2)
    kords = razlika_tacaka(tackice_monitor[0],kords)

    x = kords[0]
    y = kords[1]
    kords = []

    sfera_sa_kord(x, y, z_monitora, VAO[2], lokacija_modela, tekstura[2], indeksi_sfera)
    glfw.swap_buffers(prozor)
    
glfw.terminate()
snimak.release()