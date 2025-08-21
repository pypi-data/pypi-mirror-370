import pygame
import torch
from PIL import Image, ImageDraw, ImageFont
from matrixbuffer.MatrixBuffer import MultiprocessSafeTensorBuffer

class Text:
    def __init__(self, text, x, y, font_path=None, font_size=16, color=(255,255,255)):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color

        if font_path is None:
            font_path = "fonts/ComicMono.ttf"
        try:
            self.font = ImageFont.truetype(font_path, font_size)
        except:
            self.font = ImageFont.load_default()

    def render_to_tensor(self, buffer: MultiprocessSafeTensorBuffer):
        if not self.text: return
        bbox = self.font.getbbox(self.text)
        text_w, text_h = max(1,bbox[2]-bbox[0]), max(1,bbox[3]-bbox[1])

        img = Image.new("RGBA", (text_w, text_h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.text((-bbox[0], -bbox[1]), self.text, font=self.font, fill=(*self.color,255))

        arr = torch.ByteTensor(torch.ByteStorage.from_buffer(img.tobytes())).reshape(text_h, text_w, 4)
        text_rgb = arr[...,:3].to(torch.float32)
        alpha = arr[...,3:4].to(torch.float32)/255.0

        buf = buffer.read_matrix().to(torch.float32)
        H, W = buffer.get_dimensions()
        x0, y0 = max(0,self.x), max(0,self.y)
        x1, y1 = min(W, self.x+text_w), min(H, self.y+text_h)
        if x0>=x1 or y0>=y1: return
        tx0, ty0 = 0, 0
        tx1, ty1 = x1-x0, y1-y0

        region = buf[y0:y1, x0:x1]
        buf[y0:y1, x0:x1] = text_rgb[ty0:ty1, tx0:tx1]*alpha[ty0:ty1, tx0:tx1] + region*(1-alpha[ty0:ty1, tx0:tx1])
        buffer.write_matrix(buf.to(torch.uint8))

class Table:
    """
    A class to render a table with text and grid lines to a PyTorch tensor buffer.
    It can dynamically adjust column widths based on content.
    """
    def __init__(self, data, x, y, font_path=None, font_size=16,
                cell_width=100, cell_height=40, grid_color=(200,200,200),
                bg_color=None, text_color=(255,255,255), expand_cells=False):
        self.data = data
        self.x = x
        self.y = y
        self.font_size = font_size
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.grid_color = grid_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_path = font_path or "fonts/ComicMono.ttf"
        self.expand_cells = expand_cells

    def render_to_tensor(self, buffer: MultiprocessSafeTensorBuffer):
        """
        Renders the full table, including background, grid, and text, onto the buffer.
        """
        H, W = buffer.get_dimensions()
        buf = buffer.read_matrix().to(torch.float32)
        rows, cols = len(self.data), max(len(r) for r in self.data)

        # --- FIX START ---
        # Calculate individual column widths if expand_cells is true
        column_widths = [self.cell_width] * cols
        if self.expand_cells:
            for c in range(cols):
                max_text_width = 0
                for r in range(rows):
                    if c < len(self.data[r]):
                        text = str(self.data[r][c])
                        font = Text(text, 0, 0, font_path=self.font_path, font_size=self.font_size).font
                        bbox = font.getbbox(text)
                        w = bbox[2] - bbox[0]
                        if w > max_text_width:
                            max_text_width = w
                # Add padding and set the new width for the column
                column_widths[c] = max_text_width + 8
        # --- FIX END ---
        
        # Table bounds based on new column widths
        table_width = sum(column_widths)
        table_height = rows * self.cell_height
        y_start, y_end = self.y, min(H, self.y + table_height)
        x_start, x_end = self.x, min(W, self.x + table_width)

        # 1. Draw table background
        if self.bg_color:
            buf[y_start:y_end, x_start:x_end] = torch.tensor(self.bg_color, dtype=torch.float32)

        # 2. Draw grid lines
        # Horizontal lines
        for r in range(rows + 1):
            y_pos = self.y + r * self.cell_height
            if y_pos < y_end:
                buf[y_pos:y_pos+1, x_start:x_end] = torch.tensor(self.grid_color, dtype=torch.float32)
        # Vertical lines
        current_x = self.x
        for c in range(cols + 1):
            if c < cols:
                current_x += column_widths[c]
            if current_x < x_end:
                buf[y_start:y_end, current_x:current_x+1] = torch.tensor(self.grid_color, dtype=torch.float32)

        # 3. Create all Text objects and render them
        current_x = self.x
        for c, cw in enumerate(column_widths):
            for r in range(rows):
                if c < len(self.data[r]):
                    cell_text = str(self.data[r][c])
                    cell_y = self.y + r * self.cell_height
                    text_obj = Text(cell_text, x=current_x, y=cell_y,
                                    font_path=self.font_path,
                                    font_size=self.font_size,
                                    color=self.text_color)
                    text_obj.render_to_tensor(buffer)
            current_x += cw

class Graphics:
    def __init__(self, width=800, height=600, bg_color=(0,0,0)):
        pygame.init()
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Custom Tensor Renderer")
        self.clock = pygame.time.Clock()
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def run(self, buffer: MultiprocessSafeTensorBuffer = None):
        running = True
        while running:
            self.screen.fill(self.bg_color)

            if buffer:
                tensor_data = buffer.read_matrix()
                surf = pygame.surfarray.make_surface(tensor_data.cpu().numpy().swapaxes(0,1))
                self.screen.blit(surf, (0,0))
            else:
                for obj in self.objects:
                    obj.render_to_tensor(buffer)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running=False
            self.clock.tick(30)
        pygame.quit()


if __name__ == "__main__":
    width, height = 640, 480
    buffer = MultiprocessSafeTensorBuffer(n=height, m=width, mode="rgb")
    buffer.write_matrix(torch.zeros((height,width,3), dtype=torch.uint8))

    g = Graphics(width=width, height=height, bg_color=(30,30,30))

    text1 = Text("Custom Rendering Engine!", x=50, y=50, font_size=32, color=(255,255,0))
    table1 = Table(
        data=[["Name","Age"], ["Alice","24"], ["Bob","30"]],
        x=50, y=120, cell_width=120, cell_height=40,
        bg_color=(50,50,100), grid_color=(255,255,255)
    )

    text1.render_to_tensor(buffer)
    table1.render_to_tensor(buffer)

    g.run(buffer)
