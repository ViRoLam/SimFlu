
import numpy as np
import scipy.integrate as itg

#----------------------------------------- Constantes
g =  9.81             # pesanteur
rho0 = 1.0            # densité de base
mu = 0.0020           # facteur de viscosité
K = 10                # facteur de pression
K_NEAR = K*2          # facteur de pression près de la particule
R = 4
n=15


# Fonctions utilisées par ODEint
def RFD(v,t, F,m):
    [Fx,Fy] = F
    [vx,vy] = v
    dvdt = [Fx/m,Fy/m]
    return dvdt

def base_int(y,t,v):
    [vx,vy] = v
    dydt = [vx,vy]
    return dydt

#-----------------------------------------  Classe définissant les particules
class Particule():
    '''La classe permet de créer des particules, avec ses caractéristiques propres, mise à jour au cours de l'animation'''
    
    def __init__(self, rayon, masse, position, vitesse,taille):
        '''Initalise les paramètres principaux de la particule'''
        
        # Caractéristiques principales
        self.taille = taille
        self.masse = masse
        self.rayon = rayon
        self.voisinage = []
        
        self.position = np.array(position) 
        self.vitesse = np.array(vitesse)
        self.force = np.array([0,-self.masse*g])

        # Densité et pression
        self.rho = 0.0
        self.rho_near = 0.0
        self.press = 0.0
        self.press_near = 0.0
        
        #Stock des positions et vitesse au cours de la simulation
        self.all_pos = [np.copy(self.position)]
        self.all_vit = [np.copy(self.vitesse)]
        self.all_for = [np.copy(self.force)]
        self.all_vit_norme = [np.linalg.norm(np.copy(self.vitesse))]


    def maj_voisinage(self, particule):
        '''Permet d'ajouter une particule b dans le voisinage d'une particule a si elles son suffisamment proches'''
        d = np.linalg.norm(self.position-particule.position)
        R = self.rayon+particule.rayon
        if d < R and d != 0:
            self.voisinage.append(particule)


    def maj_particule(self,dt):
        '''Fonction de mise à jour de la particule '''
        
        # Mise à jour de la vitesse, selon la RFD: mdv/dt = F
        [vx,vy] = self.vitesse
        [Fx,Fy] = self.force
        m = self.masse
        sol = np.transpose(itg.odeint(RFD,[vx,vy],t=[0,dt],args=([Fx,Fy],m)))
        self.vitesse = np.array([sol[0,1],sol[1,1]])
        
        # Mise à jour de la position, par dérivation : dx/dt = v
        [vx,vy] = self.vitesse
        [x,y] = self.position
        sol2 = np.transpose(itg.odeint(base_int,[x,y],t=[0,dt],args=([vx,vy],)))
        self.position =np.array([sol2[0,1],sol2[1,1]])
        
        # Remise à g de la force
        self.force = np.array([0,-self.masse*g])

        # Réduit la vitesse si elle devient trop grande
        if np.linalg.norm(self.vitesse)> 5.0:
            self.vitesse *= 0.5
            
        elif np.linalg.norm(self.vitesse[0]) > 4:
            self.vitesse[0] *= 0.01

        # Contraintes du sol et des parois
        if (self.position[1]-self.rayon) <0:
            self.force[1] =self.masse*(abs(self.vitesse[1])/dt)
            self.position[1] = self.rayon
            
            if self.position[0] < 0:
                self.force[0] = self.masse*(abs(self.vitesse[0])/dt)

            elif self.position[0]>self.taille:
                self.force[0] = self.masse*(-abs(self.vitesse[0])/dt)
                
        if self.position[0]-self.rayon<0:
            self.force[0] = self.masse*(abs(self.vitesse[0])/dt)
            
        elif self.position[0]+self.rayon>self.taille:
            self.force[0] = self.masse*(-abs(self.vitesse[0])/dt)
        
        # Diminution de la vitesse sur les couches basses
        for i in range(n):
            if self.position[1]<=self.rayon+i and self.position[1]>= self.rayon +i-1:
                if self.vitesse[0]>0:
                    self.vitesse[0]-=(1-i/n)*self.vitesse[0]
                elif self.vitesse[0]<0:
                    self.vitesse[0]-=(1-i/n)*self.vitesse[0]
                    
        # Mise à jour de toutes les positions
        self.all_pos.append(np.copy(self.position)) 
        self.all_vit.append(np.copy(self.vitesse)) 
        self.all_vit_norme.append(np.linalg.norm(np.copy(self.vitesse))) 

        # Mise à zéro de la densité, de la pression et du voisinage
        self.rho = 0.0
        self.rho_near = 0.0
        self.press = 0.0
        self.press_near = 0.0
        self.voisinage = []
        
    def pression(self):
        '''  Pression propre de la particule '''
        
        self.press = K * (self.rho - rho0)
        self.press_near = K_NEAR * self.rho_near
    
    