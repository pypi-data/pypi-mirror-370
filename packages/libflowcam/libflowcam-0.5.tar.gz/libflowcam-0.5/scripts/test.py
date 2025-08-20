from libflowcam import ROIReader

# Sometimes autodecting the offset frames doesn't work automatically, so you can set it manually, start from 33, as this is usually roughly right!
#sample = ROIReader("testdata/flowcam_polina_pontoon_1407_r2/flowcam_polina_pontoon_1407_r2.csv", verbose=True, calibration_offset_frames=33)
#print(str(len(sample.rois)) + " ROIs") # Should be 3618 ROIs

#sorted_rois = sorted(sample.rois, key=lambda x: x.width * x.height, reverse = True)

#for roi in sorted_rois[:32]: # Gives back the 30 biggest plankton
#    roi.image.save("testout/flowcam_polina_pontoon_1407_r2_" + str(roi.index) + ".png")


# A Sample, with some bigger copepods

sample = ROIReader("testdata/flowcam_polina_pontoon_1807_r1/flowcam_polina_pontoon_1807_r1.csv", verbose=True)
print(str(len(sample.rois)) + " ROIs") # Should be 137015 ROIs

sorted_rois = sorted(sample.rois, key=lambda x: x.width * x.height, reverse = True)

for roi in sorted_rois[:32]: # Gives back the 30 biggest plankton
    roi.image.save("testout/flowcam_polina_pontoon_1807_r1_" + str(roi.index) + ".png")

print(sample.roi_from_udt("udt_c691abd6787d_5208ac35cc63a8d7_00006880f0ee_0f4121d0ef1df4c8").index) # Should match 216



