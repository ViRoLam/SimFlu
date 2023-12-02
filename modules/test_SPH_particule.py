from SPH_particule import*
from pytest import*

#------------------------------------------------- Test de fonctions
def test_RFD():
    v = [1,1]
    t = 0
    F = [1,1]
    m = 1
    assert RFD(v,t,F,m) == [1,1]

def test_base_int():
    y = [1,1]
    t = 0
    v = [1,1]
    assert base_int(y,t,v) == [1,1]
    

#------------------------------------------------- Test de méthodes
def test_particule_init():
    p = Particule(rayon=1,masse=1, position=[0,0], vitesse=[0,0], taille = 1)
    assert p.rayon == 1
    assert p.masse == 1
    assert p.position == [0,0]
    assert p.vitesse == [0,0]
    assert p.taille == 1
    assert p.rho == 0.0
    assert p.rho_near == 0.0
    assert p.press == 0.0
    assert p.press_near == 0.0

def test_particule_maj_voisinage():
    p = Particule(rayon=1,masse=1, position=[0,0], vitesse=[0,0], taille = 1)
    p1 = Particule(rayon=1,masse=1, position=[0.1,0.1], vitesse=[0,0], taille = 1)
    p2 = Particule(rayon=1,masse=1, position=[10,10], vitesse=[0,0], taille = 1)
    p.maj_voisinage(p1)
    p.maj_voisinage(p2)
    assert p.voisinage == [p1]
    
def test_particule_maj_particule():
    dt = 1
    p = Particule(rayon=1,masse=1, position=[0,0], vitesse=[0,0], taille = 1)
    p.maj_particule(dt)
    assert p.rho == 0.0
    assert p.rho_near == 0.0
    assert p.voisinage == []