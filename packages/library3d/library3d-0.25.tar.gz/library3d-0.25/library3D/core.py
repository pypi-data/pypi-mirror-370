from PIL import Image, ImageDraw

class Engine:
    def __init__(self, width, height):
        """
        Engine sınıfı:
        width, height: canvas boyutu
        image: PIL Image nesnesi
        draw: PIL ImageDraw nesnesi
        """
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), color=(255,255,255))
        self.draw = ImageDraw.Draw(self.image)

    def draw_polygon(self, vertices, color=(0,0,255)):
        """
        vertices: Vector3 listesi
        color: RGB tuple (0-255)
        """
        points = [(int(v.x + self.width/2), int(-v.y + self.height/2)) for v in vertices]
        self.draw.polygon(points, outline=color)

    def fill_polygon(self, vertices, color=(0,0,255)):
        """
        vertices: Vector3 listesi
        color: RGB tuple (0-255)
        Dolu polygon çizer
        """
        points = [(int(v.x + self.width/2), int(-v.y + self.height/2)) for v in vertices]
        self.draw.polygon(points, fill=color)

    def render_line(self, start, end, color=(0,0,0), width=1):
        """
        start, end: Vector3
        color: RGB tuple
        width: çizgi kalınlığı
        """
        x0, y0 = int(start.x + self.width/2), int(-start.y + self.height/2)
        x1, y1 = int(end.x + self.width/2), int(-end.y + self.height/2)
        self.draw.line((x0, y0, x1, y1), fill=color, width=width)

    def get_image(self):
        return self.image
