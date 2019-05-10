#!/usr/bin
# -*- coding: utf-8 -*-
""" Finite Element Digital Image Correlation method 
    JC Passieux, INSA Toulouse, 2017       """

import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse.linalg as splalg
import scipy as sp
import pyxel as px
import os

#%% ============================================================================
# Datafiles, images  ===========================================================
# ==============================================================================

imnums=np.array([53,54,57,58,61,62,65,66,69,70,75])
testcase='dic_composite'
imagefile=os.path.join('data',testcase,'zoom-0%03d_1.tif')
imref = imagefile % imnums[0]
f=px.Image(imref).Load()
f.Show()

#%% ============================================================================
# Mesh and Camera model  =======================================================
# ==============================================================================
''' Example2: Quadrilateral ABAQUS Mesh in meter '''
meshfile=os.path.join('data',testcase,'abaqus_q4_m.inp')
m=px.ReadMeshINP(meshfile)
#cam=px.MeshCalibration(f,m,[1,2])
cam=px.Camera(np.array([ 1.05168768e+04,  5.13737634e-02, -9.65935782e-02, -2.65443047e-03]))

# Plot Mesh on the reference image
px.PlotMeshImage(f,m,cam)
# Visualization of the mesh alone
m.Plot()

#%% ============================================================================
# Pre-processing  ==============================================================
# ==============================================================================

# Build the connectivity table
m.Connectivity()
# Build the quadrature rule; compute FE basis functions and derivatives
m.DICIntegration(cam)

# Open reference image
imdef = imagefile % imnums[-2]
g = px.Image(imdef).Load()

# Multiscale initialization of the displacement
U0=px.MultiscaleInit(m,f,g,cam,3)
m.Plot(U0,30)

#%% ============================================================================
# Classic Modified Gauss Newton  ===============================================
# ==============================================================================
U=U0.copy()
dic=px.DICEngine()
H=dic.ComputeLHS(f,m,cam)
H_LU=splalg.splu(H)
for ik in range(0,30):
    [b,res]=dic.ComputeRHS(g,m,cam,U)
    dU=H_LU.solve(b)
    U+=dU
    err=np.linalg.norm(dU)/np.linalg.norm(U)
    print("Iter # %2d | disc/dyn=%2.2f %% | dU/U=%1.2e" % (ik+1,np.std(res)/dic.dyn*100,err))
    if err<1e-3:
        break


#%% ============================================================================
# Post-processing  =============================================================
# ==============================================================================
# Visualization: Scaled deformation of the mesh
m.Plot(edgecolor='#CCCCCC')
m.Plot(U,30)
# Visualization: displacement fields
m.PlotContourDispl(U)
# Visualization: strain fields
m.PlotContourStrain(U)
# Plot deformed Mesh on deformed state image
px.PlotMeshImage(g,m,cam,U)


'''==========='''
''' EXERCISES '''
'''==========='''

#%% 1. Time Resolved DIC  ===================================================


#%% 2. Tikhonov Regularization  =====================================================

L=m.Tikhonov()
l=100000
U=U0.copy()


# copy-paste the classic Gauss-Newton
# and modify operators and right hand side...



# Displacement field visualization using matplotlib
m.Plot(U,30)


#%% 3. Mechanical Regularization  ===================================================

El=1.0e+10
Et=1.9e+10
vtl=0.18
Glt=1.0e+09
vlt=vtl*El/Et
alp=1/(1-vlt*vtl)
hooke=np.array([[alp*El     , alp*vtl*El,0    ],
                [alp*vlt*Et , alp*Et    ,0    ],
                [0          , 0         ,2*Glt]])

K=m.Stiffness(hooke)
# Select the non-free boundary nodes (here two lines)
# repb1=px.SelectMeshLine(m)
# repb2=px.SelectMeshLine(m)
repb1=np.array([ 12,  13, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235])
repb2=np.array([ 14,  15, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268])
repb=np.append(repb1,repb2)
dofb=m.conn[repb,:].ravel()
D=np.ones_like(U)
D[dofb]=0
D=sp.sparse.diags(D)
KK=K.T.dot(D.dot(K))


U=U0.copy()
l=0.0001

# copy-paste the classic Gauss-Newton
# and modify operators and right hand side...


# Displacement field visualization using matplotlib
m.Plot(U,30)


#%% 4. Experimental displacement driven simulation


#%% 5. Model Validation


#%% 6 Constitutive parameter identification

