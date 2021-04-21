import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile
from tkinter import messagebox
from parser_class import ArithmeticParser, ProgramParser
from lexer import ProgramLexer
from execution_exceptions import *


class App:
    def __init__(self, master=None):
        # build ui
        self.mainframe = ttk.Frame(master)
        self.program_text = tk.Text(self.mainframe)
        self.program_text.configure(cursor='arrow', font='{Source Code Pro} 12 {}', height='20', insertunfocussed='none')
        self.program_text.configure(relief='flat', setgrid='false', takefocus=False, width='50')
        self.program_text.grid(column='0', row='1')
        self.output_text = tk.Text(self.mainframe)
        self.output_text.configure(font='{Source Code Pro} 12 {}', height='20', width='50')
        self.output_text.grid(column='3', row='1')
        self.text_separator = ttk.Separator(self.mainframe)
        self.text_separator.configure(orient='horizontal')
        self.text_separator.grid(column='1', row='1')
        self.program_label = ttk.Label(self.mainframe)
        self.program_label.configure(font='{Arial} 12 {}', text='Programa')
        self.program_label.grid(column='0', row='0')
        self.output_label = ttk.Label(self.mainframe)
        self.output_label.configure(font='{Arial} 12 {}', text='Resultado')
        self.output_label.grid(column='3', row='0')
        self.upload = ttk.Button(self.mainframe)
        self.upload.configure(text='Subir')
        self.upload.grid(column='0', row='2', sticky='w')
        self.upload.configure(command=self.upload_file)
        self.filename = tk.Text(self.mainframe)
        self.filename.configure(background='#ffffff', blockcursor='true', font='TkDefaultFont', foreground='#000000')
        self.filename.configure(height='1', relief='flat', setgrid='false', takefocus=False)
        self.filename.configure(width='50')
        _text_ = '''Archivo'''
        self.filename.insert('0.0', _text_)
        self.filename.grid(column='0', row='2', sticky='e')
        self.team = ttk.Button(self.mainframe)
        self.team.configure(default='normal', text='Integrantes')
        self.team.grid(column='3', row='2', sticky='e')
        self.team.configure(command=self.show_team)
        self.validate = ttk.Button(self.mainframe)
        self.validate.configure(text='validar')
        self.validate.grid(column='3', row='2', sticky='w')
        self.validate.configure(command=self.run_parser)
        self.mainframe.configure(height='800', width='800')
        self.mainframe.grid(column='0', row='0')

        # Main widget
        self.mainwindow = self.mainframe

    def upload_file(self):
        with askopenfile() as input_file:
            self.text = input_file.read()
            self.write_text(input_file.name, self.filename)

        self.write_text(self.text, self.program_text)
        self.output_text.delete('0.0', tk.END)

    def show_team(self):
        messagebox.showinfo("Integrantes", "Alicia Velez Alvarado\nDiego Rangel Pardo\nLuis Sebastián Martínez Vega")

    def run_parser(self):
        # Checamos si se ha introducido algún archivo.
        try:
            self.text
        except AttributeError:
            messagebox.showerror("Error", "No se ha especificado archivo de entrada.")
            return False

        lexer = ProgramLexer(self.text)
        parser = ProgramParser(lexer.generate_tokens())
        try:
            result = parser.parse()
        except AttributeError:
            self.write_text("Sintaxis Incorrecta", self.output_text)
            return False
        except InvalidSyntax as e:
            result = e.message

        sans_newlines = result
        sans_newlines.lstrip("\n")

        # Hubo errores.
        if sans_newlines: 
            self.write_text(result, self.output_text)  
        else:
            self.write_text("Programa correcto", self.output_text)

    def write_text(self, text, text_box):
        text_box.delete('0.0', tk.END)
        text_box.insert('0.0', text)

    def run(self):
        self.mainwindow.mainloop()
