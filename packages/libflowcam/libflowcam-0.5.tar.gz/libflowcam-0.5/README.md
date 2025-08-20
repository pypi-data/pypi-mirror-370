# libflowcam
An optimised, native Python library for working with FlowCam data. Implements lazy-loading wherever possible and maintains open file pointers for speedy access. Returns standard Pillow image objects for further processing.

## Example
```python
from libflowcam import ROIReader

# Represents a typical sample density
sample1 = ROIReader("testdata/flowcam_polina_pontoon_0907_r2/flowcam_polina_pontoon_0907_r2.csv")
print(str(len(sample1.rois)) + " ROIs") # Should be 6268 ROIs
for roi_index in [10, 100, 1000]:
    sample1.rois[roi_index].image.save("testout/flowcam_polina_pontoon_0907_r2_" + str(roi_index) + ".png")

# A very dense sample, this is a cruel test
sample2 = ROIReader("testdata/flowcam_polina_pontoon_0707_r1/flowcam_polina_pontoon_0707_r1.csv")
print(str(len(sample2.rois)) + " ROIs") # Should be 137015 ROIs
for roi_index in [10, 100, 1000, 10000, 100000]:
    sample2.rois[roi_index].image.save("testout/flowcam_polina_pontoon_0707_r1_" + str(roi_index) + ".png")
```

## Note
This library has been built with no internal knowledge of the FlowCam software, and the data output format was reverse engineered soley from output data. It would therefore be highly appreciated if users could contribute data that breaks the library in order to better accomodate for all use cases.
