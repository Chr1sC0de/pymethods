# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 12:56:58 2019

@author: chris
"""
from stl import mesh
import numpy as np

def write_stl(OCT_contour,name = 'OCT.stl'):
    """write_stl

    from list of contours write an stl

    Args:
        OCT_contour (List[CartContour]): list of cartesian contours
        name (str, optional): destination of save file . Defaults to 'OCT.stl' in local directory.
    """
    # OCT_contour = np.stack(OCT_contour,axis = -1)

    OCT_contour = OCT_contour.swapaxes(0,1)
    pointNum,dims,contourNum = OCT_contour.shape
    total_num_vertices = pointNum* contourNum
    vertices = np.zeros((total_num_vertices, 3))
    faces = np.zeros((2 * (total_num_vertices-pointNum), 3))
      # write vertices
    for contourID in range(contourNum):
        vertices[contourID*pointNum: (contourID+1)*pointNum,:] = OCT_contour[:,:,contourID] # change to OCt_contour[i] later

    # write faces ===>>> normals outwards, counter-clockwise 1-2-2, 2-3-3, 3-4-4, 4-1-1
    for contourID in range(contourNum-1):
        for pointID in range(pointNum):
            if pointID < pointNum - 1 :
                # 0-0'-1'
                faces[2*(pointID + contourID * pointNum), :] = [pointID + contourID * pointNum, pointID + (contourID+1) * pointNum, (pointID+1) + (contourID+1) * pointNum]
                # 0-1'-1
                faces[2*(pointID + contourID * pointNum) + 1, :] = [pointID + contourID * pointNum, (pointID+1) + (contourID+1) * pointNum, (pointID+1) + contourID * pointNum]

            else:
                # 3-3'-0'
                faces[2*(pointID + contourID * pointNum), :] = [pointID + contourID * pointNum, pointID + (contourID+1) * pointNum, (0) + (contourID+1) * pointNum]
                # 3-0'-0
                faces[2*(pointID + contourID * pointNum) + 1, :] = [pointID + contourID * pointNum, (0) + (contourID+1) * pointNum, (0) + contourID * pointNum]

    faces = faces.astype(np.int64)
    #print(faces)

    # Create the mesh
    OCT_rec = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            OCT_rec.vectors[i][j] = vertices[f[j],:]

    # Write the mesh to file "cube.stl"
    OCT_rec.save(name)