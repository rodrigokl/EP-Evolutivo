#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://github.com/rodrigokl/EPEvolutivo

# Rodrigo K. Leitzke, UFPEL - Laboratório de Conforto e Eficiência Energética (LABCEE); 
# Proposta de uma ferramenta que rode de forma evolutiva as simulações do EnergyPlus.

from tkinter import *
from tkinter import ttk
import tkinter as tk
from eppy import modeleditor
from ttkthemes import ThemedTk
from eppy.modeleditor import IDF
try:
    # python 2
    from tkFont import Font
except ImportError:
    # python 3
    from tkinter.font import Font

try:
    import Tkinter as tk
    import ttk
    from tkFileDialog import askopenfilename
    import tkMessageBox
    import tkSimpleDialog
    from tkSimpleDialog import Dialog
except ModuleNotFoundError:   # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    import tkinter.messagebox as tkMessageBox
    import tkinter.simpledialog as tkSimpleDialog
    from tkinter.simpledialog import Dialog

import platform
import os

from evolib import *

global fname, idd, epw 

fname = ''
idd = ''
epw = ''
parameters = []

from besos import eppy_funcs as ef
import sampling
from evaluator import EvaluatorEP
from objectives import MeterReader
from optimizer import NSGAII, SPEA2
from parameters import *
from problem import EPProblem
import platypus
import pandas as pd
import matplotlib.pyplot as plt
from platypus.evaluator import MapEvaluator
import matplotlib.pyplot as plt
from pandastable import Table, TableModel
import matplotlib.backends.backend_tkagg
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure

# DEF's

# --------------------------------------

def simulate():
	global parameters, idf
	EPobjectives = ['Cooling:Electricity', 'Heating:Electricity']       # Heating e Cooling como objeivos;
	problem = EPProblem(parameters, EPobjectives)                 # Criando uma instância do problema;
	evaluator = EvaluatorEP(problem, idf, epw=epw)   # Função de avaliação com o problema e o modelo;
	results = NSGAII(evaluator, evaluations=5, population_size=20)   # rodando o NSGA II;
	l=1
	vazio = ttk.Label(resultados, text="",font=font,background='white')
	vazio.grid(row=l,column=0, padx=10) 
	l+=1
	results['Cooling:Electricity'] = (results['Cooling:Electricity']/3600000)/104.34 # Transformando J em EUI;
	results['Heating:Electricity'] = (results['Heating:Electricity']/3600000)/104.34
	df = results
	table = pt =  Table(resultados, dataframe=df, showtoolbar=True, showstatusbar=False)
	pt.show()
	l+=1
	
	optres = results.loc[results['pareto-optimal']==True,:] # pareto-ótimo
	plot = matplotlib.figure.Figure(figsize=(10,4))
	axplot = plot.add_subplot(111)
	axplot.plot(results['Cooling:Electricity'], results['Heating:Electricity'],'x') # Plot de todos os resultados em 'x'
	axplot.plot(optres['Cooling:Electricity'], optres['Heating:Electricity'],'ro') # Plot das melhores soluções em vermelho
	axplot.set_xlabel('EUI Cooling (kWh/(m².year))')
	axplot.set_ylabel('EUI Heating (kWh/(m².year))')

	canvas = FigureCanvasTkAgg(plot, resultados)
	canvas.get_tk_widget().grid(row=l,column=1,sticky=N,padx=10)
	canvas.draw()
	
	l+=1
	vazio = ttk.Label(resultados, text="",font=font,background='white')
	vazio.grid(row=l,column=0, padx=10) 
	l+=1
	tab3()

def insertVar(fname,classEP,objEP,fieldEP,minEP,maxEP):
	global parameters
	parameters.append( 
				Parameter(
                	selector=FieldSelector(
                    class_name=classEP,            			   # Classe do E+;
                    object_name=objEP,                          # Nome do objeto;
                    field_name=fieldEP, 						   # Campo do objeto;
                ),
                	value_descriptor=RangeParameter(min_val=float(minEP), max_val=float(maxEP))      # limites;
                )
            )
	print (parameters)


def tab3():
	notebook.select(resultados)
def tab2():
    notebook.select(avaliacao)

def group_selected(event):
	selected = idf.idfobjects[box2.get()]
	list_sel = []
	for sel in selected:
		list_sel.append(sel.Name)
	box3['values'] = list_sel	

def obj_selected(event):
	selected = idf.idfobjects[box2.get()]
	for sel in selected:
		if sel.Name == box3.get():
			box4['values'] = sel.fieldnames	

def popupmsg(msg):
    popup = ThemedTk(theme="arc")	
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg,font='Arial 14',background='white')
    popup.configure(background='white')
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Ok",style='TButton', command = popup.destroy)
    B1.pack()
    popup.mainloop()

def load_file_IDF():
    global fname
    fname = askopenfilename(filetypes=(("Arquivos IDF", "*.idf"),
                                           ("All files", "*.*")))
    if fname:
      try:
        idftext.insert(INSERT, fname)

      except:                     
        showerror("Falha!", "Erro ao abrir o arquivo idf\n'%s'" % fname)
        return

def load_file_EPW():
    global epw
    epw = askopenfilename(filetypes=(("Arquivos EPW", "*.epw"),
                                           ("All files", "*.*")))
    if epw:
      try:
        epwtext.insert(INSERT, epw)
                
      except:                     
        showerror("Falha!", "Erro ao abrir o arquivo epw\n'%s'" % epw)
        return

def load_file_IDD():
    global idd
    idd = askopenfilename(filetypes=(("Arquivos IDD", "*.idd"),
                                           ("All files", "*.*")))
    if idd:
      try:
        iddtext.insert(INSERT, idd)
    
      except:                     
        showerror("Falha!", "Erro ao abrir o arquivo epw\n'%s'" % idd)
        return

def confirma_arqs():
	global fname, idd,idf, epw, box2,box3,box4
	if len(fname) == 0 and len(idd) == 0 and len(epw) == 0:
		popupmsg("Insira todos os arquivos na entrada!")
	else:
		idf = ef.get_building(fname)
		l2 = 0
		list_obj = []
		for objects in idf.idfobjects:
			list_obj.append(objects)

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1
		pergunta = ttk.Label(avaliacao, text="Selecione o grupo do EnergyPlus: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		box_value2 = StringVar()
		box2 = ttk.Combobox(avaliacao, textvariable = box_value2,width=50)
		box2['values'] = list_obj
		box2.bind("<<ComboboxSelected>>", group_selected)
		box2.current(0)
		box2.grid(column=2, row=l2,sticky=S,padx=10)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1
		pergunta = ttk.Label(avaliacao, text="Selecione o objeto: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		box_value3 = StringVar()
		box3 = ttk.Combobox(avaliacao, textvariable=box_value3,width=50)
		box3.bind("<<ComboboxSelected>>", obj_selected)
		#box3.current(0)
		box3.grid(column=2, row=l2,sticky=S,padx=10)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1
		pergunta = ttk.Label(avaliacao, text="Selecione o campo objeto: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		box_value4 = StringVar()
		box4 = ttk.Combobox(avaliacao, textvariable=box_value4,width=50)
		#box2.current(0)
		box4.grid(column=2, row=l2,sticky=S,padx=10)


		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1
		pergunta = ttk.Label(avaliacao, text="Limites para variação: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		de_entry = ttk.Entry(avaliacao,width=10)
		de_entry.grid(column=2, row=l2, padx=10,sticky=W)
		l2 += 1
		a_entry = ttk.Entry(avaliacao,width=10)
		a_entry.grid(column=2, row=l2, padx=10,sticky=W)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1


		pergunta = ttk.Label(avaliacao, text="Número de gerações: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		ger_entry = ttk.Entry(avaliacao,width=10)
		ger_entry.grid(column=2, row=l2, padx=10,sticky=W)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1

		pergunta = ttk.Label(avaliacao, text="Número de indivíduos: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		indiv_entry = ttk.Entry(avaliacao,width=10)
		indiv_entry.grid(column=2, row=l2, padx=10,sticky=W)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1

		pergunta = ttk.Label(avaliacao, text="Selecione o algoritmo: ", font = "Arial 14", background='white')
		pergunta.grid(column=1, row=l2,sticky=W,padx=10)
		chk_NSGA = ttk.Checkbutton(avaliacao, text="NSGA-II",style='TCheckbutton')
		chk_NSGA.grid(column=2, row=l2, padx=10,sticky=W)
		l2 += 1
		chk_NSGA = ttk.Checkbutton(avaliacao, text="SPEA2",style='TCheckbutton')
		chk_NSGA.grid(column=2, row=l2, padx=10,sticky=W)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		l2 += 1

		tkButtonSimular = ttk.Button(avaliacao, text="Inserir variável", style='TButton', command=lambda: insertVar(fname,box2.get(),box3.get(),box4.get(),de_entry.get(),a_entry.get()))
		tkButtonSimular.grid(column=2, row=l2,stick=E, padx=140)
		tkButtonAdd = ttk.Button(avaliacao, text="Simular", style='TButton',command=simulate)
		tkButtonAdd.grid(column=2, row=l2, sticky=E,padx=10)

		l2 += 1

		vazio = ttk.Label(avaliacao, text="",font=font,background='white')
		vazio.grid( row=l2,column=0, padx=10)

		

		tab2()	

tkTop = ThemedTk(theme="arc")	
tkTop.title("EnergyPlus Evolutivo")
#tkTop.geometry('800x650')
#tkTop.geometry('800x600')
tkTop.configure(background='white')
#img = ImageTk.PhotoImage(file='logo_p.png')
#tkTop.tk.call('wm', 'iconphoto', tkTop._w, img)
#stylelogo_p_3


font = "Arial 14"
font_bold = "Arial 14 bold"
noteStyler = ttk.Style()
noteStyler.configure("TFrame", background="white", borderwidth=0)
noteStyler.configure("TCheckbutton", background="white", font='Arial 14 bold')
noteStyler.configure("TNotebook", background='white',darkcolor='white',lightcolor='white', borderwidth=0)
noteStyler.map("TNotebook.Tab", background=[("selected", 'white')], foreground=[("selected", '#3A8FD7')]);
noteStyler.configure("TNotebook.Tab", background='white', foreground='#9e9e9e',bordercolor='#3A8FD7',  borderwidth=0,font='Arial 14 bold')
noteStyler.configure("TButton",background='white',foreground='#3A8FD7', borderwidth=0,font='Arial 14 bold')

notebook = ttk.Notebook(tkTop,style='TNotebook')
inicio = ttk.Frame(notebook,style='TFrame')
avaliacao = ttk.Frame(notebook, style='TFrame')
resultados = ttk.Frame(notebook,style='TFrame')
#notebook_Add_Producao = ttk.Notebook(notebook, style='TNotebook')



notebook.add(inicio,text='Início',compound = tk.TOP)
notebook.add(avaliacao, text='Avaliação evolutiva')
notebook.add(resultados, text='Resultados')
notebook.grid()



l = 0

vazio = ttk.Label(inicio, text="",font=font,background='white')
vazio.grid( row=l,column=0, padx=10)

l += 1

idflab = "Arquivo IDF:"
idflab = ttk.Label(inicio, text=idflab, background='white',font='Arial 14') 
idflab.grid(column=1, row=l, padx=10)

idftext = ttk.Entry(inicio,width=50)
idftext.grid(column=2, row=l, padx=10)
procuraridf = ttk.Button(inicio,text="Procurar", command=load_file_IDF, style='TButton')
procuraridf.grid(column=3, row=l, padx=10)

l += 1

vazio = ttk.Label(inicio, text="",font=font,background='white')
vazio.grid( row=l,column=0, padx=10)

l += 1
# --------------------------------------

iddlab = "Arquivo IDD:"
iddlab = ttk.Label(inicio, text=iddlab, background='white',font='Arial 14') 
iddlab.grid(column=1, row=l, padx=10)

iddtext = ttk.Entry(inicio,width=50)
iddtext.grid(column=2, row=l, padx=10)
procuraridd = ttk.Button(inicio,text="Procurar",command=load_file_IDD, style='TButton')
procuraridd.grid(column=3, row=l, padx=10)

l += 1

vazio = ttk.Label(inicio, text="",font=font,background='white')
vazio.grid( row=l,column=0, padx=10)

l += 1
# --------------------------------------

epwlab = "Arquivo EPW:"
epwlab = ttk.Label(inicio, text=epwlab, background='white', font='Arial 14') 
epwlab.grid(column=1, row=l, padx=10)

epwtext = ttk.Entry(inicio,width=50)
epwtext.grid(column=2, row=l, padx=10)
procurarepw = ttk.Button(inicio,text="Procurar",command=load_file_EPW, style='TButton')
procurarepw.grid(column=3, row=l, padx=10)

l += 1

vazio = ttk.Label(inicio, text="",font=font,background='white')
vazio.grid( row=l,column=0, padx=10)

l += 1

tkButtonQuit = ttk.Button(inicio, text="   Sair    ",command=quit, style='TButton')
tkButtonQuit.grid(column=3, row=l, padx=10)
tkButtonConfirma = ttk.Button(inicio, text="  Confirmar  ",command=confirma_arqs, style='TButton')
tkButtonConfirma.grid(column=2, row=l, sticky = E)

l += 1

vazio = ttk.Label(inicio, text="",font=font,background='white')
vazio.grid( row=l,column=0, padx=10) 


tkTop.resizable(True,True)

tkTop.mainloop()


tk.mainloop()