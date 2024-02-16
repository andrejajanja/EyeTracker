from sve import *
import pygame
tacke, indeksi = ucitaj_obj("modeli/kocka.obj")

pygame.init()
pygame.display.set_mode((1280,720), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))


VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)
#EBO = glGenBuffers(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, tacke.nbytes, tacke, GL_STATIC_DRAW)

#glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
#glBufferData(GL_ELEMENT_ARRAY_BUFFER, indeksi.nbytes, indeksi, GL_STATIC_DRAW)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(20))

tekstura = glGenTextures(1)
kocka1_teksura = ucitaj_texturu(tekstura, "teksture/kockaColor.jpg")

glUseProgram(shader)
glClearColor(0,0.2,0.2,1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)

lokacija_modela = glGetUniformLocation(shader, "model")
mat_projekcije = glGetUniformLocation(shader, "projection")
lokacija_pogleda = glGetUniformLocation(shader, "view")

kocka1 = pyrr.matrix44.create_from_translation(pyrr.Vector3([0,0,0]))
razmera = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.01,0.01,0.01]))
kocka1 = pyrr.matrix44.multiply(razmera,kocka1)


pogled = pyrr.matrix44.create_look_at(pyrr.Vector3([0,0,-5]),pyrr.Vector3([0,0,0]),pyrr.Vector3([0,1,0]))


projekcija = pyrr.matrix44.create_perspective_projection_matrix(45, 1280/720, 0.1, 100.0)
glUniformMatrix4fv(mat_projekcije, 1, GL_FALSE, projekcija)
glUniformMatrix4fv(lokacija_pogleda, 1, GL_FALSE, pogled)

ide = True
while ide:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ide = False

        if event.type == pygame.VIDEORESIZE:
            glViewport(0,0, event.w, event.h)
            projekcija = pyrr.matrix44.create_perspective_projection_matrix(45, event.w/event.h, 0.1, 100.0)
            glUniformMatrix4fv(mat_projekcije, 1, GL_FALSE, projekcija)

    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT)

    vreme = pygame.time.get_ticks() / 1000

    #rotacija_x = pyrr.Matrix44.from_x_rotation(0.5*vreme)
    #rotacija_y = pyrr.Matrix44.from_y_rotation(0.8*vreme)

    #rotacija = pyrr.matrix44.multiply(rotacija_x, rotacija_y)
    #model = pyrr.matrix44.multiply(razmera, rotacija)
    #model = pyrr.matrix44.multiply(model, translacija)
    

    glBindVertexArray(VAO)
    #glBindTexture(GL_TEXTURE_2D, tekstura)
    glUniformMatrix4fv(lokacija_modela, 1, GL_FALSE, kocka1)
    glDrawArrays(GL_TRIANGLES, 0 , len(indeksi))
    #glDrawElements(GL_TRIANGLES, len(indeksi), GL_UNSIGNED_INT, None)

    x = math.sin(vreme)*5
    z = math.cos(vreme)*5

    pogled = pyrr.matrix44.create_look_at(pyrr.Vector3([x,3,z]),pyrr.Vector3([0,0,0]),pyrr.Vector3([0,1,0]))
    glUniformMatrix4fv(lokacija_pogleda, 1, GL_FALSE, pogled)

    pygame.display.flip()
    
pygame.quit()