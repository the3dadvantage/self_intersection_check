import bpy
import time
current_time = time.time()
print('-------------start--------------')



bpy.types.Object.recursion_count = bpy.props.IntProperty()
bpy.context.object.recursion_count = 0
ticker = 0
start = True
extra_edges = ['not used']
collect = set()
new_count = set()
new_count2 = set()

def self_intersect_to_vert_group(obj, v_group):
    """Assign weight to vertex group if vertices are
    part of faces that self-intersect"""
    
    global start, extra_edges, collect, new_count, new_count2
    ray_cast = obj.ray_cast
    # For setting the error margin of the raycast
    EPS_NORMAL = 0.005
    EPS_CENTER = 0.01  # should always be bigger

    if start == True:
        check_edges =[ed for ed in obj.data.edges]
        print(11111111)
        #print('This is check edges11111111111',check_edges)
    elif start ==False: #and ticker ==0:
        #print("scene edges",bpy.types.Scene.collision_edges)
        check_edges = [ed for ed in obj.data.edges if ed.index in bpy.types.Scene.collision_edges]
        #print('This is check edges',check_edges)
        print(22222222)    
    else:
        check_edges = [ed for ed in obj.data.edges if ed.index in extra_edges]   
        #print('This is check edges33333333',check_edges)
        print(33333333)    
    new_count2 = new_count.copy()
    new_count.clear()
    for ed in check_edges:
        v1i, v2i = ed.vertices
        v1 = obj.data.vertices[v1i]
        v2 = obj.data.vertices[v2i]

        # setup the edge with an offset
        co_1 = v1.co.copy()
        co_2 = v2.co.copy()
        co_mid = (co_1 + co_2) * 0.5
        no_mid = (v1.normal + v2.normal).normalized() * EPS_NORMAL
        co_1 = co_1.lerp(co_mid, EPS_CENTER) + no_mid
        co_2 = co_2.lerp(co_mid, EPS_CENTER) + no_mid

        co, no, index = ray_cast(co_1, co_2)

        if index != -1:
            collect.add(ed.index)
            new_count.add(ed.index)
            obj.data.vertices[v1i].groups[0].weight = 1
            obj.data.vertices[v2i].groups[0].weight = 1
            obj.data.vertices[v1i].select = True    
            obj.data.vertices[v2i].select = True    
            #print("in the loop",collect)

            

    start = False
    bpy.types.Scene.collision_edges = collect
    #print("this is collision edges",bpy.types.Scene.collision_edges)
    #print("this is collect ", collect)
    # Send out the edge intersections
    


def select_extra():
    print("select extra is running")
    global extra_edges
    """if there are still intersections but
    smoothing them is no longer changing anything"""
    bpy.ops.object.mode_set(mode = 'EDIT')    
    bpy.ops.mesh.select_more()
    bpy.context.scene.tool_settings.vertex_group_weight = 1.0
    bpy.ops.object.vertex_group_assign()   
    bpy.ops.object.mode_set(mode = 'OBJECT')    
    extra_edges = [ed for ed in bpy.context.object.data.edges if ed.select == True]
    #print('this is the first extra edges',extra_edges)
def smooth_intersections(obj):
    global ticker, edge_list
    # Check for existing modifiers
    bpy.ops.object.modifier_add(type='SMOOTH')
    smooth = obj.modifiers[len(obj.modifiers)-1]

    # Check for existing vertex groups

    bpy.ops.object.vertex_group_add()    
    bpy.ops.object.vertex
    v_group = obj.vertex_groups[len(obj.vertex_groups)-1]
    
    # Store some existing settings
    current_mode = bpy.context.object.mode
    weight = bpy.context.scene.tool_settings.vertex_group_weight
    
    # Set up some vertex weights
    if current_mode != 'EDIT':
        bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.context.scene.tool_settings.vertex_group_weight = 0.0
    bpy.ops.object.vertex_group_assign()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    self_intersect_to_vert_group(bpy.context.object,v_group)
    print('this is new count',len(new_count))
    print('this is new count again',len(new_count2))
    if len(new_count)>= len(new_count2):
        ticker += 1
    else:
        ticker = 0
    print('this is ticker',ticker)
    
    # Smooth a larger area if number of intersections is not decreasing
    if ticker>2:
        select_extra()
        
#        if    
#            ticker += 0
#            if ticker > 0:
#
#                for i in range(ticker):
#                    select_extra()
#            print('ticker:',ticker)                
#    else:
#        ticker = 0
    #print("Look I'm a ticker",ticker,count)
    edge_list = [ed for ed in obj.data.edges if ed.select == True]
    # Settings for the smooth modifier
    smooth.factor = 0.7
    smooth.iterations = 20
    smooth.vertex_group = v_group.name
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=smooth.name)
    obj.vertex_groups.remove(v_group)
    bpy.ops.object.mode_set(mode = current_mode)
    #print("Look I'm a ticker",ticker,count)
def run_recursive():
    while len(new_count) != 0 or start == True:
        #bpy.context.object.recursion_count != 0 or start == True:
        smooth_intersections(bpy.context.object)





run_recursive()
print('totatal time: ',time.time() - current_time)
