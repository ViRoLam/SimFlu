import numpy as np

#Constantes
kb = 1.38064852e-23 #Constante de Boltzmann

'''Classe principale pour les différentes simulations de gaz parfait, et fonctions de base pour les simulations '''

class Particule():
    def __init__(self, rayon, masse, position, vitesse):
        '''Initalise les paramètres principaux de la particule, 
        position et vitesse sont des vecteurs 2D de la forme [x,y] et [vx,vy]
        '''

        #Caractéristiques principales
        self.masse=masse
        self.rayon = rayon
        self.position = np.array(position) 
        self.vitesse = np.array(vitesse)


        #Stock des positions et vitesse au cours de la simulation
        self.all_pos = [np.copy(self.position)]
        self.all_vit = [np.copy(self.vitesse)]
        self.all_vit_norme = [np.linalg.norm(np.copy(self.vitesse))]
        self.compteur = []

    def maj_pos(self, dt):
        """Mise à jour de la position après un temps dt"""
        self.position += dt * self.vitesse
        self.all_pos.append(np.copy(self.position)) 
        self.all_vit.append(np.copy(self.vitesse)) 
        self.all_vit_norme.append(np.linalg.norm(np.copy(self.vitesse))) 

    def test_collision(self, particule):
        """Retourne True s'il y a eu une collision avec la particule_test
        Condition de collision: distance entre les centre des deux particules 
        est inférieure à la somme des deux rayons + petite marge d'erreur"""
        
        r1, r2 = self.rayon, particule.rayon
        pos1, pos2 = self.position, particule.position
        dist = np.linalg.norm(pos2-pos1) #Distance entre les deux particules

        if dist<(r1+r2): #Condition de collision 
            return True
        else:
            return False
        
    def maj_collision(self, particule, dt):
        """Mise à jour des vitesses dans le cas d'une collision avec une particule"""
        
        r1, r2 = self.rayon, particule.rayon
        v1, v2 = self.vitesse, particule.vitesse
        m1, m2 = self.masse, particule.masse
        pos1, pos2 = self.position, particule.position
        d = pos1-pos2
        norme = np.linalg.norm(d)

        if norme<(r1+r2):
            #équations de collision élastique
            self.vitesse = v1 - 2 * m2/(m1+m2) * np.dot(v1-v2, d) / (norme**2) * d
            particule.vitesse = v2 - 2 * m1/(m2+m1) * np.dot(v2-v1, (-d)) / (norme**2) * (-d)

        
    def maj_paroi(self, dt, taille):
        """Mise à jour des vitesse dans le cas où la particule atteint une paroi de la boîte et rebondit, 
        boite de dimension taille x taille.
        """
        count = 0
        r, v = self.rayon, self.vitesse, 
        x,y = self.position

        projx = dt*abs(np.dot(v,np.array([1.,0.]))) #projection verticale de la position 
        projy = dt*abs(np.dot(v,np.array([0.,1.]))) ##projection horizontale de la position 

        if np.abs(x)-r < projx or abs(taille-x)-r < projx: #Condition pour rebondir sur la paroi verticale
            self.vitesse[0] *= -1
            count +=1
        if np.abs(y)-r < projy or abs(taille-y)-r < projy: #Condition pour rebondir sur la paroi horizontale:  
            self.vitesse[1] *= -1.
            count +=1
        
        self.compteur.append(count)


    
def maj_all_pos(liste_particules, dt, taille):
    '''Fonction permettant de mettre à jour l'état des particules après un temps dt'''
    #Mise à jour des vitesses si collision ou rebond sur la paroi
    for i in range(len(liste_particules)):
        liste_particules[i].maj_paroi(dt,taille)
        for j in range(i+1,len(liste_particules)):
                liste_particules[i].maj_collision(liste_particules[j],dt)    

    #Mise à jour globale
    for particule in liste_particules:
        particule.maj_pos(dt)


def energie_totale(liste_particule): 
    '''Renvoie l'énergie totale du gaz'''
    E = sum([0.5 * liste_particule[i].masse * liste_particule[i].all_vit_norme[0]**2 for i in range(len(liste_particule))])
    #NB: l'énergie est constante au cours du temps, d'où le choix de l'énergie à l'instant initial
    return E

def generation_liste_particules(N,rayon,masse, taille):
    '''Création de listes de particules avec des états initiaux aléatoires'''
    liste_particules = []
    for i in range (N):
        pos =  rayon + np.random.rand(2)*(taille-2*rayon) 
        v = np.random.uniform(-10, 10, size=2)
        liste_particules.append(Particule(rayon, masse, pos, v))
    return liste_particules


def generation_liste_particules_bis(N,rayon,masse, taille, T):
    '''Création de listes de particules avec des états initiaux aléatoires'''
    liste_particules = []
    for i in range (N):
        pos =  rayon + np.random.rand(2)*(taille-2*rayon) 
        v_quadra = np.sqrt(2*kb*T/masse) * np.random.uniform(0.5,1.5)
        angle = np.random.rand()* 2* np.pi
        v = [v_quadra * np.cos(angle), v_quadra * np.sin(angle)]
        liste_particules.append(Particule(rayon, masse, pos, v))
    return liste_particules 


#Théorie, distribution Maxwell-Boltzamm

def MB_distribution(liste_particule):
    E = energie_totale(liste_particule)
    masse = liste_particule[0].masse
    E_moyenne = E/len(liste_particule) 
    vitesses = [liste_particule[j].all_vit_norme for j in range(len(liste_particule))]
    v = np.linspace(0,np.max(vitesses)*1.6,100)
    T = 2*E_moyenne/(2*kb) #température thermodynamique 
    distrib = masse *np.exp(-masse*v**2/(2*T*kb))/(2*np.pi*T*kb)*2*np.pi*v
    return v, distrib

def MB_distribution_bis(liste_particule,T):
    masse = liste_particule[0].masse
    vitesses = [liste_particule[j].all_vit_norme for j in range(len(liste_particule))]
    v = np.linspace(0,np.max(vitesses)*1.7,100)
    distrib = masse *np.exp(-masse*v**2/(2*T*kb))/(2*np.pi*T*kb)*2*np.pi*v
    return v, distrib

def pression(liste_particule,j):
    """Retourne la pression par intervalle de temps corresponant à j itérations"""
    N_it = len(liste_particule)
    chocs = np.array(liste_particule[0].compteur)
    for i in range(1,N_it):
        chocs += liste_particule[i].compteur

    pression=[]
    for i in range(N_it-j):
        data=sum(chocs[i:i+j])
        pression.append(data)
    for i in range(j):
        pression.append(data)
    return pression



