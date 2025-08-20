import argparse
import openvds
import numpy as np

parser = argparse.ArgumentParser(prog='corners', description='Print the corner points of a VDS file')
parser.add_argument('url')
parser.add_argument('-c', '--connection-string', default='')
args = parser.parse_args()

with openvds.open(args.url, args.connection_string) as vds:
    # Get the layout of the VDS
    layout = openvds.getLayout(vds)

    # Find inline and crossline axis descriptors
    axisDescriptors = [layout.getAxisDescriptor(dim) for dim in range(layout.dimensionality)]
    axisNames = [axisDescriptor.name for axisDescriptor in axisDescriptors]
    if not openvds.KnownAxisNames.inline() in axisNames or not openvds.KnownAxisNames.crossline() in axisNames:
        raise Exception("VDS does not have inline and crossline axes")
    inlineAxis = axisDescriptors[axisNames.index(openvds.KnownAxisNames.inline())]
    crosslineAxis = axisDescriptors[axisNames.index(openvds.KnownAxisNames.crossline())]

    # Find the inline and crossline index of the corners
    gridCorners = [(inlineAxis.coordinateMin, crosslineAxis.coordinateMin),
                   (inlineAxis.coordinateMin, crosslineAxis.coordinateMax),
                   (inlineAxis.coordinateMax, crosslineAxis.coordinateMax),
                   (inlineAxis.coordinateMax, crosslineAxis.coordinateMin)]
    
    # Calculate the corner points using the bin grid metadata
    origin = np.array(layout.getMetadata(openvds.KnownMetadata.surveyCoordinateSystemOrigin()))
    inlineSpacing = np.array(layout.getMetadata(openvds.KnownMetadata.surveyCoordinateSystemInlineSpacing()))
    crosslineSpacing = np.array(layout.getMetadata(openvds.KnownMetadata.surveyCoordinateSystemCrosslineSpacing()))
    cornerPoints = [origin + inlineSpacing * inline + crosslineSpacing * crossline for (inline, crossline) in gridCorners]

    # Print the corner points
    for (index, ((inline, crossline), cornerPoint)) in enumerate(zip(gridCorners, cornerPoints)):
        print(f"CORNER{index}:3D INLINE {round(inline):5}, 3D XLINE {round(crossline):5}, UTM-X {cornerPoint[0]:.1f}, UTM-Y {cornerPoint[1]:.1f}")
