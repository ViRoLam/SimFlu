import numpy as np
from PIL import Image, ImageTk,ImageFilter
from scipy.special import erf
import datetime
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import threading
import random
import time 
from modules.SimFlu_fluid import Fluid,Fluid2

import cv2
from scipy.ndimage import binary_erosion
from scipy.ndimage import gaussian_filter
from tkinter.colorchooser import askcolor


def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

def hex_to_rgb(hex):
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class AjoutPointFrame(tk.Frame):
    def __init__(self, master=None,SimFlu=None):
        super().__init__(master)
        self.master = master
        self.pack()

        #on va récupérer les variables de la fenêtre principale
        self.SimFlu = SimFlu

        self.create_widgets()
        self._watch_variables(
            self.slider_posx_var,
            self.slider_posy_var,
            self.slider_taille_var,
            self.slider_vitesse_var,
            self.slider_direction_var,
            self.variable_checkbox_encre,
            self.variable_combobox_mode
            )
        self._update_canvas()
    
    def _watch_variables(self, *variables):
        for var in variables:
            var.trace_add("write", self._handle_trace)
    
    def _handle_trace(self, *args):
        print("trace", args)
        self._update_canvas()

    def _update_canvas(self):
        # on va récupérer les valeurs des sliders
        posx = int(self.slider_posx.get())
        posy = int(self.slider_posy.get())
        taille = int(self.slider_taille.get())
        vitesse = int(self.slider_vitesse.get())
        direction = int(self.slider_direction.get())/180*np.pi
        encre = int(self.variable_checkbox_encre.get())

        tree = self.SimFlu.tree
        #on va créer un canvas pour afficher la position du point
        #self.canvas = tk.Canvas(self,width=RESOLUTION[0],height=RESOLUTION[1],bg="white")
        #self.canvas.grid(row=0,column=2,rowspan=6)
        self.canvas.delete("all")
        #on va créer un cercle pour afficher le point
        self.canvas.create_oval(posx,posy,posx+taille,posy+taille,fill="black" if encre == 1 else "white")

        #on va ajouter une flèche pour afficher la direction et la vitesse 

        if self.variable_combobox_mode.get()=="Directionnel":
            self.canvas.create_line(posx+taille//2,posy+taille//2,posx+taille//2+np.cos(direction)*vitesse*10,posy+taille//2+np.sin(direction)*vitesse*10,arrow=tk.LAST)
        elif self.variable_combobox_mode.get()=="Divergent":
            nb_fleches = 8
            for i in range(nb_fleches):
                print("creation de la fleche",i)
                self.canvas.create_line(posx+taille//2,posy+taille//2,posx+taille//2+np.cos(i/nb_fleches*2*np.pi)*vitesse*10,posy+taille//2+np.sin(i/nb_fleches*2*np.pi)*vitesse*10,arrow=tk.LAST)
        
        #on ajoute les points de départ, qui sont stockés dans tree
        for i in tree.get_children():
            posy,posx = [int(i) for i in tree.item(i)["values"][0].split(" ")]
            taille_point = int(tree.item(i)["values"][1])
            vitesse_point = int(tree.item(i)["values"][2])
            direction_point = int(tree.item(i)["values"][3])/180*np.pi
            encre = int(tree.item(i)["values"][4])
            mode = tree.item(i)["values"][5]
            
            #on va créer un cercle pour afficher le point
            self.canvas.create_oval(posx,posy,posx+taille_point,posy+taille_point,fill="black" if encre == 1 else "white")

            #on va ajouter une flèche pour afficher la direction et la vitesse
            print(self.variable_combobox_mode.get(),i) 
            if mode=="Directionnel":
                self.canvas.create_line(posx+taille_point//2,posy+taille_point//2,posx+taille_point//2+np.cos(direction_point)*vitesse_point*10,posy+taille_point//2+np.sin(direction_point)*vitesse_point*10,arrow=tk.LAST)
            elif mode=="Divergent":
                nb_fleches = 8
                for i in range(nb_fleches):
                    print("creation de la fleche",i)
                    self.canvas.create_line(posx+taille_point//2,posy+taille_point//2,posx+taille_point//2+np.cos(i/nb_fleches*2*np.pi)*vitesse_point*10,posy+taille_point//2+np.sin(i/nb_fleches*2*np.pi)*vitesse_point*10,arrow=tk.LAST)
                #self.canvas.create_line(posx+taille_point//2,posy+taille_point//2,posx+taille_point//2-np.cos(direction_point)*vitesse_point*10,posy+taille_point//2-np.sin(direction_point)*vitesse_point*10,arrow=tk.LAST)
        #si il y a des murs on les affiche 
        if self.SimFlu.variable_checkbox_murs.get() == 1:
            murs_width = 5
            self.canvas.create_line(0,murs_width,self.SimFlu.RESOLUTION[0],murs_width,fill="black",width=murs_width)
            self.canvas.create_line(murs_width,0,murs_width,self.SimFlu.RESOLUTION[1],fill="black",width=murs_width)
            self.canvas.create_line(self.SimFlu.RESOLUTION[0],0,self.SimFlu.RESOLUTION[0],self.SimFlu.RESOLUTION[1],fill="black",width=murs_width)
            self.canvas.create_line(0,self.SimFlu.RESOLUTION[1],self.SimFlu.RESOLUTION[0],self.SimFlu.RESOLUTION[1],fill="black",width=murs_width)
        self.canvas.update()

    
    def create_widgets(self):
        #on va ajouter un canvas pour afficher la position du point
        self.canvas = tk.Canvas(self,width=self.SimFlu.RESOLUTION[0],height=self.SimFlu.RESOLUTION[1],bg="grey")
        self.canvas.grid(row=0,column=2,rowspan=6)


        # on va rendre tout ça plus joli, avec des grid 
        #on va donner des noms aux sliders, pour pouvoir récupérer leurs valeurs
        # on va ajouter deux labels pour la position
        label = tk.Label(self,text="x:")
        label.grid(row=0,column=0)

        label = tk.Label(self,text="y:")
        label.grid(row=1,column=0)

        # on va ajouter deux sliders pour la position

        self.slider_posx_var = tk.IntVar()
        self.slider_posx = tk.Scale(self, from_=0, to=self.SimFlu.RESOLUTION[0], orient=tk.HORIZONTAL,variable=self.slider_posx_var)
        self.slider_posx.set(self.SimFlu.RESOLUTION[0]//2)
        self.slider_posx.grid(row=0,column=1)

        self.slider_posy_var = tk.IntVar()
        self.slider_posy = tk.Scale(self, from_=0, to=self.SimFlu.RESOLUTION[1],orient=tk.HORIZONTAL,variable=self.slider_posy_var)
        self.slider_posy.set(self.SimFlu.RESOLUTION[1]//2)
        self.slider_posy.grid(row=1,column=1)

        # on va ajouter un label pour la taille
        label = tk.Label(self,text="Taille")
        label.grid(row=2,column=0)
        # on va ajouter un slider pour la taille
        self.slider_taille_var = tk.IntVar()
        self.slider_taille = tk.Scale(self, from_=3, to=20, orient=tk.HORIZONTAL,variable=self.slider_taille_var)
        self.slider_taille_var.set(10)
        self.slider_taille.grid(row=2,column=1)

        # on va ajouter un label pour la vitesse
        label = tk.Label(self,text="Vitesse")
        label.grid(row=3,column=0)
        # on va ajouter un slider pour la vitesse
        self.slider_vitesse_var = tk.IntVar()
        self.slider_vitesse_var.set(1)
        self.slider_vitesse = tk.Scale(self, from_=0, to=6, orient=tk.HORIZONTAL,variable=self.slider_vitesse_var)
        self.slider_vitesse.grid(row=3,column=1)
        


        # on va ajouter un label pour la direction
        label = tk.Label(self,text="Direction")
        label.grid(row=4,column=0)
        # on va ajouter un slider pour la direction
        self.slider_direction_var = tk.IntVar()
        self.slider_direction = tk.Scale(self, from_=0, to=360, orient=tk.HORIZONTAL,variable=self.slider_direction_var)
        self.slider_direction.grid(row=4,column=1)


        #on va créer une checkbox pour l'encre 
        self.variable_checkbox_encre = tk.IntVar()
        checkbox_encre = tk.Checkbutton(self,text="Encre",variable=self.variable_checkbox_encre)
        self.variable_checkbox_encre.set(1)
        checkbox_encre.grid(row=5,column=0)

        #on va créer une combobox pour le mode
        self.variable_combobox_mode = tk.StringVar()
        combobox_mode = ttk.Combobox(self,textvariable=self.variable_combobox_mode)
        combobox_mode['values'] = ('Directionnel',"Divergent")
        combobox_mode.current(0)
        combobox_mode.grid(row=5,column=1)

        #On va mettre les prochains paramètres dans un autre frame
        frame = tk.Frame(self,bg="grey")
        frame.grid(row=6,column=0,columnspan=2)

        #On va ajouter un Slider pour le nombre de points aléatoires
        label = tk.Label(frame,text="Nombre de points aléatoires",bg="grey")
        label.pack(side=tk.LEFT)
        self.slider_nb_points = tk.Scale(frame, from_=1, to=20, orient=tk.HORIZONTAL,bg="grey")
        self.slider_nb_points.pack(side=tk.LEFT)

        # on va ajouter un bouton pour créer des points aléatoires
        button = tk.Button(frame,text="Créer les points aléatoires",command=self.creer_points_aleatoires,bg="grey")
        button.pack(side=tk.RIGHT)

        # on va ajouter un bouton pour valider
        button = tk.Button(self,text="Valider",command=self.valider_point)
        button.grid(row=7,column=0)
        # on va ajouter un bouton pour annuler
        button = tk.Button(self,text="Quitter",command=self.master.destroy)
        button.grid(row=7,column=1)

        #on va ajouter un bouton pour modifier les paramètres avec du code
        button = tk.Button(self,text="Modifier les paramètres avec du code",command=self.secret_bouton)
        button.grid(row=8,column=0,columnspan=2)

    def secret_bouton(self):
        self.top = tk.Toplevel(self.master)
        self.top.resizable(False,False)
        self.top.title("Modifier les paramètres avec du code")
        #il n'y a qu'une seule entry, et un bouton pour valider
        frame = tk.Frame(self.top)
        frame.pack()
        self.entry_code = tk.Text(frame)
        self.entry_code.insert(tk.INSERT,self.SimFlu.get_secret_buffer())
        self.entry_code.grid(row=0,column=1,padx=5,pady=5,ipadx=80,ipady=60)
        button = tk.Button(frame,text="Valider",command=self.valider_code)
        button.grid(row=1,column=0,columnspan=2)

    def valider_code(self):
        text =self.entry_code.get("1.0",tk.END)
        exec_namespace = {}
        exec(text,exec_namespace)
        #print(points)
        
        points = exec_namespace["points"]
        print(points)
        #on va ajouter les points à la liste
        for point in points:
            self.SimFlu.tree.insert('', tk.END, values=(point[0],point[1],point[2],point[3],point[4],point[5]))
        self.top.destroy()
        self._update_canvas()

        

    def valider_point(self):
        posx = int(self.slider_posx.get())
        posy = int(self.slider_posy.get())
        taille = int(self.slider_taille.get())
        vitesse = int(self.slider_vitesse.get())
        direction = int(self.slider_direction.get())
        encre = int(self.variable_checkbox_encre.get())
        mode = self.variable_combobox_mode.get()

        self.SimFlu.tree.insert('', tk.END, values=((posy,posx),taille,vitesse,direction,encre,mode))
        #self.master.destroy()
    
    def creer_points_aleatoires(self):
        nb_points = int(self.slider_nb_points.get())
        for i in range(nb_points):
            posx = np.random.randint(0,self.SimFlu.RESOLUTION[0])
            posy = np.random.randint(0,self.SimFlu.RESOLUTION[1])
            taille = np.random.randint(3,20)
            vitesse = np.random.randint(1,5)
            direction = np.random.randint(0,360)
            encre = np.random.randint(0,2)
            mode = random.choice(['Directionnel',"Divergent"])
            self.SimFlu.tree.insert('', tk.END, values=((posx,posy),taille,vitesse,direction,encre,mode))
        self._update_canvas()
        #newWindow.destroy()


#Classe principale de cette simulation 
class SimFlu():
    def __init__(self,master) -> None:
        #On commence par définir les paramètres de la simulation ainsi que les constantes
        self.RESOLUTION = 200, 200
        self.SCALE = 3

        #taille du canvas des paramètres
        self.parameter_size = 350
        self.SIMULATION_SPEED_MAX = 10
        self.SIMULATION_SPEED_MIN = 1
        self.NOM_APPLI = "SimFlu"

        self.colors = [None,'#8b32a8n',None]

        #on va créer une liste qui va contenir les frames
        self.frames = []

        self.setup_window(master)
        self.create_widgets()

    def setup_window(self,master):
        self.root = master#tk.Tk(master)
        self.root.title(self.NOM_APPLI)
        self.root.geometry(f"{self.RESOLUTION[0]*self.SCALE+self.parameter_size}x{self.RESOLUTION[1]*self.SCALE}")
        self.root.configure(bg="black")
        self.root.resizable(True,True)

    def create_widgets(self):
        #on va créer les widgets 
        self.create_simulation_window()
        self.create_parameter_window()
    
    def create_simulation_window(self):
        #On va créer un canvas qui va contenir la simulation
        self.simulation_window = tk.Frame(self.root, bg="black",width=self.RESOLUTION[0]*self.SCALE, height=self.RESOLUTION[1]*self.SCALE)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.simulation_window.grid(row=0,column=0,sticky="nsew")
        self.my_label = tk.Label(self.simulation_window,bg="black")
        self.my_label.pack()

    def create_parameter_window(self):
        #On va créer un canvas qui va contenir les paramètres
        self.canvas_param = tk.Canvas(self.root,width=self.parameter_size,height=self.RESOLUTION[1]*self.SCALE,bg="white")
        self.canvas_param.grid(row=0,column=1,sticky="nsew")

        #on va ajouter un label pour les paramètres
        self.label_param = tk.Label(self.canvas_param,text="Paramètres",bg="white")
        self.label_param.grid(row=0,column=0)

        #on va créer un treeview pour recenser les points de départ
        self.colonnes = ("Position","Taille","Vitesse","Direction","Encre","Directionnel")
        self.tree = ttk.Treeview(self.canvas_param,column=self.colonnes,show="headings")
        for i in range(len(self.colonnes)):
            self.tree.heading(i,text=self.colonnes[i])
            self.tree.column(i,minwidth=65,width=65)
        self.tree.grid(row=1,column=0,columnspan=2)

        #On va ajouter un bouton pour ajouter un point
        self.button_modifier = tk.Button(self.canvas_param,text="Modifier les paramètres",command=self.modifier_parametres)
        self.button_modifier.grid(row=2,column=0)

        #On va ajouter un bouton pour supprimer un point
        self.button_supprimer = tk.Button(self.canvas_param,text="Supprimer",command=self.supprimer_source)
        self.button_supprimer.grid(row=2,column=1)

        #On va créer un slider pour la durée de la simulation
        self.label = tk.Label(self.canvas_param,text="Durée de la simulation")
        self.label.grid(row=3,column=0)
        self.slider_duree = tk.Scale(self.canvas_param, from_=10, to=400, orient=tk.HORIZONTAL)
        self.slider_duree.set(50)
        self.slider_duree.grid(row=3,column=1)


        
      



        #on va ajouter une checkbox pour savoir si l'utilisateur veut être en mode interactif
        self.variable_checkbox_interactif = tk.IntVar()
        self.checkbox_interactif = tk.Checkbutton(self.canvas_param,text="Mode interactif",variable=self.variable_checkbox_interactif)
        self.checkbox_interactif.grid(row=5,column=0)

        #on ajoute un label pour la vitesse de la simulation
        self.label = tk.Label(self.canvas_param,text="Vitesse de la simulation")
        self.label.grid(row=6,column=0)
        #on ajoute un slider pour la vitesse de la simulation
        self.slider_vitesse_sim = tk.Scale(self.canvas_param, from_=self.SIMULATION_SPEED_MIN, to=self.SIMULATION_SPEED_MAX, orient=tk.HORIZONTAL)
        self.slider_vitesse_sim.set(10)
        self.slider_vitesse_sim.grid(row=6,column=1)

        #on ajoute une checkbox pour savoir si l'utilisateur veut afficher les murs
        self.variable_checkbox_murs = tk.IntVar()
        self.checkbox_murs = tk.Checkbutton(self.canvas_param,text="Afficher les murs",variable=self.variable_checkbox_murs)
        self.checkbox_murs.grid(row=7,column=0)

        #on ajoute un paramètre (scale) pour contrôler l'aspect fumée
        self.label = tk.Label(self.canvas_param,text="Aspect fumée")
        self.label.grid(row=8,column=0)
        self.slider_aspect_fumee = tk.Scale(self.canvas_param, from_=0, to=7, orient=tk.HORIZONTAL)
        self.slider_aspect_fumee.set(1)
        self.slider_aspect_fumee.grid(row=8,column=1)

        #on ajouter une checkbox pour savoir si l'utilisateur veut afficher le glow 
        self.variable_checkbox_glow = tk.IntVar()
        self.checkbox_glow = tk.Checkbutton(self.canvas_param,text="Glow",variable=self.variable_checkbox_glow)
        self.checkbox_glow.grid(row=9,column=0)

        #on va ajouter une checkbox pour savoir si l'utilisateur veut choisir une couleur 
        self.variable_checkbox_color_chooser = tk.IntVar()
        self.checkbox_color_choser = tk.Checkbutton(self.canvas_param,text="Choisir couleur",variable=self.variable_checkbox_color_chooser)
        self.checkbox_color_choser.grid(row=10,column=0)

        #si la personne choisit de prendre une couleur, on veut aussi pouvoir choisir la couleur 
        self.choisir_couleur_button = tk.Button(self.canvas_param,text="couleur",command=self.choisir_couleur)
        self.choisir_couleur_button.grid(row=10,column=1)


        #on va créer un bouton pour lancer la simulation
        self.button = tk.Button(self.canvas_param,text="Lancer la simulation",command=self.lancer_simulation)
        self.button.grid(row=11,column=0)

        #on va créer un bouton pour sauvegarder la simulation
        self.button_sauvegarde = tk.Button(self.canvas_param,text="Sauvegarder",command=self.save_simulation)
        self.button_sauvegarde.grid(row=11,column=1)

        #on va créer une barre de progression
        self.progress_bar = ttk.Progressbar(self.canvas_param,orient=tk.HORIZONTAL,length=200,mode='determinate')
        self.progress_bar.grid(row=12,column=0,columnspan=2)

    def choisir_couleur(self):
        self.colors = askcolor(title="Choisit une couleur pour l'animation")

    def lancer_simulation(self):
        #on desactive le bouton de lancement
        self.button.configure(state="disabled")
        self.button_sauvegarde.configure(state="disabled")

        #on va récupérer les points de départ
        #on va créer un tableau qui va contenir les points de départ
        points = []

        #On y ajoute les points de départ qui sont stockés dans tree
        for i in self.tree.get_children():
            points.append(self.tree.item(i)["values"])

        #On créer le fluide 
        fluid = Fluid(self.RESOLUTION, 'dye')
        inflow_dye = np.zeros(fluid.shape)
        inflow_velocity = np.zeros_like(fluid.velocity)


        for point in points:
            #print(point)
            posx,posy = [int(i) for i in point[0].split(" ")]
            #print(posx,posy)
            taille_point = int(point[1])
            vitesse_point = int(point[2])
            direction_point = int(point[3])/180*np.pi
            point_arr = np.array([posx+taille_point//2,posy+taille_point//2])
            mask = np.linalg.norm(fluid.indices - point_arr[:, None, None], axis=0) <= taille_point
            if point[5]=="Directionnel":
                inflow_velocity[:, mask] += np.array([np.sin(direction_point),np.cos(direction_point)])[:, None] * vitesse_point
            elif point[5]=="Divergent":
                x0 = posx+taille_point//2
                y0 = posy+taille_point//2
                #print(fluid.shape)
                f = lambda x,y: np.array([2*(x-x0),2*(y-y0)])
                arr = np.zeros_like(inflow_velocity)
                for i in range(fluid.shape[0]):
                    for j in range(fluid.shape[1]):
                        if mask[i, j]:
                            vec = f(i, j)
                            norm = np.linalg.norm(vec)
                            # We place the vector in the last dimension of 'arr'
                            arr[:,i, j] = vec / (norm if norm != 0 else 1)

                # Now 'arr' is constructed to have the same shape as 'inflow_velocity'
                # and can be directly used in operations with 'inflow_velocity
                inflow_velocity += arr * vitesse_point
            if point[4]: inflow_dye[mask] = 1

        #Maintenant que tout est bien initialisé, on va lancer la simulation
        self.frames = []
        duree = int(self.slider_duree.get())

        color_params = np.array([0, 1, 255])
        #if self.variable_checkbox_couleur.get()==1:
        #    a = random.random()
        #    b = random.random()
        #    color_params = np.array([min(a,b),max(a,b), random.randint(30,220)])

        #on définit une fonction qui va afficher les images
        def afficher_image(i):
            #print(int(slider_vitesse_sim.get()))
            try:
                img = ImageTk.PhotoImage(self.frames[i])
                self.my_label.img = img
                self.my_label.configure(image=img)
                
                self.my_label.after(self.SIMULATION_SPEED_MAX+1-int(self.slider_vitesse_sim.get()),afficher_image,(i+1)%len(self.frames))
            except:
                #img = ImageTk.PhotoImage(frames[i-1])
                #my_label.img = img
                #my_label.configure(image=img)
                if self.variable_checkbox_interactif.get() == 1:
                    time.sleep(0.1)
                    if len(self.frames) > 0:
                        self.my_label.after(10,afficher_image,(i)%len(self.frames))
                    else:
                        self.my_label.after(10,afficher_image,(i))
        
        calculating = True
        #Si on est en mode interactif on va afficher la simulation au fur et à mesure
        if self.variable_checkbox_interactif.get() == 1:
            #t = threading.Thread(target=afficher_image,args=(1,))
            #t.start()
            afficher_image(1)
        self.checkbox_interactif.configure(state="disabled")

        for f in range(duree):
            print(f'Computing frame {f + 1} of {duree}.')

            #On ajoute les points de départ
            if f <= duree:
                fluid.velocity += inflow_velocity
                fluid.dye += inflow_dye

            divergence,curl,pressure = fluid.step(boundary=None,walls=self.variable_checkbox_murs.get()==1)
            
            curl = (erf(curl * 7)+1) / 8

            color = np.dstack((curl, np.ones(fluid.shape), fluid.dye))
            color = (np.clip(color, color_params[0], color_params[1]) * color_params[2]).astype('uint8') 
            if int(self.variable_checkbox_color_chooser.get())==1:
                color[:,:,0][color[:,:,0]>1] = rgb_to_hsv(*hex_to_rgb(self.colors[1]))[0]
            #arr[arr > 255] = x
            #Image.fromarray(color, mode='HSV').convert('RGB')
            #on ajoute un peu de transparence là où la couleur est moins forte 
            #alpha = Image.fromarray(np.clip(fluid.dye * 255, 0, 255).astype('uint8'),mode='L')
            #image.putalpha(alpha)
            image = Image.fromarray(color, mode='HSV').convert('RGB')
            
            if int(self.variable_checkbox_glow.get()) == 1:
                #hue_index = 0
                #other_indices = [0,1,2] 
                #other_indices.remove(hue_index)
                #hue = color[:,:,hue_index]
                
                #eroded = binary_erosion(image, iterations=3)
                image = image.filter(ImageFilter.GaussianBlur(radius = 1)) 
                edges = image.filter(ImageFilter.FIND_EDGES)
                # Make the outlined rectangles.
                #outlines = image - eroded
                image = np.array(image)
                edges = np.array(edges)
                # Convolve with a Gaussian to effect a blur.
                blur = np.clip(gaussian_filter(edges, sigma=7),0,255).astype('uint8')
                # Combine the images and constrain to [0, 1].
                blur_strength = 3
                glow =image + blur*blur_strength
                glow = glow.astype(float)
                glow *= (255/glow.max())
                #on ajoute un flou gaussien
                #print(glow.shape)
                #glow[:,:,2][glow[:,:,2]<40] = 0
                #image = Image.fromarray(glow, mode='HSV').convert('RGB')
                image =  Image.fromarray(glow.astype("uint8"))

            
            image = image.resize((self.RESOLUTION[0]*self.SCALE,self.RESOLUTION[1]*self.SCALE))
            image = image.filter(ImageFilter.GaussianBlur(radius = int(self.slider_aspect_fumee.get()))) 
            self.frames.append(image)
            #on change la progression
            self.progress_bar['value'] = f/duree*100
            self.root.update()
        calculating = False
        #une fois la simulation terminée, on va l'afficher

        #on reactive le bouton de lancement
        self.button.configure(state="normal")
        self.button_sauvegarde.configure(state="normal")

        if self.variable_checkbox_interactif.get() == 0:
            print("displaying simulation")
            afficher_image(1)
        self.checkbox_interactif.configure(state="normal")                

    def supprimer_source(self):
        selected_items = self.tree.selection()    
       
        for selected_item in selected_items:
            self.tree.delete(selected_item)

        #On regarde si l'ajout frame existe, si oui on met à jour le canvas
        if hasattr(self,"ajoutFrame"):
            self.ajoutFrame._update_canvas()

    def modifier_parametres(self):
        #on va créer une fenêtre pour modifier les paramètres
        self.top = tk.Toplevel(self.root)
        self.top.title("Modifier les paramètres")
        self.ajoutFrame = AjoutPointFrame(master=self.top,SimFlu=self)



    def save_simulation(self):
        try:
            self.frames[0].save(f'example-{datetime.datetime.now()}.gif', save_all=True, append_images=self.frames[1:], duration=20, loop=0)
        except Exception as e :
            messagebox.showerror("Erreur",f"Erreur lors de la sauvegarde de la simulation: {e}")

    def run(self):
        self.root.mainloop()


    def get_secret_buffer(self):
        buffer_secret = f'''
#Vous pouvez modifier les paramètres avec du code
#Pour cela, vous allez devoir spécifier la variable suivante:
# points: liste des points de départ
# Chaque point est une liste de 6 éléments:
#  - position: tuple (x,y)
#  - taille: int
#  - vitesse: int
#  - direction: int
#  - encre: int
#  - mode: str

import numpy as np
RESOLUTION = {self.RESOLUTION}
points = []

encre = 1 #1 si on veut que le point laisse une trace, 0 sinon
mode = "Directionnel" #Directionnel ou Divergent
vitesse = 1
taille = 7

#Exemple1:
points = []
points = [[(RESOLUTION[0]//2,RESOLUTION[1]//2),taille,vitesse,0,encre,mode]]
points.append([(RESOLUTION[0]//2-taille,RESOLUTION[1]//2),taille,vitesse,180,encre,mode])


#Exemple2 (cercle):
points = []

nb_points = 10
center = np.floor_divide(RESOLUTION, 2)
radius = np.min(center) - 60

positions = np.linspace(-np.pi, np.pi, nb_points, endpoint=False)
positions = tuple(np.array((np.cos(p), np.sin(p))) for p in positions)
normals = tuple(-p for p in positions)
positions = tuple(radius * p + center for p in positions)

print(positions)
for i,pos in enumerate(positions):
    direction = (i+2)*360/nb_points 
    points.append([(int(pos[0]),int(pos[1])),int(taille),int(vitesse),int(direction),encre,mode])

'''
        return buffer_secret
