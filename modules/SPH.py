# Modules python de base
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.ttk as ttk
import datetime
from tkinter import messagebox

# Modules graphiques
import matplotlib as mpl
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1
import matplotlib.style as mplstyle
mplstyle.use(['dark_background','fast'])
save_count=60

# Modules spécifiques
from modules.SPH_particule import*
from modules.SPH_fonctions import*

class SPH():
    #----------------------------------------- Constantes de classe (modifiables)
    g =  9.81             # pesanteur
    rho0 = 1.0            # densité de base
    mu = 0.0020           # facteur de viscosité
    K = 10                # facteur de pression
    K_NEAR = K*2          # facteur de pression près de la particule
    n = 15
    R1,M,T = 3.5,0.85,90


    def __init__(self,master) -> None:
        self.NOM_APPLI = "SPH"
        self.anim = None


        self.setup_window(master)
        self.create_widgets()

    def setup_window(self,master):
        self.root = master
        self.root.title(self.NOM_APPLI)
        self.root.configure(bg="black")
        self.root.resizable(False,False)

    def create_widgets(self):
        self.create_parameter_window() 
        self.create_figure()
        self.create_simulation_window()

    def create_figure(self):
        #on va créer la figure
        if not hasattr(self, 'fig'):
            self.fig = plt.Figure(figsize=(5,5),dpi=100)
            self.ax = self.fig.add_subplot(111)

        self.liste_particule = self.generation_liste_particules()
        N = len(self.liste_particule)
        rayon = 4.85
        taille = 100
        x0,y0 = [self.liste_particule[i].all_pos[0][0] for i in range(N)],[self.liste_particule[i].all_pos[0][1] for i in range(N)]
        self.points = self.ax.scatter(x0, y0, s = 50*2**(rayon), alpha = 0.90)
        self.ax.set_xlim(0, taille)
        self.ax.set_ylim(rayon, taille/1.5)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        #self.ax.axis('off')



    def create_parameter_window(self):
        #On a plusieurs paramètres à modifier, on va créer une frame pour les paramètres
        self.parameter_frame = tk.Frame(self.root,bg="white")
        self.parameter_frame.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)

        #premier paramètre: nombre de particules
        self.nb_part_label = tk.Label(self.parameter_frame,text="Nombre de particules")
        self.nb_part_label.grid(row=0,column=0)
        self.nb_part_entry = tk.Entry(self.parameter_frame,width=10)
        self.nb_part_entry.insert(0,"120")
        self.nb_part_entry.grid(row=0,column=1)


        #quatrième paramètre: nombre d'itération
        self.nb_iter_label = tk.Label(self.parameter_frame,text="Nombre d'itération")
        self.nb_iter_label.grid(row=1,column=0)
        self.nb_iter_entry = tk.Entry(self.parameter_frame,width=10)
        self.nb_iter_entry.insert(0,"250")
        self.nb_iter_entry.grid(row=1,column=1)


        #on va créer un bouton pour lancer la simulation
        self.lancer_button = tk.Button(self.parameter_frame,text="Lancer la simulation",command=self.lancer_simulation)
        self.lancer_button.grid(row=4,column=0,columnspan=2)

        #on va créer un bouton pour sauvegarder la simulation
        self.sauvegarder_button = tk.Button(self.parameter_frame,text="Sauvegarder",command=self.sauvegarder)
        self.sauvegarder_button.grid(row=5,column=0,columnspan=2)

        #on ajoute une barre de progression
        self.progress_bar = ttk.Progressbar(self.parameter_frame,orient=tk.HORIZONTAL,length=200,mode='determinate')
        self.progress_bar.grid(row=6,column=0,columnspan=2)
        self.progress_bar['value'] = 0



    def sauvegarder(self):
        #on va sauvegarder la simulation
        #on va récupérer les paramètres
        N = int(self.nb_part_entry.get())
        nb_iteration = int(self.nb_iter_entry.get())

        #on va créer un nom de fichier
        nom_fichier = "SPH_"
        nom_fichier += str(N)+"_"
        nom_fichier += str(nb_iteration)+"_"
        nom_fichier += str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        nom_fichier += ".gif"

        #on va sauvegarder si on a déjà lancé une simulation
        if self.anim == None:
            messagebox.showerror("Erreur","Vous n'avez pas encore lancé de simulation")
            return 
        self.anim.save(nom_fichier, writer='imagemagick', fps=60)

    #-------------------------------------------------------- Fonctions de génération des particules et des grandeurs   
    def generation_liste_particules(self):
        '''Création de listes de particules avec des états initiaux aléatoires'''
        N = int(self.nb_part_entry.get())
        taille = 90
        rayon = 4.85
        masse = 0.85

        liste_particules = []
        for i in range (N):
            pos =  rayon + np.random.rand(2)*(taille/1.3-2*rayon) 
            v = np.random.rand(2)*1
            liste_particules.append(Particule(rayon,masse, pos, v,taille))
        return liste_particules 
    
    def maj_all(self,liste_particules, dt):
        '''Fonction permettant de mettre à jour l'état du système après un temps dt'''
        
        
        # Mise à jour des particules
        for particule in liste_particules:
            particule.maj_particule(dt)
            
        # Mise à jour des voisinages
        for particule in liste_particules:
            for particule_b in liste_particules:
                particule.maj_voisinage(particule_b)
            
        # Calcul de la densité
        func_dens(liste_particules)
        
        # Calcul de la pression
        for particule in liste_particules:
            particule.pression()
        
        # Application des forces de pression et de viscosité
        func_press_visc(liste_particules)

    def lancer_simulation(self):
        #on va lancer la simulation
        #on va récupérer les paramètres
        self.lancer_button["state"] = "disabled"
        self.sauvegarder_button["state"] = "disabled"
        self.N = int(self.nb_part_entry.get())
        self.taille = 100
        self.nb_iteration = int(self.nb_iter_entry.get())
        self.rayon = 4.85
        self.masse = 0.85
        
        #si la simulation est déjà lancée, on la stoppe
        if self.anim != None:
            self.anim.event_source.stop()
            self.anim._stop()
            self.anim = None
            #on va régénérer les axes 
            #self.fig.clear()
        self.ax.clear()
        self.create_figure()



        #on va créer la liste de particules
        dt = 0.15
        self.frames = []
        for i in range(self.nb_iteration):
            self.frames.append(self.liste_particule)
            self.maj_all(self.liste_particule, dt)
            self.progress_bar["value"] = i/self.nb_iteration*100
            self.root.update()
            if i%40==0:
                print("Itération numéro ",i, "...")
        print("Fin simulation")


        # Mise à jour des particules
        self.anim = FuncAnimation(self.fig, self.update, frames=int(self.nb_iter_entry.get()), interval=15)
        self.simulation_canvas.draw()
        self.lancer_button["state"] = "normal"
        self.sauvegarder_button["state"] = "normal"

    def update(self,i):
        global liste_particule
        dt = 0.15

        #self.maj_all(self.liste_particule, dt)
        self.liste_particule = self.frames[i]
        N = len(self.liste_particule)
        # Mise à jour du scatter plot (position des particules)
        x = [self.liste_particule[j].all_pos[i][0] for j in range(N)]
        y = [self.liste_particule[j].all_pos[i][1] for j in range(N)]
        self.points.set_offsets(np.transpose([x,y]))
        self.points.set_color((0,2.5/4,1))
        self.simulation_canvas.draw() #pas forcément utile, à tester
        self.root.update() #important pour que ça ne glitch pas
        return self.points,

    def create_simulation_window(self):
        #On va créer la fenêtre de simulation, cette fois ci on va utiliser matplotlib, donc on va créer un canvas spécial
        self.simulation_frame = tk.Frame(self.root)
        self.simulation_frame.grid(row=0,column=0)

        self.simulation_canvas = FigureCanvasTkAgg(self.fig, master=self.simulation_frame)  # A tk.DrawingArea.
        self.simulation_canvas.draw()
        self.simulation_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    


        
    def run(self):
        self.root.mainloop()