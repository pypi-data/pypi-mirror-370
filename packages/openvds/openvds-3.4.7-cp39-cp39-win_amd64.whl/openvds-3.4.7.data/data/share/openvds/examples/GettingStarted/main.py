url = TEST_URL
connectionString = TEST_CONNECTION

import openvds
import numpy as np

try:
    with openvds.open(url, connectionString) as vds:
        manager = openvds.getAccessManager(vds)
        layout = manager.volumeDataLayout
        
        sampleDimension, crosslineDimension, inlineDimension = (0, 1, 2)
        inlineAxis = layout.getAxisDescriptor(inlineDimension)
        inlineNumber = (inlineAxis.coordinateMin + inlineAxis.coordinateMax) // 2
        inlineIndex = inlineAxis.coordinateToSampleIndex(inlineNumber)

        voxelMin = (0, 0, inlineIndex)
        voxelMax = (layout.getDimensionNumSamples(sampleDimension), layout.getDimensionNumSamples(crosslineDimension), inlineIndex + 1)

        buffer = np.empty((layout.getDimensionNumSamples(crosslineDimension), layout.getDimensionNumSamples(sampleDimension)))
        request = manager.requestVolumeSubset(data_out = buffer, dimensionsND = openvds.DimensionsND.Dimensions_012, min = voxelMin, max = voxelMax, lod = 0, channel = 0)
        success = request.waitForCompletion()

        request = manager.requestVolumeSubset(dimensionsND = openvds.DimensionsND.Dimensions_012, min = voxelMin, max = voxelMax, lod = 0, channel = 0)
        data = request.data.reshape(layout.getDimensionNumSamples(crosslineDimension), layout.getDimensionNumSamples(sampleDimension))

        # Plot the data
        import matplotlib.pyplot as plt
        plt.imshow(data.transpose(), cmap='seismic', vmin = layout.getChannelValueRangeMin(0), vmax = layout.getChannelValueRangeMax(0), interpolation='bilinear')
        plt.show(block=True)
except RuntimeError as error:
    print(f"Could not open VDS: {error}")