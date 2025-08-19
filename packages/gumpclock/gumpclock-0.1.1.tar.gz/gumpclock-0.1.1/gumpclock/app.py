import tkinter as tk
from .core import get_current_gump_time, convert_to_gump_hours

def main():
    def update_clock():
        gump_time = get_current_gump_time()
        label_result_current.config(text=f"{gump_time} Gumps")
        window.after(10000, update_clock)  # update every 10 seconds

    def handle_input():
        try:
            hours = int(hour_entry.get())
            minutes = int(min_entry.get())
            result = convert_to_gump_hours(hours, minutes)
            label_result_converted.config(text=f"Converted: {result} Gumps")
        except ValueError:
            label_result_converted.config(text="Invalid input! Enter numbers only.")

    # --- GUI Setup ---
    window = tk.Tk()
    window.title("Gump Time Converter")
    window.geometry("400x350")
    window.config(bg="black")

    label_title = tk.Label(window, text="Gump Mean Time GMT+0", font=("Digital-7", 18),
                           fg="lime", bg="black")
    label_title.pack(pady=10)

    label_result_current = tk.Label(window, text="", font=("Digital-7", 24),
                                    fg="cyan", bg="black")
    label_result_current.pack(pady=10)

    convert_title = tk.Label(window, text="Convert hours/mins to Gumps", font=("Digital-7", 10),
                             fg="lime", bg="black")
    convert_title.pack(pady=10)

    input_frame = tk.Frame(window, bg="black")
    input_frame.pack(pady=5)

    label_hour = tk.Label(input_frame, text="Insert Hour", font=("Digital-7", 10),
                          fg="cyan", bg="black")
    label_hour.grid(row=0, column=0, padx=10)
    hour_entry = tk.Entry(input_frame, width=5)
    hour_entry.grid(row=1, column=0, padx=10)

    label_minute = tk.Label(input_frame, text="Insert Minute", font=("Digital-7", 10),
                            fg="cyan", bg="black")
    label_minute.grid(row=0, column=1, padx=10)
    min_entry = tk.Entry(input_frame, width=5)
    min_entry.grid(row=1, column=1, padx=10)

    btn_update = tk.Button(window, text="Calculate", command=handle_input,
                           font=("Digital-7", 10), fg="black", bg="yellow", relief="solid")
    btn_update.pack(pady=10)

    label_result_converted = tk.Label(window, text="", font=("Digital-7", 14),
                                      fg="yellow", bg="black")
    label_result_converted.pack(pady=10)

    # Start live updating
    update_clock()
    window.mainloop()
