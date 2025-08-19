# MatrixBuffer

MatrixBuffer is a Python package that provides a multiprocess-safe buffer for PyTorch tensors, specifically designed for rendering RGB matrices and tables using Pygame. This package allows for efficient sharing of tensor data between processes, making it suitable for applications that require real-time rendering and updates.

## Features

- **Multiprocess Safe**: Utilizes shared memory and locks to ensure safe access to tensor data across multiple processes.
- **Flexible Modes**: Supports both numerical and RGB modes for tensor data.
- **Table Rendering**: Built-in utilities to render structured tabular data directly on the screen.
- **Easy Integration**: Designed to work seamlessly with Pygame for rendering visual data.

## Installation

You can install the MatrixBuffer package using pip:

```bash
pip install matrixbuffer
```

## Usage
Here is a simple example of how to use the MatrixBuffer package:
```python
import pygame
import multiprocessing
from matrixbuffer.MatrixBuffer import MultiprocessSafeTensorBuffer, Render, update_buffer_process
from matrixbuffer.Graphics import draw_table

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Create a multiprocess-safe tensor buffer
rgb_buffer = MultiprocessSafeTensorBuffer(n=240, m=320, mode="rgb")

# Create a renderer
renderer = Render(rgb_buffer, screen)

# Start the worker process to update the buffer
stop_event = multiprocessing.Event()
worker_process = multiprocessing.Process(
    target=update_buffer_process, 
    args=(rgb_buffer, stop_event)
)
worker_process.start()

# Example table data
headers = ["ID", "Name", "Score"]
rows = [
    [1, "Alice", 95],
    [2, "Bob", 87],
    [3, "Charlie", 78],
]

# Main loop for rendering
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Render tensor buffer
    renderer.render()

    # Draw a table on top
    draw_table(screen, headers, rows, (50, 50))

    pygame.display.flip()

# Clean up
stop_event.set()
worker_process.join()
pygame.quit()

```
