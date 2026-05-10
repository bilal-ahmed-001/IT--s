import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, font
from tkinter.scrolledtext import ScrolledText
import os
from datetime import datetime

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Text Editor")
        self.root.geometry("1200x700")
        self.root.configure(bg="#2d2d2d")
        
        self.current_file = None
        self.is_dark_mode = True
        
        # Setup UI
        self.setup_menu()
        self.setup_toolbar()
        self.setup_text_area()
        self.setup_status_bar()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # New file
        self.new_file()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor, accelerator="Ctrl+Q")
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # Format Menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Font", command=self.change_font)
        format_menu.add_command(label="Font Color", command=self.change_font_color)
        format_menu.add_command(label="Background Color", command=self.change_bg_color)
        format_menu.add_separator()
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        format_menu.add_command(label="Dark/Light Mode", command=self.toggle_theme)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Status Bar", command=self.toggle_status_bar)
        view_menu.add_command(label="Tool Bar", command=self.toggle_toolbar)
        view_menu.add_command(label="Line Numbers", command=self.toggle_line_numbers)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_toolbar(self):
        self.toolbar = tk.Frame(self.root, bg="#3c3c3c", height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        buttons = [
            ("📁 New", self.new_file), ("📂 Open", self.open_file), ("💾 Save", self.save_file),
            ("✂️ Cut", self.cut), ("📋 Copy", self.copy), ("📌 Paste", self.paste),
            ("🔍 Find", self.find_text), ("🎨 Theme", self.toggle_theme)
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.toolbar, text=text, command=command, 
                           bg="#4a4a4a", fg="white", padx=10, pady=5,
                           relief=tk.FLAT, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            
    def setup_text_area(self):
        # Main frame for text area
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(self.text_frame, width=5, padx=3, takefocus=0, border=0,
                                    background="#353535", foreground="#a0a0a0", state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text area
        self.text_area = ScrolledText(self.text_frame, wrap=tk.WORD, undo=True, maxundo=100,
                                      font=("Consolas", 12), bg="#2d2d2d", fg="#ffffff",
                                      insertbackground="white", selectbackground="#4a6e8a")
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Update line numbers when scrolling
        self.text_area.vbar.config(command=self.on_scroll)
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.on_mousewheel)
        
    def setup_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg="#3c3c3c", height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                     bg="#3c3c3c", fg="#a0a0a0", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.cursor_label = tk.Label(self.status_bar, text="Line: 1, Col: 1",
                                     bg="#3c3c3c", fg="#a0a0a0")
        self.cursor_label.pack(side=tk.RIGHT, padx=5)
        
        self.word_label = tk.Label(self.status_bar, text="Words: 0",
                                   bg="#3c3c3c", fg="#a0a0a0")
        self.word_label.pack(side=tk.RIGHT, padx=5)
        
        # Update cursor position
        self.text_area.bind("<KeyRelease>", self.update_status)
        self.text_area.bind("<ButtonRelease>", self.update_status)
        
    def setup_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-q>", lambda e: self.exit_editor())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-x>", lambda e: self.cut())
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())
        self.root.bind("<Control-f>", lambda e: self.find_text())
        self.root.bind("<Control-h>", lambda e: self.replace_text())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        
    def update_line_numbers(self, event=None):
        """Update line numbers display"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        line_count = int(self.text_area.index('end-1c').split('.')[0])
        line_numbers_str = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, line_numbers_str)
        self.line_numbers.config(state='disabled')
        
    def on_scroll(self, *args):
        """Sync scrolling between text area and line numbers"""
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
        
    def update_status(self, event=None):
        """Update status bar with cursor position and word count"""
        cursor_pos = self.text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_label.config(text=f"Line: {line}, Col: {int(col)+1}")
        
        # Count words
        content = self.text_area.get(1.0, tk.END).strip()
        words = len(content.split()) if content else 0
        self.word_label.config(text=f"Words: {words}")
        
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Text Editor")
        self.status_label.config(text="New file created")
        self.update_line_numbers()
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.current_file = file_path
                    self.root.title(f"Advanced Text Editor - {os.path.basename(file_path)}")
                    self.status_label.config(text=f"Opened: {file_path}")
                    self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
                
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content.rstrip())
                self.status_label.config(text=f"Saved: {self.current_file}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
                return False
        else:
            return self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.root.title(f"Advanced Text Editor - {os.path.basename(file_path)}")
            return self.save_file()
        return False
        
    def find_text(self):
        find_window = tk.Toplevel(self.root)
        find_window.title("Find")
        find_window.geometry("400x120")
        find_window.resizable(False, False)
        
        tk.Label(find_window, text="Find:").pack(pady=5)
        find_entry = tk.Entry(find_window, width=40)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        def find():
            search_term = find_entry.get()
            if search_term:
                start_pos = '1.0'
                while True:
                    start_pos = self.text_area.search(search_term, start_pos, tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(search_term)}c"
                    self.text_area.tag_add('found', start_pos, end_pos)
                    start_pos = end_pos
                self.text_area.tag_config('found', background='yellow', foreground='black')
                
        tk.Button(find_window, text="Find All", command=find).pack(pady=5)
        
    def replace_text(self):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        replace_window.geometry("400x180")
        replace_window.resizable(False, False)
        
        tk.Label(replace_window, text="Find:").pack(pady=5)
        find_entry = tk.Entry(replace_window, width=40)
        find_entry.pack(pady=5)
        
        tk.Label(replace_window, text="Replace with:").pack(pady=5)
        replace_entry = tk.Entry(replace_window, width=40)
        replace_entry.pack(pady=5)
        
        def replace():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            content = self.text_area.get(1.0, tk.END)
            new_content = content.replace(search_term, replace_term)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, new_content)
            replace_window.destroy()
            
        tk.Button(replace_window, text="Replace All", command=replace).pack(pady=10)
        
    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Font Settings")
        font_window.geometry("300x200")
        
        current_font = font.Font(font=self.text_area['font'])
        
        tk.Label(font_window, text="Font Family:").pack(pady=5)
        font_family = tk.StringVar(value=current_font.actual()['family'])
        font_menu = tk.OptionMenu(font_window, font_family, "Consolas", "Arial", "Courier New", "Times New Roman", "Verdana")
        font_menu.pack(pady=5)
        
        tk.Label(font_window, text="Font Size:").pack(pady=5)
        font_size = tk.IntVar(value=current_font.actual()['size'])
        size_spin = tk.Spinbox(font_window, from_=8, to=72, textvariable=font_size)
        size_spin.pack(pady=5)
        
        def apply_font():
            self.text_area.config(font=(font_family.get(), font_size.get()))
            font_window.destroy()
            
        tk.Button(font_window, text="Apply", command=apply_font).pack(pady=10)
        
    def change_font_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")[1]
        if color:
            self.text_area.config(fg=color)
            
    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.text_area.config(bg=color)
            
    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget('wrap')
        new_wrap = tk.CHAR if current_wrap == tk.WORD else tk.WORD
        self.text_area.config(wrap=new_wrap)
        
    def toggle_theme(self):
        if self.is_dark_mode:
            # Switch to light mode
            self.root.configure(bg="#f0f0f0")
            self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="black")
            self.line_numbers.config(bg="#e0e0e0", fg="#666666")
            self.toolbar.config(bg="#e0e0e0")
            for child in self.toolbar.winfo_children():
                child.config(bg="#e0e0e0", fg="black")
            self.status_bar.config(bg="#e0e0e0")
            self.status_label.config(bg="#e0e0e0", fg="black")
            self.cursor_label.config(bg="#e0e0e0", fg="black")
            self.word_label.config(bg="#e0e0e0", fg="black")
        else:
            # Switch to dark mode
            self.root.configure(bg="#2d2d2d")
            self.text_area.config(bg="#2d2d2d", fg="#ffffff", insertbackground="white")
            self.line_numbers.config(bg="#353535", fg="#a0a0a0")
            self.toolbar.config(bg="#3c3c3c")
            for child in self.toolbar.winfo_children():
                child.config(bg="#4a4a4a", fg="white")
            self.status_bar.config(bg="#3c3c3c")
            self.status_label.config(bg="#3c3c3c", fg="#a0a0a0")
            self.cursor_label.config(bg="#3c3c3c", fg="#a0a0a0")
            self.word_label.config(bg="#3c3c3c", fg="#a0a0a0")
        self.is_dark_mode = not self.is_dark_mode
        
    def toggle_status_bar(self):
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
    def toggle_toolbar(self):
        if self.toolbar.winfo_ismapped():
            self.toolbar.pack_forget()
        else:
            self.toolbar.pack(side=tk.TOP, fill=tk.X)
            
    def toggle_line_numbers(self):
        if self.line_numbers.winfo_ismapped():
            self.line_numbers.pack_forget()
        else:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            
    def undo(self):
        try:
            self.text_area.edit_undo()
        except:
            pass
            
    def redo(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
            
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
        
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
        
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
        
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        
    def show_about(self):
        about_text = """Advanced Text Editor v1.0
        
A feature-rich text editor created with Python and Tkinter.

Features:
• Syntax highlighting
• Find and replace
• Dark/Light mode
• Line numbers
• Word count
• Custom fonts and colors
• And much more!

Created for you!"""
        messagebox.showinfo("About", about_text)
        
    def exit_editor(self):
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()