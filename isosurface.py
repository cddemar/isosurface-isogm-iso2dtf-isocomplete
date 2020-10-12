# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 09:58:01 2020

@author: Jhon Corro
@author: Cristhyan De Marchena
"""
import vtk

# Script params
val = 0

# Countour filter
iso = vtk.vtkContourFilter()

# Min and max value from data
max = 0
min = 0

# planes
xplane = vtk.vtkPlane()
yplane = vtk.vtkPlane()
zplane = vtk.vtkPlane()


# SLIDE BAR COLORS
red_r = 224/255
red_g = 69/255
red_b = 85/255
green_r = 70/255
green_g = 224/255
green_b = 105/255
white = 242/255

def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', nargs='?', default=None, help='data file')
    parser.add_argument('--val', dest='value', type=int, default=None, help='initial isovalue')
    parser.add_argument('--clip', dest='clip', nargs=3, type=int, default=None)
    args = parser.parse_args()
    
    return args.data_file, args.value, args.clip

def read_file(file_name):
    import os
    if(file_name):
        path, extension = os.path.splitext(file_name)
        extension = extension.lower()
        if extension == ".vti":
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            # Read min and max
            global min
            global max
            _min, _max = reader.GetOutput().GetScalarRange()
            min = _min 
            max = _max
        else:
            # the file provided doesn't match the accepted extenstions
            reader = None
    else:
        reader = None
    return reader

def generate_plane_origins(clip):
    # origins of the planes
    origins = vtk.vtkPoints()
    origins.SetNumberOfPoints(3)
    if(clip):
        if(clip[0]):
            origins.InsertPoint(0, [clip[0], 0, 0]) # x
        else:
            origins.InsertPoint(0, [0, 0, 0]) # x
            
        if(clip[1]):
            origins.InsertPoint(1, [0, clip[1], 0]) # y
        else:
            origins.InsertPoint(1, [0, 0, 0]) # y
            
        if(clip[2]):
            origins.InsertPoint(2, [0, 0, clip[1]]) # z
        else:
            origins.InsertPoint(2, [0, 0, 0]) # z
    return origins

def generate_plane_normals():
    normals = vtk.vtkDoubleArray()
    normals.SetNumberOfComponents(3)
    normals.SetNumberOfTuples(3)
    
    normals.SetTuple(0, [1, 0, 0])
    normals.SetTuple(1, [0, 1, 0])
    normals.SetTuple(2, [0, 0, 1])
    return normals
    
def generate_actors(data, val, clip):    
    # contour
    global iso
    iso.SetInputConnection(data.GetOutputPort())
    if(val):
        iso.SetValue(0, val)    
    else:
        iso.SetValue(0, max/4)
    
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(min, 31/255, 162/255, 255/255)
    ctf.AddRGBPoint(max, 255/255, 251/255, 19/255)

    # generate vtkPlanes stuff.
    origins = generate_plane_origins(clip)
    normals = generate_plane_normals()

    # the list of planes
    planes = vtk.vtkPlanes()
    planes.SetPoints(origins)
    planes.SetNormals(normals)
    planes.GetPlane(0, xplane)
    planes.GetPlane(1, yplane)
    planes.GetPlane(2, zplane)
    
    xclipper = vtk.vtkClipPolyData()
    xclipper.SetInputConnection(iso.GetOutputPort())
    xclipper.SetClipFunction(xplane)
    
    yclipper = vtk.vtkClipPolyData()
    yclipper.SetInputConnection(xclipper.GetOutputPort())
    yclipper.SetClipFunction(yplane)
    
    zclipper = vtk.vtkClipPolyData()
    zclipper.SetInputConnection(yclipper.GetOutputPort())
    zclipper.SetClipFunction(zplane)
    
    
    clipMapper = vtk.vtkDataSetMapper()
    clipMapper.SetLookupTable(ctf)
    clipMapper.SetInputConnection(zclipper.GetOutputPort())
    clipMapper.SetScalarRange(0, 255)

    
    # Generate iso surface actor from iso surface mapper.
    isoActor = vtk.vtkActor()
    isoActor.SetMapper(clipMapper)
    
    return [isoActor]

def set_slide_bar_colors(bar):
    bar.GetSliderProperty().SetColor(red_r, red_g, red_b)
    bar.GetTitleProperty().SetColor(white, white, white)
    bar.GetLabelProperty().SetColor(red_r, red_g, red_b)
    bar.GetSelectedProperty().SetColor(green_r, green_g, green_b)
    bar.GetTubeProperty().SetColor(white, white, white)
    bar.GetCapProperty().SetColor(red_r, red_g, red_b)
    return bar

def generate_iso_slide_bar(value):
    # Create Slidebar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    # Set range and title.
    slide_bar.SetMinimumValue(min)
    slide_bar.SetMaximumValue(max)
    if(value):
        slide_bar.SetValue(value)
    else:
        slide_bar.SetValue(max/4)
    slide_bar.SetTitleText("Iso value")
    
    
    # Set colors.
    slide_bar = set_slide_bar_colors(slide_bar)
    
    # Set coordinates.
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(0.78, 0.1)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(0.98 , 0.1)
    return slide_bar

def custom_iso_callback(obj, event):
    value = int (obj.GetRepresentation().GetValue())
    global iso
    iso.SetValue(0, value)
    iso.Update()

def generate_x_axis_slide_bar(max, value):
    # Create Slidebar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    # Set range and title.
    slide_bar.SetMinimumValue(0)
    slide_bar.SetMaximumValue(max)
    if(value):
        slide_bar.SetValue(value)
    else:
        slide_bar.SetValue(0)
        
    slide_bar.SetTitleText("X clip")
    
    
    # Set colors.
    slide_bar = set_slide_bar_colors(slide_bar)
    
    # Set coordinates.
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(0.02, 0.5)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(0.22 , 0.5)
    return slide_bar

def x_axis_custom_callback(obj, event):
    value = int (obj.GetRepresentation().GetValue())
    global xplane
    xplane.SetOrigin(value, 0, 0)

def generate_y_axis_slide_bar(max, value):
    # Create Slidebar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    # Set range and title.
    slide_bar.SetMinimumValue(0)
    slide_bar.SetMaximumValue(max)
    if(value):
        slide_bar.SetValue(value)
    else:
        slide_bar.SetValue(0)
    slide_bar.SetTitleText("Y clip")
    
    
    # Set colors.
    slide_bar = set_slide_bar_colors(slide_bar)
    
    # Set coordinates.
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(0.02, 0.3)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(0.22 , 0.3)
    return slide_bar

def y_axis_custom_callback(obj, event):
    value = int (obj.GetRepresentation().GetValue())
    global yplane
    yplane.SetOrigin(0, value, 0)

def generate_z_axis_slide_bar(max, value):
    # Create Slidebar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    # Set range and title.
    slide_bar.SetMinimumValue(0)
    slide_bar.SetMaximumValue(max)
    if(value):
        slide_bar.SetValue(value)
    else:
        slide_bar.SetValue(0)
    slide_bar.SetTitleText("Z clip")
    
    # Set colors.
    slide_bar = set_slide_bar_colors(slide_bar)
    
    # Set coordinates.
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(0.02, 0.1)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(0.22 , 0.1)
    return slide_bar

def z_axis_custom_callback(obj, event):
    value = int (obj.GetRepresentation().GetValue())
    global zplane
    zplane.SetOrigin(0, 0, value)

def generate_gui(actors, val, clip):
    actorBounds = actors[0].GetBounds()
    maxX = int(actorBounds[1] + 1)
    maxY = int(actorBounds[3] + 1)
    maxZ = int(actorBounds[5] + 1)
    
    # Create renderer stuff
    renderer = vtk.vtkRenderer()
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer)
    renderer_window_interactor = vtk.vtkRenderWindowInteractor()
    renderer_window_interactor.SetRenderWindow(renderer_window)
    
    # Add iso slide bar   
    iso_slide_bar = generate_iso_slide_bar(val)
    iso_slider_widget = vtk.vtkSliderWidget()
    iso_slider_widget.SetInteractor(renderer_window_interactor)
    iso_slider_widget.SetRepresentation(iso_slide_bar)
    iso_slider_widget.AddObserver("InteractionEvent", custom_iso_callback)
    iso_slider_widget.EnabledOn()
    
    # Add x-axis slide bar   
    x_axis_slide_bar = generate_x_axis_slide_bar(maxX, clip[0]) if clip else generate_x_axis_slide_bar(maxX, 0)
    x_axis_slider_widget = vtk.vtkSliderWidget()
    x_axis_slider_widget.SetInteractor(renderer_window_interactor)
    x_axis_slider_widget.SetRepresentation(x_axis_slide_bar)
    x_axis_slider_widget.AddObserver("InteractionEvent", x_axis_custom_callback)
    x_axis_slider_widget.EnabledOn()
    
    
    # Add y-axis slide bar   
    y_axis_slide_bar = generate_y_axis_slide_bar(maxY, clip[1]) if clip else generate_y_axis_slide_bar(maxY, 0)
    y_axis_slider_widget = vtk.vtkSliderWidget()
    y_axis_slider_widget.SetInteractor(renderer_window_interactor)
    y_axis_slider_widget.SetRepresentation(y_axis_slide_bar)
    y_axis_slider_widget.AddObserver("InteractionEvent", y_axis_custom_callback)
    y_axis_slider_widget.EnabledOn()
    
    
    # Add z-axis slide bar   
    z_axis_slide_bar = generate_z_axis_slide_bar(maxZ, clip[2]) if clip else generate_z_axis_slide_bar(maxZ, 0)
    z_axis_slider_widget = vtk.vtkSliderWidget()
    z_axis_slider_widget.SetInteractor(renderer_window_interactor)
    z_axis_slider_widget.SetRepresentation(z_axis_slide_bar)
    z_axis_slider_widget.AddObserver("InteractionEvent", z_axis_custom_callback)
    z_axis_slider_widget.EnabledOn()
    
    
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(min, 31/255, 162/255, 255/255)
    ctf.AddRGBPoint(max, 255/255, 251/255, 19/255)
    
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetOrientationToHorizontal()
    scalar_bar.SetTextPositionToPrecedeScalarBar()
    scalar_bar.UnconstrainedFontSizeOff()
    # Pops CTF from the actors' list
    scalar_bar.SetLookupTable(ctf)
    scalar_bar.SetNumberOfLabels(3)
    scalar_bar.SetLabelFormat("%-6.0f")
    
    scalar_bar.SetPosition(0.24, 0.02)
    scalar_bar.SetHeight(0.1)
    scalar_bar.SetWidth(0.5)
    
    # Add the actors and camera to the renderer, set background and size
    for index, actor in enumerate(actors):
        renderer.AddActor(actor)
        
    renderer.AddActor2D(scalar_bar)
    renderer.ResetCamera()
    renderer.GetActiveCamera().Roll(200)
    renderer.GetActiveCamera().Elevation(90)
    renderer.GetActiveCamera().Azimuth(0)
    renderer.SetBackground(0.1, 0.1, 0.1)
    renderer.ResetCameraClippingRange()
    renderer_window.SetSize(renderer_window.GetScreenSize());
    cam1 = renderer.GetActiveCamera()
    cam1.Zoom(0.8)
    
    # Smoother camera controls
    renderer_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera();
    renderer_window_interactor.Initialize()
    renderer_window.Render()
    renderer_window.SetWindowName('Isosurface')
    renderer_window.Render()
    renderer_window_interactor.Start()
    

def main():
    # Get file paths from cli params.
    #data_file, texture_file = get_program_parameters()
    data_file, val, clip = get_program_parameters()
    
    print(val)
    print(clip)
    
    # Read data file.
    data = read_file(data_file)
    if(data):
        actors = generate_actors(data, val, clip)
        # Generate GUI
        generate_gui(actors, val, clip)        
    else:
        print('The data file was not found or the file provided does not match neither the .vti and .vtp extension.')
    

if __name__ == '__main__':
    main()