from sve import *


if not glfw.init():
    raise Exception("ne moze da inicijalizuje glfw")

prozor = glfw.create_window(1280, 720, "Prozor", None, None)

if not prozor:
    glfw.terminate()
    raise Exception("ne radi prozor")

glfw.set_window_pos(prozor,400,200)
glfw.set_window_size_callback(prozor, prozor_resize)
glfw.make_context_current(prozor)



tacke = np.array(tacke, dtype = np.float32)
indeksi = np.array(indeksi, dtype = np.uint32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, tacke.nbytes, tacke, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indeksi.nbytes, indeksi, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, tacke.itemsize * 8, ctypes.c_void_p(24))


tekstura = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, tekstura)

glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

slika, x, y = ucitaj_sliku("teksture/drvo.jpg")
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, x, y, 0, GL_RGB, GL_UNSIGNED_BYTE, slika)


glUseProgram(shader)
glClearColor(0,0.2,0.2,1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)

rotacija = glGetUniformLocation(shader, "rotation")

while not glfw.window_should_close(prozor):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT)

    rotacija_x = pyrr.Matrix44.from_x_rotation(0.5*glfw.get_time())
    rotacija_y = pyrr.Matrix44.from_y_rotation(0.8*glfw.get_time())

    glUniformMatrix4fv(rotacija, 1, GL_FALSE, pyrr.matrix44.multiply(rotacija_x, rotacija_y))

    glDrawElements(GL_TRIANGLES, len(indeksi), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(prozor)

glfw.terminate()