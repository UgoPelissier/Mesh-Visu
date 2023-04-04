import vtk

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def ReadPolyData(file_name):
    from pathlib import Path

    from vtkmodules.vtkIOGeometry import (
        vtkBYUReader,
        vtkOBJReader,
        vtkSTLReader
    )
    from vtkmodules.vtkIOLegacy import vtkPolyDataReader
    from vtkmodules.vtkIOPLY import vtkPLYReader
    from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
    
    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None
    else:
        if ext == ".ply":
            reader = vtkPLYReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtp":
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".obj":
            reader = vtkOBJReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".stl":
            reader = vtkSTLReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtk":
            reader = vtkPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".g":
            reader = vtkBYUReader()
            reader.SetGeometryFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()

        return poly_data


def get_program_parameters():
    import argparse
    description = 'vtkUnstructuredGrid.'
    epilogue = '''
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='boolean.vtk')
    args = parser.parse_args()
    return args.filename

class IPWCallback:
    def __init__(self, plane):
        self.plane = plane

    def __call__(self, caller, ev):
        rep = caller.GetRepresentation()
        rep.GetPlane(self.plane)


def main():
    colors = vtkNamedColors()
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    filename = get_program_parameters()
    
    # Create the reader for the data.
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(filename)
    
    print('There are %s input points' % reader.GetOutput().GetNumberOfPoints())
    print('There are %s input cells' % reader.GetOutput().GetNumberOfCells())

    #++++++++++++++++++++++++++++++++++++++++++++++++
    # Create a rendering window and renderer
    ren = vtkRenderer()
    ren.SetBackground(colors.GetColor3d('Grey'))
    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetWindowName('Mesh')
    renWin.SetSize(640, 480)

    # Create a renderwindowinteractor
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    # Get the edges from the mesh
    edges = vtk.vtkExtractEdges()
    edges.SetInputConnection(reader.GetOutputPort())
    
    edge_mapper = vtk.vtkPolyDataMapper()
    edge_mapper.SetInputConnection(edges.GetOutputPort())
       
    edge_actor = vtk.vtkActor()
    edge_actor.SetMapper(edge_mapper)
    
    edge_actor.GetProperty().SetColor(0.25,0.25,0.25)
    edge_actor.GetProperty().SetOpacity(0.5)
    
    # ren.AddActor(edge_actor)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++ 
    # Extract the outer (polygonal) surface.
    surface = vtkDataSetSurfaceFilter()
    surface.SetInputConnection(reader.GetOutputPort())
    
    aBeamMapper = vtkDataSetMapper()
    aBeamMapper.SetInputConnection(surface.GetOutputPort())
    aBeamActor = vtkActor()
    aBeamActor.SetMapper(aBeamMapper)
    aBeamActor.AddPosition(0, 0, 0)
    aBeamActor.GetProperty().SetColor(
        colors.GetColor3d('Yellow'))
    aBeamActor.GetProperty().SetOpacity(0.60)
    aBeamActor.GetProperty().EdgeVisibilityOn()
    aBeamActor.GetProperty().SetEdgeColor(
        colors.GetColor3d('Grey'))
    aBeamActor.GetProperty().SetLineWidth(1.5)
    
    ren.AddActor(aBeamActor)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    # Create a plane to cut
    plane = vtk.vtkPlane()
    plane.SetOrigin(0.5, 0, 0)
    plane.SetNormal(1, 0, 0)

    # Create cutter
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputData(reader.GetOutput())
    cutter.Update()
    cutterMapper = vtk.vtkPolyDataMapper()
    cutterMapper.SetInputConnection(cutter.GetOutputPort())

    # Create plane actor
    planeActor = vtkActor()
    planeActor.GetProperty().SetOpacity(0.60)
    planeActor.GetProperty().EdgeVisibilityOn()
    planeActor.GetProperty().SetEdgeColor(
        colors.GetColor3d('Black'))
    planeActor.SetMapper(cutterMapper)
    
    # ren.AddActor(planeActor)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    # Plane widget
    plane_widget = vtk.vtkPlane()
    
    cutter_widget = vtk.vtkCutter()
    cutter_widget.SetCutFunction(plane_widget)
    cutter_widget.SetInputData(reader.GetOutput())
    
    mapper_widget = vtk.vtkPolyDataMapper()
    mapper_widget.SetInputConnection(cutter_widget.GetOutputPort())
    actor_widget = vtkActor()
    actor_widget.SetMapper(mapper_widget)
    
    # The callback will do the work.
    my_callback = IPWCallback(plane_widget)
    
    rep = vtk.vtkImplicitPlaneRepresentation()
    rep.SetPlaceFactor(1.)  # This must be set prior to placing the widget
    rep.PlaceWidget(actor_widget.GetBounds())
    rep.SetNormal(plane_widget.GetNormal())
    
    plane_widget = vtk.vtkImplicitPlaneWidget2()
    plane_widget.SetInteractor(iren)
    plane_widget.SetRepresentation(rep)
    plane_widget.AddObserver(vtk.vtkCommand.InteractionEvent, my_callback)
    
    #++++++++++++++++++++++++++++++++++++++++++++++++
    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    plane_widget.On()
    iren.Start()

if __name__ == '__main__':
    main()