import tkinter as tk
from tkinter import ttk, messagebox
from chapter_generator import generate_chapter, regenerate_chapter

class ChapterWritingUI:
    def __init__(self, parent):
        self.parent = parent

        # Frame setup for chapter writing UI
        self.chapter_writing_frame = ttk.Frame(parent)
        self.chapter_writing_frame.pack(expand=True, fill="both")

        # Title Label
        self.title_label = ttk.Label(self.chapter_writing_frame, text="Write Chapters", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Entry to select chapter number
        self.chapter_label = ttk.Label(self.chapter_writing_frame, text="Enter Chapter Number:")
        self.chapter_label.pack()
        self.chapter_number_entry = ttk.Entry(self.chapter_writing_frame)
        self.chapter_number_entry.pack(pady=5)

        # Button to write chapter
        self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Write Chapter", command=self.write_chapter)
        self.write_chapter_button.pack(pady=20)

        # Button to re-write chapter
        self.write_chapter_button = ttk.Button(self.chapter_writing_frame, text="Re-Write Chapter", command=self.rewrite_chapter)
        self.write_chapter_button.pack(pady=20)



    def write_chapter(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            # Call the generate_chapter function
            generate_chapter(chapter_number)
            messagebox.showinfo("Success", f"Chapter {chapter_number} saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write chapter: {str(e)}")


    def rewrite_chapter(self):
        try:
            chapter_number = int(self.chapter_number_entry.get())

            # Call the generate_chapter function
            regenerate_chapter(chapter_number)
            messagebox.showinfo("Success", f"Chapter {chapter_number} RE-saved successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid chapter number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to RE-write chapter: {str(e)}")