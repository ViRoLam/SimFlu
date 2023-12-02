
import numpy as np
from modules.SPH_particule import*

#--------------------------------------------------------Fonctions de densité, de pression et de viscosité
def func_dens(list_particules):
    '''Fonction qui calcule la densité de particule au voisinage de chaque particule'''
    
    for particule in list_particules:
        densite = 0.0
        densite_near = 0.0
        for particule_b in particule.voisinage:
            d = np.linalg.norm(particule.position-particule_b.position) # Distance entre les particules
            R = (particule.rayon + particule_b.rayon)/1.5
            d_norm = 1 - d / R # Normalisation et adimensionnement
            
            if d < R :
            
            # On définit une densité et une densité proche
            
                densite += d_norm**2
                densite_near += d_norm**3
                particule_b.rho += d_norm**2
                particule_b.rho_near += d_norm**3
        
        particule.rho += densite
        particule.rho_near += densite_near
        
                
def func_press_visc(list_particules):
    '''Fonction qui calcule les force de pression et de viscosité que subissent chaque particule à son voisinage'''
    
    for particule in list_particules:
        for particule_b in particule.voisinage:

            d = np.linalg.norm(particule.position-particule_b.position)
            R = (particule.rayon + particule_b.rayon)/1.5
            
            # Calcul des forces de pression normalisée
            d_norm = 1 - d / R
            ptot = (particule.press + particule_b.press)*d_norm**2 + (particule.press_near + particule_b.press_near)*d_norm**3
            pvect= (particule_b.position-particule.position)* ptot / d
            pvect[np.isnan(pvect[0])] = np.array([0,0])
            particule_b.force += pvect/2
            particule.force -= pvect/2

            diff_pos = particule_b.position - particule.position
            norm_pos = diff_pos/d
            relative_d = d/R
            if norm_pos[0]!=0 and norm_pos[1]!=0:
                diff_v = (particule.vitesse[0] - particule_b.vitesse[0])/norm_pos[0] + (particule.vitesse[1] - particule_b.vitesse[1])/norm_pos[1] 

            elif norm_pos[0]==0 and norm_pos[1]!=0:
                diff_v = (particule.vitesse[1] - particule_b.vitesse[1])/norm_pos[1]

            elif norm_pos[0]!=0 and norm_pos[1]==0:
                diff_v = (particule.vitesse[0] - particule_b.vitesse[0])/norm_pos[0]
            
            elif norm_pos == [0,0]:
                diff_v = 0


            # Calcul des forces de viscosité normalisées
            if diff_v>=0 and particule.position[1]>R and particule_b.position[1] >R:
                viscosity_force = (1 - relative_d)*mu*diff_v*norm_pos
                particule.vitesse -= viscosity_force
                particule_b.vitesse += viscosity_force
            