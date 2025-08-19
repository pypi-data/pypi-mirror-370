import os
import time
import shutil
import sys
import glob
from PIL import Image, ImageSequence

ASCII_CHARS = " .'`^\",:;Il!i><~+_-?][}{1234567890)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
FRAME_DELAY = 0.06
BG_COLOR = (255, 255, 255)
BG_THRESHOLD = 50
ASPECT_RATIO_FACTOR = 0.48

def get_max_terminal_size():
    columns, lines = shutil.get_terminal_size()
    return max(1, columns), max(1, lines - 1)

def scale_image(image, max_width, max_height):
    width, height = image.size
    target_width = min(width, max_width)
    aspect_ratio = height / width
    target_height = min(int(target_width * aspect_ratio * ASPECT_RATIO_FACTOR), max_height)
    if target_height < max_height:
        new_height = min(max_height, height)
        target_width = min(int(new_height / (aspect_ratio * ASPECT_RATIO_FACTOR)), max_width)
        target_height = min(int(target_width * aspect_ratio * ASPECT_RATIO_FACTOR), max_height)
    return image.resize((target_width, target_height))

def remove_background(image, bg_color=BG_COLOR, threshold=BG_THRESHOLD):
    image = image.convert("RGBA")
    width, height = image.size
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            distance = abs(r - bg_color[0]) + abs(g - bg_color[1]) + abs(b - bg_color[2])
            if distance < threshold:
                pixels[x, y] = (0, 0, 0, 0)
    return image

def pixel_to_ascii_color(pixel):
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a < 50:
            return ' '
    else:
        r, g, b = pixel
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    char_idx = min(int(brightness * len(ASCII_CHARS) / 256), len(ASCII_CHARS) - 1)
    char = ASCII_CHARS[char_idx]
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"

def convert_to_colored_ascii(image):
    if image.mode == 'RGBA':
        pixels = list(image.getdata())
    else:
        image = image.convert("RGB")
        pixels = list(image.getdata())
    ascii_image = []
    width = image.width
    for y in range(image.height):
        start_index = y * width
        end_index = start_index + width
        row = pixels[start_index:end_index]
        line = ''.join(pixel_to_ascii_color(p) for p in row)
        ascii_image.append(line)
    return '\n'.join(ascii_image)

def gif_to_ascii_frames(gif_path, remove_bg=False):
    from PIL import ImageSequence
    ascii_frames = []
    total_duration = 0
    with Image.open(gif_path) as im:
        frame_count = im.n_frames
        print(f"\033[93mProcesando GIF: {frame_count} frames...\033[0m")
        max_width, max_height = get_max_terminal_size()
        print(f"\033[93mTamaño máximo disponible: {max_width}x{max_height}\033[0m")
        for frame in ImageSequence.Iterator(im):
            if remove_bg:
                frame = remove_background(frame.copy())
            scaled_frame = scale_image(frame, max_width, max_height)
            print(f"\033[93mFrame {len(ascii_frames)+1}/{frame_count}: "
                  f"{scaled_frame.width}x{scaled_frame.height}\033[0m", end='\r')
            ascii_frame = convert_to_colored_ascii(scaled_frame)
            duration_ms = frame.info.get('duration', int(FRAME_DELAY * 1000))
            duration_sec = max(duration_ms / 1000.0, 0.06)
            total_duration += duration_sec
            ascii_frames.append((ascii_frame, duration_sec))
    print("\n\033[92mProcesamiento completado\033[0m")
    print(f"\033[92mDuración total: {total_duration:.2f} segundos\033[0m")
    return ascii_frames

def play_ascii_animation(frames):
    try:
        print("\033[?25l", end='')
        os.system('cls' if os.name == 'nt' else 'clear')
        if not frames:
            return
        escape_home = f"\033[0;0H"
        start_time = time.perf_counter()
        t = 0
        while True:
            for frame, duration in frames:
                target_time = start_time + t
                while time.perf_counter() < target_time:
                    time.sleep(0.001)
                print(f"{escape_home}{frame}", end='', flush=True)
                t += duration
    except KeyboardInterrupt:
        print("\033[?25h", end='')
        print("\033[0m", end='')
        print("\n\033[91mAnimación detenida\033[0m")
    finally:
        print("\033[?25h\033[0m\033[2J\033[H", end='')

def image_to_ascii(image_path, remove_bg=False):
    with Image.open(image_path) as img:
        max_width, max_height = get_max_terminal_size()
        if remove_bg:
            img = remove_background(img)
        img = scale_image(img, max_width, max_height)
        ascii_art = convert_to_colored_ascii(img)
        print(ascii_art)

def find_file_by_mode(mode):
    if mode == "gif":
        files = glob.glob("*.gif") + glob.glob("*.webp")
    else:
        files = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg")
    if not files:
        print(f"\033[91mError: No se encontraron archivos {mode} en el directorio actual.\033[0m")
        sys.exit(1)
    return files[0]
