import bpy
import time
current_time = time.time()
print('-------------start--------------')

bpy.types.Object.recursion_count = bpy.props.IntProperty()
bpy.context.object.recursion_count = 1
ticker = 0
start = True
check_edges = []
first_collision_check = []
edge_set = set()
edge_list = []

def self_intersect_to_vert_group(obj, v_group):
    """Assign weight to vertex group if vertices are
    part of faces that self-intersect"""
    
    global first_collision_check, start, check_edges, edge_set, edge_list
    ray_cast = obj.ray_cast
    # For setting the error margin of the raycast
    EPS_NORMAL = 0.005
    EPS_CENTER = 0.01  # should always be bigger
    
    # Initilize for intersecting vertices
    collect = []


            
    if start == True:
        check_edges =[ed for ed in obj.data.edges]
    elif start ==False:
        check_edges = [ed for ed in obj.data.edges]
        
    
    for all in check_edges:
        v1i, v2i = all.vertices
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
            collect.append(index)
            obj.data.vertices[v1i].groups[0].weight = 1
            obj.data.vertices[v2i].groups[0].weight = 1
            obj.data.vertices[v1i].select = True    
            obj.data.vertices[v2i].select = True    
            #edge_list.append(bpy.context.object.data.edges[index])
            edge_list.append(index)
            
            # Get selected edged from selected verts:

    #print("this is edge_set ", edge_set)
    print("this is edge_list ", edge_list)
    # Send out the edge intersections
    return(collect)


def select_extra():
    """if there are still intersections but
    smoothing them is no longer changing anything"""
    bpy.ops.object.mode_set(mode = 'EDIT')    
    bpy.ops.mesh.select_more()
    bpy.context.scene.tool_settings.vertex_group_weight = 1.0
    bpy.ops.object.vertex_group_assign()   
    bpy.ops.object.mode_set(mode = 'OBJECT')    

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
    count = obj.recursion_count
    obj.recursion_count = len(self_intersect_to_vert_group(bpy.context.object,v_group))
    # Smooth a larger area if number of intersections is not decreasing
    if count == obj.recursion_count or count<obj.recursion_count:
        print('ticker:',ticker)
        ticker += 1
        if ticker > 1:

            for i in range(ticker):
                select_extra()
    else:
        ticker = 0

    edge_list = [ed for ed in obj.data.edges if ed.select == True]
    # Settings for the smooth modifier
    smooth.factor = 0.9
    smooth.iterations = 30
    smooth.vertex_group = v_group.name
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=smooth.name)
    obj.vertex_groups.remove(v_group)
    bpy.ops.object.mode_set(mode = current_mode)

def run_recursive():

    while bpy.context.object.recursion_count>0:
        smooth_intersections(bpy.context.object)





run_recursive()
print('totatl time: ',time.time() - current_time)
#Git Test
