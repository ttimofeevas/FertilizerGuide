import json
import os
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF


class FertilizerGuide:
    def __init__(self, root):
        self.root = root
        self.root.title("Справочник норм удобрений")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.n_value = StringVar()
        self.p_value = StringVar()
        self.k_value = StringVar()

        self.data = self.load_data()
        self.create_widgets()
        self.set_default_values()

    def load_data(self):
        filename = "fertilizer_data.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                return self.get_default_data()
        else:
            default_data = self.get_default_data()
            self.save_data(default_data)
            return default_data

    def get_default_data(self):
        return {
            "пшеница": {
                "чернозём": {"N": 90, "P": 60, "K": 50},
                "серозём": {"N": 110, "P": 70, "K": 40},
                "дерново-подзолистая": {"N": 80, "P": 80, "K": 70},
                "каштановая": {"N": 100, "P": 65, "K": 55}
            },
            "кукуруза": {
                "чернозём": {"N": 120, "P": 70, "K": 80},
                "серозём": {"N": 140, "P": 80, "K": 60},
                "дерново-подзолистая": {"N": 110, "P": 90, "K": 75}
            },
            "подсолнечник": {
                "чернозём": {"N": 60, "P": 90, "K": 100},
                "серозём": {"N": 50, "P": 100, "K": 90},
                "каштановая": {"N": 55, "P": 85, "K": 95}
            },
            "соя": {
                "чернозём": {"N": 30, "P": 80, "K": 70},
                "серозём": {"N": 40, "P": 90, "K": 60}
            },
            "картофель": {
                "чернозём": {"N": 100, "P": 90, "K": 120},
                "дерново-подзолистая": {"N": 120, "P": 100, "K": 140}
            }
        }

    def save_data(self, data):
        try:
            with open("fertilizer_data.json", 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def create_widgets(self):
        frame_crop = LabelFrame(self.root, text="Выбор культуры", padx=10, pady=10)
        frame_crop.pack(fill="x", padx=20, pady=10)

        Label(frame_crop, text="Культура:").grid(row=0, column=0, sticky="w", padx=5)
        self.crop_combo = ttk.Combobox(frame_crop, state="readonly", width=25)
        self.crop_combo.grid(row=0, column=1, padx=5, pady=5)
        self.crop_combo.bind('<<ComboboxSelected>>', self.on_crop_selected)

        frame_soil = LabelFrame(self.root, text="Выбор типа почвы", padx=10, pady=10)
        frame_soil.pack(fill="x", padx=20, pady=10)

        Label(frame_soil, text="Тип почвы:").grid(row=0, column=0, sticky="w", padx=5)
        self.soil_combo = ttk.Combobox(frame_soil, state="readonly", width=25)
        self.soil_combo.grid(row=0, column=1, padx=5, pady=5)
        self.soil_combo.bind('<<ComboboxSelected>>', self.show_fertilizer)

        frame_result = LabelFrame(self.root, text="Рекомендуемые нормы (кг/га)", padx=10, pady=10)
        frame_result.pack(fill="both", padx=20, pady=10, expand=True)

        Label(frame_result, text="Азот (N):", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_n = Entry(frame_result, textvariable=self.n_value, width=10, font=("Arial", 14), state="readonly")
        entry_n.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        Label(frame_result, text="Фосфор (P):", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_p = Entry(frame_result, textvariable=self.p_value, width=10, font=("Arial", 14), state="readonly")
        entry_p.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        Label(frame_result, text="Калий (K):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_k = Entry(frame_result, textvariable=self.k_value, width=10, font=("Arial", 14), state="readonly")
        entry_k.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        frame_buttons = Frame(self.root)
        frame_buttons.pack(fill="x", padx=20, pady=10)

        Button(frame_buttons, text="Сохранить в TXT", width=20, command=self.save_to_txt).pack(side="left", padx=5)
        Button(frame_buttons, text="Сохранить в PDF", width=20, command=self.save_to_pdf).pack(side="left", padx=5)
        Button(frame_buttons, text="Очистить", width=20, command=self.clear_fields).pack(side="right", padx=5)

    def set_default_values(self):
        if self.data:
            crops = list(self.data.keys())
            self.crop_combo['values'] = crops
            if crops:
                self.crop_combo.current(0)
                self.update_soils()

    def on_crop_selected(self, event):
        self.update_soils()

    def update_soils(self):
        crop = self.crop_combo.get()
        if crop in self.data:
            soils = list(self.data[crop].keys())
            self.soil_combo['values'] = soils
            if soils:
                self.soil_combo.current(0)
                self.show_fertilizer()
            else:
                self.clear_fields()

    def show_fertilizer(self):
        crop = self.crop_combo.get()
        soil = self.soil_combo.get()

        if crop and soil and crop in self.data and soil in self.data[crop]:
            norms = self.data[crop][soil]
            self.n_value.set(str(norms.get("N", "—")))
            self.p_value.set(str(norms.get("P", "—")))
            self.k_value.set(str(norms.get("K", "—")))
        else:
            self.clear_fields()

    def clear_fields(self):
        self.n_value.set("—")
        self.p_value.set("—")
        self.k_value.set("—")

    def save_to_txt(self):
        crop = self.crop_combo.get()
        soil = self.soil_combo.get()
        n = self.n_value.get()
        p = self.p_value.get()
        k = self.k_value.get()

        if not crop or not soil or n == "—" or p == "—" or k == "—":
            messagebox.showwarning("Предупреждение", "Сначала выберите культуру и тип почвы!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            initialfile=f"удобрения_{crop}_{soil}.txt"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("=" * 50 + "\n")
                    file.write("  РЕКОМЕНДАЦИЯ ПО ВНЕСЕНИЮ УДОБРЕНИЙ\n")
                    file.write("=" * 50 + "\n\n")
                    file.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                    file.write(f"Культура: {crop}\n")
                    file.write(f"Тип почвы: {soil}\n\n")
                    file.write("-" * 30 + "\n")
                    file.write(f"Азот (N):  {n} кг/га\n")
                    file.write(f"Фосфор (P): {p} кг/га\n")
                    file.write(f"Калий (K):  {k} кг/га\n")
                    file.write("-" * 30 + "\n\n")
                    file.write("* Рекомендация сформирована программой\n")
                    file.write("* Справочник норм удобрений для основных культур\n")

                messagebox.showinfo("Успех", f"Файл сохранен:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def save_to_pdf(self):
        crop = self.crop_combo.get()
        soil = self.soil_combo.get()
        n = self.n_value.get()
        p = self.p_value.get()
        k = self.k_value.get()

        # Проверка, что все поля заполнены
        if not crop or not soil or n == "—" or p == "—" or k == "—":
            messagebox.showwarning("Предупреждение", "Сначала выберите культуру и тип почвы!")
            return

        # Открываем диалог сохранения файла
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")],
            initialfile=f"удобрения_{crop}_{soil}.pdf"
        )

        if file_path:
            try:
                # Создаём PDF-документ
                pdf = FPDF()
                pdf.add_page()

                # ПОДКЛЮЧАЕМ ВСЕ ТРИ РУССКИХ ШРИФТА
                pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
                pdf.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)

                # Заголовок (жирный)
                pdf.set_font('DejaVu', 'B', 16)
                pdf.cell(190, 15, "РЕКОМЕНДАЦИЯ ПО ВНЕСЕНИЮ УДОБРЕНИЙ", ln=1, align="C")
                pdf.line(10, 25, 200, 25)

                # Дата (обычный)
                pdf.set_font('DejaVu', '', 11)
                pdf.cell(190, 10, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=1, align="R")

                # Основная информация
                pdf.ln(10)
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(50, 10, "Культура:", 0, 0)
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(140, 10, crop, 0, 1)

                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(50, 10, "Тип почвы:", 0, 0)
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(140, 10, soil, 0, 1)

                # Таблица с NPK
                pdf.ln(10)
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(60, 10, "Элемент", 1, 0, "C")
                pdf.cell(60, 10, "Норма (кг/га)", 1, 1, "C")

                pdf.set_font('DejaVu', '', 12)
                pdf.cell(60, 10, "Азот (N)", 1, 0, "C")
                pdf.cell(60, 10, n, 1, 1, "C")

                pdf.cell(60, 10, "Фосфор (P)", 1, 0, "C")
                pdf.cell(60, 10, p, 1, 1, "C")

                pdf.cell(60, 10, "Калий (K)", 1, 0, "C")
                pdf.cell(60, 10, k, 1, 1, "C")

                # Примечание (курсив)
                pdf.ln(10)
                pdf.set_font('DejaVu', 'I', 10)
                pdf.cell(190, 10, "Рекомендация сформирована программой", 0, 1, "C")
                pdf.cell(190, 10, "Справочник норм удобрений для основных культур", 0, 1, "C")

                # Сохранение PDF
                pdf.output(file_path)

                messagebox.showinfo("Успех", f"PDF файл сохранен:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить PDF: {e}")


def main():
    root = Tk()
    app = FertilizerGuide(root)
    root.mainloop()


if __name__ == '__main__':
    main()