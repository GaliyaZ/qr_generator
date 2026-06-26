import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import qrcode
from qrcode.exceptions import DataOverflowError
from PIL import Image, ImageTk
from datetime import datetime
import logging

# --- Настройка логирования ---
logging.basicConfig(
    filename="qr_generator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Программа запущена")

# --- Глобальные переменные ---
current_qr_image = None
fill_color = "#000000"  # чёрный
back_color = "#FFFFFF"  # белый


def choose_color(initial_color, title, color_var, button):
    """Открывает диалог выбора цвета и обновляет кнопку."""
    color = colorchooser.askcolor(title=title, initialcolor=initial_color)
    if color:
        color_hex = color[1] # возвращает кортеж (RGB, hex)
        color_var.set(color_hex)
        button.config(bg=color_hex)
        logging.info(f"Выбран цвет {title}: {color_hex}")


def generate_qr():
    """Генерирует QR-код с учётом выбранных параметров."""
    global current_qr_image
    text = entry.get().strip()
    if not text:
        messagebox.showwarning("Предупреждение", "Введите текст или ссылку!")
        return

    try:
        # Получаем параметры из виджетов
        box_size = int(scale_box_size.get())
        error_correction = combobox_error.get()
        # Преобразуем уровень коррекции в константу qrcode
        error_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        error_level = error_map[error_correction]

        # Создаём QR-код с выбранными параметрами
        qr = qrcode.QRCode(
            version=1,  # автоматически подстроим под данные
            error_correction=error_level,
            box_size=box_size, #TODO: автоматический выбор размера?
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)  # подбираем версию под объём данных

        # Создаём изображение с выбранными цветами
        img = qr.make_image(
            fill_color=fill_color_var.get(), back_color=back_color_var.get()
        )
        current_qr_image = img

        orig_width, orig_height = img.size
        max_size = 300
        if orig_width > max_size and orig_height > max_size:
            display_img = img.resize((max_size, max_size), Image.Resampling.LANCZOS)
        else:
            # Отображаем в окне без масштабирования
            display_img = img
        qr_display = ImageTk.PhotoImage(display_img)
        label_qr.config(image=qr_display)
        label_qr.image = qr_display

        # Активируем кнопку сохранения
        btn_save.config(state=tk.NORMAL)

        logging.info(
            f"QR-код сгенерирован: текст '{text[:30]}...' (длина {len(text)}), "
            f"box_size={box_size}, коррекция={error_correction}, цвет={fill_color_var.get()}, фон={back_color_var.get()}"
        )

    except DataOverflowError:
        error_msg = (
            "Текст слишком длинный для выбранного уровня коррекции ошибок.\n"
            "Попробуйте выбрать более низкий уровень или сократить текст."
        )
        messagebox.showerror("Ошибка", error_msg)
        logging.error(
            f"DataOverflowError при длине текста {len(text)} и коррекции {error_correction}"
        )
    except Exception as e:
        error_msg = f"Не удалось сгенерировать QR-код:\n{e}"
        messagebox.showerror("Ошибка", error_msg)
        logging.error(error_msg)


def save_qr():
    """Сохраняет текущий QR-код в файл с выбором имени."""
    global current_qr_image
    if current_qr_image is None:
        messagebox.showwarning("Предупреждение", "Сначала сгенерируйте QR-код!")
        return

    default_name = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = filedialog.asksaveasfilename(
        title="Сохранить QR-код",
        defaultextension=".png",
        filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
        initialfile=default_name,
    )
    if not file_path:
        logging.info("Сохранение отменено пользователем")
        return

    try:
        current_qr_image.save(file_path, "PNG")
        messagebox.showinfo("Успех", f"QR-код сохранён в:\n{file_path}")
        logging.info(f"QR-код сохранён в файл: {file_path}")
    except Exception as e:
        error_msg = f"Не удалось сохранить файл: {e}"
        messagebox.showerror("Ошибка", error_msg)
        logging.error(error_msg)


# --- Создание главного окна ---
root = tk.Tk()
root.title("Генератор QR-кодов")
root.geometry("500x700")
root.resizable(False, False)

# --- Ввод текста ---
tk.Label(root, text="Введите текст или ссылку:").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5, padx=10, fill="x")

# --- Параметры ---
frame_params = tk.LabelFrame(root, text="Параметры QR-кода", padx=10, pady=10)
frame_params.pack(pady=10, fill="x", padx=10)

# 1. Размер модуля
tk.Label(frame_params, text="Размер модуля:").grid(
    row=0, column=0, sticky="w", pady=5
)
scale_box_size = tk.Scale(
    frame_params, from_=3, to=10, orient=tk.HORIZONTAL, length=60
)
scale_box_size.set(6)
scale_box_size.grid(row=0, column=1, padx=10, pady=5)

# 2. Уровень коррекции ошибок
tk.Label(frame_params, text="Уровень коррекции:").grid(
    row=1, column=0, sticky="w", pady=5
)
combobox_error = ttk.Combobox(
    frame_params, values=["L", "M", "Q", "H"], state="readonly", width=5
)
combobox_error.set("M")
combobox_error.grid(row=1, column=1, sticky="w", padx=10, pady=5)

# 3. Цвет кода
tk.Label(frame_params, text="Цвет кода:").grid(row=2, column=0, sticky="w", pady=5)
# создаем переменную для использования в генерации
fill_color_var = tk.StringVar(value=fill_color)
btn_fill_color = tk.Button(
    frame_params,
    text="Выбрать",
    bg=fill_color,
    fg="white",
    width=10,
    command=lambda: choose_color(
        fill_color,
        "Выберите цвет кода",
        fill_color_var,
        btn_fill_color,
    ),
)
btn_fill_color.grid(row=2, column=1, sticky="w", padx=10, pady=5)

# 4. Цвет фона
tk.Label(frame_params, text="Цвет фона:").grid(row=2, column=2, sticky="w", pady=5)
back_color_var = tk.StringVar(value=back_color)
btn_back_color = tk.Button(
    frame_params,
    text="Выбрать",
    bg=back_color,
    fg="black",
    width=10,
    command=lambda: choose_color(
        back_color,
        "Выберите цвет фона",
        back_color_var,
        btn_back_color,
    ),
)
btn_back_color.grid(row=2, column=3, sticky="w", padx=10, pady=5)

# --- Кнопка генерации ---
btn_generate = tk.Button(
    root, text="Сгенерировать QR-код", command=generate_qr, width=25
)
btn_generate.pack(pady=10)

# --- Отображение QR-кода ---
label_qr = tk.Label(root)
label_qr.pack(pady=10)

# --- Кнопка сохранения ---
btn_save = tk.Button(
    root, text="Сохранить QR-код", command=save_qr, state=tk.DISABLED, width=25
)
btn_save.pack(pady=5)

# --- Запуск ---
root.mainloop()
logging.info("Программа завершена")
