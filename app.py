import tkinter as tk
from tkinter import messagebox
import modules.SimFlu as SimFlu
import modules.GazParfait as GazParfait
import modules.SPH as SPH


class Interface(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #on créer le menu
        self.create_menu()

        self.app = None
        #On commence par choisir quelle app on veut lancer (par défaut SimFlu)
        self.switch_sim_flu() 

    def aide_simflu(self):
        messagebox.showinfo("Aide SimFlu","Programme de simulation de fluide\n\nPour ajouter un point de départ avec ses paramètres, cliquez sur le bouton Ajouter un point\n\nPour supprimer un point de départ, sélectionnez le point dans la liste et cliquez sur le bouton Supprimer un point\n\nPour lancer la simulation, cliquez sur le bouton Lancer la simulation\n\nPour sauvegarder la simulation, cliquez sur le bouton Sauvegarder\n\nVous pouvez modifier la vitesse de la simulation ainsi que la durée de la simulation avec les sliders correspondants\n\nVous pouvez aussi choisir d'afficher la simulation au fur et à mesure en cochant la case Mode interactif")

    def aide_gaz_parfait(self):
        messagebox.showinfo("Aide Gaz Parfait","Programme de simulation de gaz parfait avec des boules\n\nVous pouvez choisir les paramètres suivants: \n- Nombre de boules\n- Taille des boules\n- Température\n- Nombre de pas de temps\n-Durée de simulation\n-Masse des particules\n\nQuand vous êtes prêt, cliquez sur le bouton Lancer la simulation")

    def aide_sph(self):
        messagebox.showinfo("Aide SPH","Programme de simulation de fluide grâce à la méthode SPH\n\nVous pouvez choisir les paramètres suivants: \n- Nombre de particules\n- Taille de la fenêtre\n- Durée de la simulation\n-Nombre d'itération\n-Rayon des particules\n-Masse des particules\n\nQuand vous êtes prêt, cliquez sur le bouton Lancer la simulation")

    def create_menu(self,app="SimFlu"):
        #On va créer un menu
        self.menu_bar = tk.Menu(self)

        #On va créer un menu pour l'app 
        if app == "SimFlu":
            self.aide = self.aide_simflu
        elif app == "GazParfait":
            self.aide = self.aide_gaz_parfait
        elif app == "SPH":
            self.aide = self.aide_sph
        #Tout d'abord un menu pour pouvoir quitter l'app
        simflu_menu = tk.Menu(self.menu_bar,tearoff=0)
        simflu_menu.add_command(label="Quitter",command=self.quit)
        self.menu_bar.add_cascade(label="",menu=simflu_menu)

        #On va créer un menu pour l'aide (nom: Aide)
        aide_menu = tk.Menu(self.menu_bar,tearoff=0)

        aide_menu.add_command(label="Aide",command=self.aide)
        aide_menu.add_command(label="A propos",command=self.a_propos)
        self.menu_bar.add_cascade(label="Aide",menu=aide_menu)

        #on va créer un menu pour switch entre les app 
        self.switch_menu = tk.Menu(self.menu_bar,tearoff=0)
        self.switch_menu.add_command(label="SimFlu",command=self.switch_sim_flu)
        self.switch_menu.add_command(label="Gaz Parfait",command=self.switch_gaz_parfait)
        self.switch_menu.add_command(label="SPH",command=self.switch_sph)

        self.menu_bar.add_cascade(label="Switch App",menu=self.switch_menu)
        self.config(menu=self.menu_bar)


    def switch_sph(self):
        print("Switching app to SPH")
        self.clear("SPH")
        self.app = SPH.SPH(self)
        self.app.run()

    def switch_sim_flu(self):
        
        #on va voir quelle app on veut lancer
        #app = self.switch_menu.entrycget(0, "label")
        
        #on retire tout de la fenêtre avant de lancer l'app
        self.clear("SimFlu")

        print("Switching app to SimFlu")
        self.app = SimFlu.SimFlu(self)
        self.app.run()
    
    def switch_gaz_parfait(self):
        print("Switching app to Gaz Parfait")
        self.clear("GazParfait")
        self.app = GazParfait.GazParfait(self)
        self.app.run()

    def clear(self,app="SimFlu"):
        #on retire tout de cette fenêtre avant de lancer l'app
        for widget in self.winfo_children():
            widget.destroy()

        #on recrée le menu, parce qu'on l'a détruit mdr 
        self.create_menu(app=app)

    def a_propos(self):
        messagebox.showinfo("A propos", "Cette application a été crée par des étudiants de CentraleSupelec dans le cadre des Coding Weeks")
    #def aide(self):
    #    messagebox.showinfo("Aide","Programme de simulation de fluide\n\nPour ajouter un point de départ avec ses paramètres, cliquez sur le bouton Ajouter un point\n\nPour supprimer un point de départ, sélectionnez le point dans la liste et cliquez sur le bouton Supprimer un point\n\nPour lancer la simulation, cliquez sur le bouton Lancer la simulation\n\nPour sauvegarder la simulation, cliquez sur le bouton Sauvegarder\n\nVous pouvez modifier la vitesse de la simulation ainsi que la durée de la simulation avec les sliders correspondants\n\nVous pouvez aussi choisir d'afficher la simulation au fur et à mesure en cochant la case Mode interactif")


if __name__ == "__main__":
    interface = Interface()