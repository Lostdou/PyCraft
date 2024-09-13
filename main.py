from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina(title='PyCraft', borderless=False, icon='assets\icon.ico')

player = FirstPersonController()
Sky()

chunk_size = 5
render_distance = 4  # Cantidad de chunks que se renderizan alrededor del jugador
chunks = {}  # Almacena los chunks visibles
chunk_data = {}  # Almacena los datos de cada chunk (posición y bloques)

def create_chunk(x, z):
    """Crea un chunk de 5x5 bloques o carga su estado guardado."""
    chunk = []
    for i in range(chunk_size):
        for j in range(chunk_size):
            block_pos = (x * chunk_size + j, 0, z * chunk_size + i)
            if (x, z) in chunk_data and block_pos not in chunk_data[(x, z)]:  # Si hay datos guardados
                continue  # Saltar bloques eliminados
            block = Button(color=color.white, model='cube', position=block_pos,
                           texture='assets\grass.png', parent=scene, origin_y=0.5)
            chunk.append(block)
    chunks[(x, z)] = chunk

def download_chunk(x, z): # Descarga un chunk y guarda su estado
    if (x, z) in chunks:
        chunk_data[(x, z)] = [block.position for block in chunks[(x, z)] if block.enabled]
        for block in chunks[(x, z)]:
            block.enabled = False  # Desactiva visualmente el chunk
        del chunks[(x, z)]  # Lo elimina de los chunks visibles

def update(): # Carga o descarga chunks dependiendo de la posición del jugador.
    player_chunk_x = int(player.position.x // chunk_size)
    player_chunk_z = int(player.position.z // chunk_size)

    # Cargar chunks cercanos
    for x in range(player_chunk_x - render_distance, player_chunk_x + render_distance + 1):
        for z in range(player_chunk_z - render_distance, player_chunk_z + render_distance + 1):
            if (x, z) not in chunks:
                create_chunk(x, z)

    # Descargar chunks lejanos
    chunks_to_download = []
    for chunk_pos in chunks:
        chunk_x, chunk_z = chunk_pos
        if abs(chunk_x - player_chunk_x) > render_distance or abs(chunk_z - player_chunk_z) > render_distance:
            chunks_to_download.append((chunk_x, chunk_z))

    for chunk_pos in chunks_to_download:
        download_chunk(*chunk_pos)

def input(key):
    for chunk in chunks.values():
        for box in chunk:
            if box.hovered:
                chunk_pos = (int(box.position.x // chunk_size), int(box.position.z // chunk_size))

                if key == 'right mouse down':
                    new_pos = box.position + mouse.normal
                    new = Button(color=color.white, model='cube', position=new_pos,
                                texture='assets\stone.png', parent=scene, origin_y=0.5)
                    chunks[chunk_pos].append(new)
                    chunk_data.setdefault(chunk_pos, []).append(new_pos)  # Guardar el nuevo bloque

                if key == 'left mouse down':
                    chunks[chunk_pos].remove(box)
                    if chunk_pos in chunk_data and box.position in chunk_data[chunk_pos]:
                        chunk_data[chunk_pos].remove(box.position)  # Eliminar de los datos guardados
                    destroy(box)

app.run()
