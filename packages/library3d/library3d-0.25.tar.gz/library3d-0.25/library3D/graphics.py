# graphics.py: yardımcı fonksiyonlar

def draw_polygon(vertices, engine, color=(0,0,255)):
    """
    engine: Engine sınıfı
    vertices: Vector3 listesi
    color: RGB
    """
    engine.draw_polygon(vertices, color=color)

def fill_polygon(vertices, engine, color=(0,0,255)):
    """
    Dolu polygon çizimi
    """
    engine.fill_polygon(vertices, color=color)

def render_line(start, end, engine, color=(0,0,0), width=1):
    """
    İki nokta arasına çizgi
    """
    engine.render_line(start, end, color=color, width=width)
