import time
import numpy as np
import bpy

print('------------------------>>>')
def timer(fun, message, iters=10000):
    T = time.time()
    for x in range(iters):
        fun()
    return(time.time()-T, message)


def get_co(ob, arr=None):
    """Returns vertex coords as N x 3"""
    c = len(ob.data.vertices)
    if arr is None:    
        arr = np.zeros(c * 3, dtype=np.float64)
    ob.data.vertices.foreach_get('co', arr.ravel())
    arr.shape = (c, 3)
    return arr

ob = bpy.context.object
co  = get_co(ob)

def apply_transforms():
    """Get vert coords in world space"""
    m = np.array(ob.matrix_world)    
    mat = m[:3, :3].T # rotates backwards without T
    loc = m[:3, 3]
    return co @ mat + loc


def matrix_world_list():
    m = ob.matrix_world
    co = [m * v.co for v in ob.data.vertices]


def matrix_world_loop():
    m = ob.matrix_world
    for i in ob.data.vertices:
        co = m * i.co


def move_verts_python():
    ob = bpy.context.object
    for x in range(100):    
        for i in ob.data.vertices:
            i.co[2] += .0001


def move_verts_numpy():
    ob = bpy.context.object
    co = get_co(ob)
    for x in range(100):    
        co[:, :2] += .0001
    ob.data.vertices.foreach_set('co', co.ravel())
    ob.data.update()


def generate_list():
    list(range(50000))


def generate_list_numpy():
    np.arange(50000)

# compare get array of coords with matrix world:
# !!!! try it on mesh with four verts then one with 10000 !!!
matrix = True
#matrix = False
if matrix:
    x = timer(apply_transforms, 'apply matrix world with numpy', 10)
    y = timer(matrix_world_list, 'apply matrix world with list_comp', 10)
    z = timer(matrix_world_loop, 'apply matrix world with loop', 10)
    print(x)
    print(y)
    print('numpy is ' + str(y[0]/x[0]) + ' times faster lan list comp')    
    print('numpy is ' + str(z[0]/x[0]) + ' times faster lan list comp')    
    print()
    print('-----------------------------------------')


# timer(move_verts_python, 'move verts with loop')
# !!! compare with light mesh and dense mesh !!! 
move = True
move = False
if move:
    x = timer(move_verts_numpy, 'move verts numpy', 1)
    y = timer(move_verts_python, 'move verts loop', 1)
    print(x)
    print(y)
    print('numpy is ' + str(y[0]/x[0]) + ' times faster')    
    print()
    print('-----------------------------------------')


gen_list = True
#gen_list = False
if gen_list:
    # timer generate list
    x = timer(generate_list_numpy, 'generate list numpy', 1000)
    y = timer(generate_list, 'generate list', 1000)
    print(x)
    print(y)
    print('numpy is ' + str(y[0]/x[0]) + ' times faster')
    print()
    print('-----------------------------------------')
