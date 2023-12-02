from SPH_particule import*
from SPH_fonctions import*
from pytest import*

#-------------------------------------------------
p = Particule(rayon=1,masse=1, position=[0,0], vitesse=[0,0], taille = 1)
liste_particules = [p]

def test_func_dens():
    func_dens(liste_particules)
    assert p.rho == 0.0
    assert p.rho_near == 0.0

def test_func_press_visc():
    func_press_visc(liste_particules)
    assert p.position == [0.0]
    assert p.vitesse == [0.0]