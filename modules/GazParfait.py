import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from modules.GP_particule import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import datetime
from tkinter import messagebox
import tkinter.ttk as ttk

class GazParfait():
    def __init__(self,master) -> None:      
        self.NOM_APPLI = "Gaz Parfait"  
        self.animation = None
        self.setup_window(master)
        self.create_widgets()

    def setup_window(self,master):
        self.root = master
        self.root.title(self.NOM_APPLI)
        self.root.configure(bg="black")
        self.root.resizable(False,False)

    def create_widgets(self):
        #on va créer les widgets
        self.create_parameter_window() 
        self.create_figure()
        self.create_simulation_window()


        
    def create_parameter_window(self):
        #On a plusieurs paramètres à modifier, on va créer une frame pour les paramètres
        self.parameter_frame = tk.Frame(self.root,bg="white")
        self.parameter_frame.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)

        #premier paramètre: nombre de particules
        self.nb_part_label = tk.Label(self.parameter_frame,text="Nombre de particules")
        self.nb_part_label.grid(row=0,column=0)
        self.nb_part_entry = tk.Entry(self.parameter_frame,width=10)
        self.nb_part_entry.insert(0,"300")
        self.nb_part_entry.grid(row=0,column=1)

        #deuxième paramètre: taille de la boîte
        self.taille_label = tk.Label(self.parameter_frame,text="Taille de la boîte")
        self.taille_label.grid(row=1,column=0)
        self.taille_entry = tk.Entry(self.parameter_frame,width=10)
        self.taille_entry.insert(0,"100")
        self.taille_entry.grid(row=1,column=1)

        #troisième paramètre: durée de la simulation
        self.duree_label = tk.Label(self.parameter_frame,text="Durée de la simulation")
        self.duree_label.grid(row=2,column=0)
        self.duree_entry = tk.Entry(self.parameter_frame,width=10)
        self.duree_entry.insert(0,"20")
        self.duree_entry.grid(row=2,column=1)

        #quatrième paramètre: nombre d'itération
        self.nb_iter_label = tk.Label(self.parameter_frame,text="Nombre d'itération")
        self.nb_iter_label.grid(row=3,column=0)
        self.nb_iter_entry = tk.Entry(self.parameter_frame,width=10)
        self.nb_iter_entry.insert(0,"200")
        self.nb_iter_entry.grid(row=3,column=1)

        #cinquième paramètre: rayon des particules
        self.rayon_label = tk.Label(self.parameter_frame,text="Rayon des particules")
        self.rayon_label.grid(row=4,column=0)
        self.rayon_entry = tk.Entry(self.parameter_frame,width=10)
        self.rayon_entry.insert(0,"1")
        self.rayon_entry.grid(row=4,column=1)

        #sixième paramètre: masse des particules
        self.masse_label = tk.Label(self.parameter_frame,text="Masse des particules")
        self.masse_label.grid(row=5,column=0)
        self.masse_entry = tk.Entry(self.parameter_frame,width=10)
        self.masse_entry.insert(0,"1e-23")
        self.masse_entry.grid(row=5,column=1)

        #septième paramètre: température
        self.temp_label = tk.Label(self.parameter_frame,text="Température")
        self.temp_label.grid(row=6,column=0)
        self.temp_entry = tk.Entry(self.parameter_frame,width=10)
        self.temp_entry.insert(0,"300")
        self.temp_entry.grid(row=6,column=1)

        #huitième paramètre: mode mélange, on ajoute une checkbox pour ce mode
        self.melange = tk.IntVar()
        self.melange_check = tk.Checkbutton(self.parameter_frame,text="Mode mélange",variable=self.melange)
        self.melange_check.grid(row=7,column=1)

        #on ajoute un bouton pour lancer la simulation
        self.lancer_button = tk.Button(self.parameter_frame,text="Lancer la simulation",command=self.lancer_simulation)
        self.lancer_button.grid(row=8,column=0,columnspan=2)

        #on ajoute un bouton pour sauvegarder la simulation
        self.sauvegarder_button = tk.Button(self.parameter_frame,text="Sauvegarder",command=self.sauvegarder)
        self.sauvegarder_button.grid(row=9,column=0,columnspan=2)

        #on ajoute une barre de progression
        self.progress_bar = ttk.Progressbar(self.parameter_frame,orient=tk.HORIZONTAL,length=200,mode='determinate')
        self.progress_bar.grid(row=10,column=0,columnspan=2)
        self.progress_bar["value"] = 0

    def generer_liste_particules_melange(self):
        #Données initiales spéciales
        taille = int(self.taille_entry.get())
        rayon, masse = float(self.rayon_entry.get()), float(self.masse_entry.get())
        N = int(self.nb_part_entry.get())
        colors = []
        liste_particule = []
        for i in range (N):
            pos =  rayon + np.random.rand(2)*(taille-2*rayon) 
            if pos[0]>taille/2:
                v= [np.random.rand() * -20,0]
                colors.append('r')
            else:
                v= [np.random.rand() * 20,0]
                colors.append('b')
            liste_particule.append(Particule(rayon, masse, pos, v))
        return liste_particule, colors  
    
    def lancer_simulation(self):
        #on va lancer la simulation
        #on va récupérer les paramètres
        self.lancer_button["state"] = "disabled"
        self.sauvegarder_button["state"] = "disabled"
        #si la simulation est déjà lancée, on la stoppe
        if self.animation != None:
            self.animation.event_source.stop()
            self.animation._stop()
            self.animation = None
        self.axs[0].cla()
        self.axs[1].cla()
        self.create_figure()
        
        
        self.N = int(self.nb_part_entry.get())
        self.taille = int(self.taille_entry.get())
        self.duree = int(self.duree_entry.get())
        self.nb_iteration = int(self.nb_iter_entry.get())
        self.rayon = float(self.rayon_entry.get())
        self.masse = float(self.masse_entry.get())
        self.T = int(self.temp_entry.get())
        print("Lancement de la simulation...")
        print("paramètres: ")
        print("Nombre de particules: ",self.N)
        print("Taille de la boîte: ",self.taille)
        print("Durée de la simulation: ",self.duree)
        print("Nombre d'itération: ",self.nb_iteration)
        print("Rayon des particules: ",self.rayon)

        #on va créer la liste de particules
        dt = self.duree/self.nb_iteration

        
        #On va créer le scatter plot
        # Initialisation des sous-graphiques
        if self.melange.get() == 1:
            liste_particule, colors = self.generer_liste_particules_melange()
            self.v, self.distrib = MB_distribution(liste_particule)
        else:
            liste_particule = generation_liste_particules_bis(self.N,self.rayon,self.masse, self.taille,self.T)
            colors = np.random.rand(self.N)
            self.v, self.distrib = MB_distribution_bis(liste_particule,self.T)
        x0,y0 = [liste_particule[j].all_pos[0][0] for j in range(self.N)], [liste_particule[j].all_pos[0][1] for j in range(self.N)]
        self.points = self.axs[0].scatter(x0, y0, s = 50**(self.rayon), alpha=0.7,c=colors, label='Température: '+str(self.T)+str(' K'))

        self.frames = []
        for i in range(self.nb_iteration):
            self.frames.append(liste_particule)
            maj_all_pos(liste_particule, dt, self.taille)
            self.progress_bar["value"] = i/self.nb_iteration*100
            self.root.update()
            if i%40==0:
                print("Itération numéro ",i, "...")
        print("Fin simulation")

        #on va calculer la pression
        #pression = pression(liste_particule, 10)
        self.pression = pression(liste_particule, 10)

        self.animation = FuncAnimation(self.fig, self.update,init_func=self.init ,frames=self.nb_iteration, interval=20)
        self.simulation_canvas.draw()
        self.lancer_button["state"] = "normal"
        self.sauvegarder_button["state"] = "normal"
    
    def init(self):
        #on va initialiser la figure
        self.axs[0].set_xlim(0, self.taille)
        self.axs[0].set_ylim(0, self.taille)
        #self.axs[0].set_title('Position des particules')
        self.axs[0].legend(loc='upper right')
    
        self.axs[1].set_title('Histogramme des vitesses')
        self.axs[1].set_xlabel('Vitesse')
        self.axs[1].set_ylabel("Densité")

        return self.points,
    
    def update(self,i):
        #on va mettre à jour la figure
        #on va récupérer la liste de particules
        liste_particule = self.frames[i]

        #on va mettre à jour le scatter plot
        x = [liste_particule[j].all_pos[i][0] for j in range(self.N)]
        y = [liste_particule[j].all_pos[i][1] for j in range(self.N)]
        self.axs[0].set_title(f'Pression : {self.pression[i%len(self.pression)]} Pa')
        self.points.set_offsets(np.c_[x,y])

        
        #on va mettre à jour l'histogramme
        self.axs[1].clear()
        self.axs[1].hist([liste_particule[j].all_vit_norme[i] for j in range(self.N)],bins=19,density=True)
        self.axs[1].plot(self.v,self.distrib,label = "Théorie (Maxwell-Boltzmann)", color="yellow")
        self.axs[1].grid(True, color='dimgrey',linewidth=0.5)
        self.axs[1].set_ylim(0,np.max(self.distrib)*1.8)#np.max(self.distrib)*1.8
        self.axs[1].set_xlim(0,np.max(self.v)*1.1) #np.max(self.v)*1.1
        self.axs[1].legend()
        self.simulation_canvas.draw()
        self.root.update()
        #self.axs[1].set_title('Histogramme des vitesses')
        #self.axs[1].set_xlabel('Vitesse')
        #self.axs[1].set_ylabel("Densité")

        return self.points,


    def create_figure(self):
        #on va créer la figure matplotlib
        plt.style.use('dark_background')
        if not hasattr(self,"fig"):
            self.fig, self.axs = plt.subplots(1, 2, figsize=(13, 6.5))

        self.fig.set_facecolor("black")
        self.axs[0].set_facecolor("black")
        self.axs[1].set_facecolor("black")

        self.axs[0].set_xlim(0, int(self.taille_entry.get()))
        self.axs[0].set_ylim(0, int(self.taille_entry.get()))
        self.axs[0].set_title('Position des particules')
        self.axs[0].legend(loc='upper right')
    
        self.axs[1].set_title('Histogramme des vitesses')
        self.axs[1].set_xlabel('Vitesse')
        self.axs[1].set_ylabel("Densité")

        #je l'ai ajouté mais faut faire attention, je sais pas si c'est utile, à tester
        self.axs[0].set_aspect('equal')
        #self.axs[1].set_aspect('equal')
        #self.fig.tight_layout()
        

    def create_simulation_window(self):
        #On va créer la fenêtre de simulation, cette fois ci on va utiliser matplotlib, donc on va créer un canvas spécial
        self.simulation_frame = tk.Frame(self.root)
        self.simulation_frame.grid(row=0,column=0)

        self.simulation_canvas = FigureCanvasTkAgg(self.fig, master=self.simulation_frame)  # A tk.DrawingArea.
        self.simulation_canvas.draw()
        self.simulation_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def sauvegarder(self):
        #on va sauvegarder la simulation, çàd l'animation 
        #on va créer un nom de fichier
        now = datetime.datetime.now()
        nom_fichier = "gaz_parfait_"+str(now.day)+"_"+str(now.month)+"_"+str(now.year)+"_"+str(now.hour)+"_"+str(now.minute)+"_"+str(now.second)+".gif"
        if hasattr(self,"animation"):
            self.animation.save(nom_fichier,fps=10)
        else:
            messagebox.showerror("Erreur","Vous devez d'abord lancer la simulation avant de pouvoir la sauvegarder")
    

    def run(self):
        self.root.mainloop()
