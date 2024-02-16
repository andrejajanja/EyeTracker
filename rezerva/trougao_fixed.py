import glfw
from OpenGL.GL import *
import numpy as np
if not glfw.init():
    raise Exception("ne moze da inicijalizuje glfw")

prozor = glfw.create_window(1280, 720, "Prozor", None, None)

if not prozor:
    glfw.terminate()
    raise Exception("ne radi prozor")

glfw.set_window_pos(prozor,400,200)

glfw.make_context_current(prozor)

tacke = [
    -0.5,-0.5,0.0,
    0.5,-0.5,0.0,
    0.0,0.5,0.0
    ]

boje = [
    1.0,0.0,0.0,
    0.0,1.0,0.0,
    0.0,0.0,1.0
    ]

tacke = np.array(tacke, dtype = np.float32)
boje = np.array(boje, dtype = np.float32)

glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3,GL_FLOAT,0, tacke)
glEnableClientState(GL_COLOR_ARRAY)
glColorPointer(3, GL_FLOAT, 0, boje)

glClearColor(0,0.2,0.2,1)

while not glfw.window_should_close(prozor):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glRotatef(2,0,1,0)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glfw.swap_buffers(prozor)

glfw.terminate()