import numpy as np
from scipy.ndimage import map_coordinates, spline_filter
from scipy.sparse.linalg import factorized

from scipy.sparse import csgraph


from functools import reduce
from itertools import cycle
from math import factorial

import numpy as np
import scipy.sparse as sp



'''
-------------------------------------------------------
Code de: https://github.com/GregTJ/stable-fluids
Modifié pour ajouter des murs
'''
def difference(derivative, accuracy=1):
    # Central differences implemented based on the article here:
    # http://web.media.mit.edu/~crtaylor/calculator.html
    derivative += 1
    radius = accuracy + derivative // 2 - 1
    points = range(-radius, radius + 1)
    coefficients = np.linalg.inv(np.vander(points))
    return coefficients[-derivative] * factorial(derivative - 1), points


def operator(shape, *differences):
    # Credit to Philip Zucker for figuring out
    # that kronsum's argument order is reversed.
    # Without that bit of wisdom I'd have lost it.
    differences = zip(shape, cycle(differences))
    factors = (sp.diags(*diff, shape=(dim,) * 2) for dim, diff in differences)
    return reduce(lambda a, f: sp.kronsum(f, a, format='csc'), factors)


class Fluid:
    def __init__(self, shape, *quantities, pressure_order=1, advect_order=3):
        self.shape = shape
        self.dimension = len(shape)

        # Prototyping is simplified by dynamically 
        # creating advected quantities as needed.
        self.quantities = quantities
        for q in quantities:
            setattr(self, q, np.zeros(shape))

        self.indices = np.indices(shape)
        self.velocity = np.zeros((self.dimension, *shape))

        self.laplacian = operator(shape, difference(2, pressure_order))
        self.pressure_solver = factorized(self.laplacian)

        
        self.advect_order = advect_order
    
    def step(self,boundary,walls=True):
        # Advection is computed backwards in time as described in Stable Fluids.
        advection_map = self.indices - self.velocity

        # SciPy's spline filter introduces checkerboard divergence.
        # A linear blend of the filtered and unfiltered fields based
        # on some value epsilon eliminates this error.
        def advect(field, filter_epsilon=10e-2, mode='constant'):
            filtered = spline_filter(field, order=self.advect_order, mode=mode)
            field = filtered * (1 - filter_epsilon) + field * filter_epsilon
            return map_coordinates(field, advection_map, prefilter=False, order=self.advect_order, mode=mode)

        # Apply advection to each axis of the
        # self.velocity field and each user-defined quantity.
        for d in range(self.dimension):
            self.velocity[d] = advect(self.velocity[d])
            if walls: #on peut soit arrêter le fluide soit le faire rebondir, ici on l'arrête
                if d == 0: 
                    self.velocity[d][:, 0] = 0#-self.velocity[d][:, 1]  
                    self.velocity[d][:, -1] = 0#-self.velocity[d][:, -2]  
                else:  
                    self.velocity[d][0, :] = 0#-self.velocity[d][1, :]
                    self.velocity[d][-1, :] = 0#-self.velocity[d][-2, :]
                

        for q in self.quantities:
            setattr(self, q, advect(getattr(self, q)))

        # Compute the jacobian at each point in the
        # self.velocity field to extract curl and divergence.
        jacobian_shape = (self.dimension,) * 2
        partials = tuple(np.gradient(d) for d in self.velocity)
        jacobian = np.stack(partials).reshape(*jacobian_shape, *self.shape)

        divergence = jacobian.trace()

        # If this curl calculation is extended to 3D, the y-axis value must be negated.
        # This corresponds to the coefficients of the levi-civita symbol in that dimension.
        # Higher dimension do not have a vector -> scalar, or vector -> vector,
        # correspondence between self.velocity and curl due to differing isomorphisms
        # between exterior powers in dimension != 2 or 3 respectively.
        curl_mask = np.triu(np.ones(jacobian_shape, dtype=bool), k=1)
        curl = (jacobian[curl_mask] - jacobian[curl_mask.T]).squeeze()

        # Apply the pressure correction to the fluid's self.velocity field.
        pressure = self.pressure_solver(divergence.flatten()).reshape(self.shape)

        self.velocity -= np.gradient(pressure)
        #On ajoute la viscocité

        return divergence, curl, pressure
'''
-------------------------------------------------------
'''    


'''
Fluide 2: basé sur l'article suivant: https://www.researchgate.net/publication/2560062_Real-Time_Fluid_Dynamics_for_Games
J'ai pas réussi à le faire fonctionner (bug dans l'advection, le code du gars est ILLISIBLE, il utilise des noms de variable que personne ne comprend), mais je le laisse ici au cas où 
'''
class Fluid2:
    def __init__(self, shape, *quantities):
        self.shape = shape
        self.dimension = len(shape)

        # Initialize self.dye and self.velocity fields
        self.dye = np.zeros(shape)
        self.velocity = np.zeros((2,shape[0],shape[1]))

        #Bon on touche pas à ça
        self.diffusion = 0.001
        self.viscosity = 0
        self.time_step = 1 #dt

        self.indices = np.indices(shape)

        self.prev_dye =np.zeros(shape)
        self.prev_velocity = np.zeros((2,shape[0],shape[1]))


    '''
    J'ai du réécrire cette fonction au moins 5 fois, et je suis toujours pas sûr de ce que je fais
    '''
    def step(self,boundary,walls=True):
        '''
        diffuse(1, self.prev_velocity[:,:,0], self.velocity[:,:,0], self.viscosity, self.time_step)
        diffuse(2, self.prev_velocity[:,:,1], self.velocity[:,:,1], self.viscosity, self.time_step)
        
        project(self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.velocity[:,:,0], self.velocity[:,:,1])
        
        advect(1, self.velocity[:,:,0], self.prev_velocity[:,:,0], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.time_step)
        advect(2, self.velocity[:,:,1], self.prev_velocity[:,:,1], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.time_step)
        
        project(self.velocity[:,:,0], self.velocity[:,:,1], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1])
        diffuse(0, self.prev_dye, self.dye, self.diffusion, self.time_step)
        advect(0, self.dye, self.prev_dye, self.velocity[:,:,0], self.velocity[:,:,1], self.time_step)
        self.prev_velocity,self.velocity = self.velocity.copy(),self.prev_velocity.copy()
        self.prev_dye,self.dye = self.dye.copy(),self.prev_dye.copy()
        #self.prev_velocity = self.velocity
        #self.prev_dye = self.dye
        '''
        #self.velocity steps 
        self.prev_velocity,self.velocity = self.velocity.copy(),self.prev_velocity.copy()
        self.diffuse(1, self.prev_velocity[:,:,0], self.velocity[:,:,0], self.viscosity, self.time_step)
        self.diffuse(2, self.prev_velocity[:,:,1], self.velocity[:,:,1], self.viscosity, self.time_step)
        self.project(self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.velocity[:,:,0], self.velocity[:,:,1])
        self.prev_velocity,self.velocity = self.velocity.copy(),self.prev_velocity.copy()
        self.advect(1, self.velocity[:,:,0], self.prev_velocity[:,:,0], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.time_step)
        self.advect(2, self.velocity[:,:,1], self.prev_velocity[:,:,1], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1], self.time_step)
        self.project(self.velocity[:,:,0], self.velocity[:,:,1], self.prev_velocity[:,:,0], self.prev_velocity[:,:,1])
        #self.dye steps
        #self.prev_dye,self.dye = self.dye.copy(),self.prev_dye.copy()
        self.diffuse(0, self.prev_dye, self.dye, self.diffusion, self.time_step)
        self.prev_dye,self.dye = self.dye.copy(),self.prev_dye.copy()
        self.advect(0, self.prev_dye, self.dye, self.velocity[:,:,0], self.velocity[:,:,1], self.time_step)
        return None,self.dye,self.velocity
    
    def advect(self,b, d, d0, velocX, velocY, dt):
        dtx = dt * (self.dimension - 2)
        dty = dt * (self.dimension - 2)

        for i in range(1, self.dimension - 1):
            for j in range(1, self.dimension - 1):
                tmp1 = dtx * velocX[i,j]
                tmp2 = dty * velocY[i,j]
                x = i - tmp1
                y = j - tmp2

                if x < 1.5:
                    x = 1.5
                if x > self.dimension - 1.5:
                    x = self.dimension - 1.5

                i0 = int(x)
                i1 = i0 + 1

                if y < 1.5:
                    y = 1.5
                if y > self.dimension - 1.5:
                    y = self.dimension - 1.5

                j0 = int(y)
                j1 = j0 + 1

                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1

                d[i, j] = s0 * (t0 * d0[i0, j0] + t1 * d0[i0, j1]) + s1 * (t0 * d0[i1, j0] + t1 * d0[i1, j1])

        self.set_bnd(b, d)
        #return d 

    def project(self,velocX, velocY, p, div):
        for i in range(1, self.dimension - 1):
            for j in range(1, self.dimension - 1):
                div[i,j] = -0.5*(velocX[i+1,j] - velocX[i-1,j] + velocY[i,j+1] - velocY[i,j-1])/self.dimension
                p[i,j] = 0
        self.set_bnd(0, div)
        self.set_bnd(0, p)
        self.lin_solve(0, p, div, 1, 6)
        for i in range(1, self.dimension - 1):
            for j in range(1, self.dimension - 1):
                velocX[i,j] -= 0.5 * (p[i+1,j] - p[i-1,j]) * self.dimension
                velocY[i,j] -= 0.5 * (p[i,j+1] - p[i,j-1]) * self.dimension
        self.set_bnd(1, velocX)
        self.set_bnd(2, velocY)


    def diffuse(self,b, x, x0, diff, dt):
        a = dt * diff * (self.dimension - 2) * (self.dimension - 2)
        #for i in range(20):
        self.lin_solve(b, x, x0, a, 1 + 4 * a)

    def lin_solve(self,b, x, x0, a, c):
        cRecip = 1.0 / c
        for i in range(1, self.dimension - 1):
            for j in range(1, self.dimension - 1):
                x[i,j] = (x0[i,j] + a*(x[i-1,j] + x[i+1,j] + x[i,j-1] + x[i,j+1])) * cRecip
        self.set_bnd(b, x)

    def set_bnd(self,b, x):
        #bounce off the walls
        for i in range(1, self.dimension - 1):
            x[i,0] = -x[i,1] if b == 2 else x[i,1]
            x[i,self.dimension - 1] = -x[i,self.dimension - 2] if b == 2 else x[i,self.dimension - 2]
        for j in range(1, self.dimension - 1):
            x[0,j] = -x[1,j] if b == 1 else x[1,j]
            x[self.dimension - 1,j] = -x[self.dimension - 2,j] if b == 1 else x[self.dimension - 2,j]

        #we do the average here to make sure the corners are set properly
        x[0,0] = 0.5 * (x[1,0] + x[0,1])
        x[0,self.dimension - 1] = 0.5 * (x[1,self.dimension - 1] + x[0,self.dimension - 2])
        x[self.dimension - 1,0] = 0.5 * (x[self.dimension - 2,0] + x[self.dimension - 1,1])
        x[self.dimension - 1,self.dimension - 1] = 0.5 * (x[self.dimension - 2,self.dimension - 1] + x[self.dimension - 1,self.dimension - 2])

