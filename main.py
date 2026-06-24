from tkinter import messagebox, Tk, Label, Entry, Button
import qrcode
from PIL import Image, ImageTk

def generate_qr():
    """Генерирует QR-код из текста и отображает его в окне."""
    text = entry.get().strip()
    if not text:
        messagebox.showwarning("Предупреждение", "Введите текст или ссылку!")
        return

    try:
        # Создаём объект QR-кода с базовыми настройками
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Создаём изображение
        img = qr.make_image(fill_color="black", back_color="white")
        # Изменяем размер для лучшего отображения (опционально)
        img = img.resize((300, 300), Image.Resampling.LANCZOS)

        # Преобразуем в формат, понятный Tkinter
        qr_image = ImageTk.PhotoImage(img)

        # Обновляем Label с изображением
        label_qr.config(image=qr_image)
        label_qr.image = qr_image  # сохраняем ссылку, чтобы изображение не удалилось сборщиком мусора

        # Сохранить файл автоматически
        # img.save("qr_temp.png")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сгенерировать QR-код:\n{e}")


# --- Создаём главное окно ---
root = Tk()
root.title("Генератор QR-кодов")
root.geometry("450x500")
root.resizable(False, False)

# --- Поле ввода ---
Label(root, text="Введите текст или ссылку:").pack(pady=5)
entry = Entry(root, width=50)
entry.pack(pady=5)

# --- Кнопка генерации ---
btn_generate = Button(root, text="Сгенерировать QR-код", command=generate_qr)
btn_generate.pack(pady=10)

# --- Место для отображения QR-кода ---
label_qr = Label(root)
label_qr.pack(pady=10)

# --- Запуск цикла обработки событий ---
root.mainloop()
