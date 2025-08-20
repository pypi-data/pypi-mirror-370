#!/bin/python3

# Copyright 2025, A Baldwin, National Oceanography Centre
#
# This file is part of libflowcam.
#
# libflowcam is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libflowcam is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with libflowcam.  If not, see <http://www.gnu.org/licenses/>.

'''
sample.py

An interface for image data from the FlowCam sensor
'''

import argparse
import os
import re
import csv
import glob
import struct
import pytz
import hashlib
from datetime import datetime
import json
from PIL import Image, ImageDraw
import numpy as np
from .utils import to_snake_case


class ROI:
    def __init__(self, roi_reader, fp_dict, src_img, w, h, x, y, index, raw_props, udt, small_udt):
        self.__fp_dict = fp_dict
        self.__roi_reader = roi_reader
        self.__src_img = src_img
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.index = index
        self.raw_props = raw_props
        self.udt = udt
        self.small_udt = small_udt

    def __get_image(self):
        self.__roi_reader._aidx += 1
        if self.__src_img not in self.__fp_dict.keys():
            fp = open(self.__src_img, "rb")
            self.__fp_dict[self.__src_img] = {
                "fp": fp,
                "im": Image.open(fp),
                "aidx": self.__roi_reader._aidx
            }
        else:
            self.__fp_dict[self.__src_img]["aidx"] = self.__roi_reader._aidx
        while len(self.__fp_dict.keys()) > 16: # Start culling file pointers at 16
            del_keys = []
            for fp in self.__fp_dict.keys():
                if self.__fp_dict[fp]["aidx"] < (self.__roi_reader._aidx - 8):
                    self.__fp_dict[fp]["im"].close()
                    self.__fp_dict[fp]["fp"].close()
                    del_keys.append(fp)
            for key in del_keys:
                del self.__fp_dict[key]

        shape = [self.x, self.y, self.x + self.width, self.y + self.height]

        #This section is for quickly debugging issues with the decoder
        #img = self.__fp_dict[self.__src_img]["im"]
        #imd = ImageDraw.Draw(img)
        #imd.rectangle(shape, fill = None, outline = "red")
        #return img

        return self.__fp_dict[self.__src_img]["im"].crop(shape)

    image = property(
            fget = __get_image,
            doc = "Dynamically generated image object"
        )

class ROIReader:
    def flowcam_id_to_udt(self, serial_number, timestamp, roi_index = None):
        udt = "udt__usa_fluid_imaging_laboratories__flow_cam__" + str(serial_number) + "__" + str(int(timestamp))
        if roi_index is not None:
            udt = udt + "__" + str(roi_index)
        return udt

    def convert_to_small_udt(self, big_udt):
        if big_udt.startswith("udt__"):
            udt_cmps = big_udt[5:].split("__")
            vendor = udt_cmps[0]
            device = udt_cmps[1]
            vdp = hashlib.sha256((vendor + "__" + device).encode("utf-8")).hexdigest()[0:12]
            device_id = udt_cmps[2].lower()
            did = hashlib.sha256((device_id).encode("utf-8")).hexdigest()[0:16]
            timestamp = int(udt_cmps[3])
            ts = '{:012x}'.format(timestamp)
            small_udt = "udt_" + vdp + "_" + did + "_" + ts
            if len(udt_cmps) > 4:
                imid = udt_cmps[4]
                small_udt = small_udt + "_" + hashlib.sha256((imid).encode("utf-8")).hexdigest()[0:16]
            return small_udt
        else:
            return big_udt

    def __to_snake_case_flowcam_preprocess(self, str_in):
        # We might want to do something special in future if a new revision messes up column names
        return to_snake_case(str_in)

    def roi_from_udt(self, udt):
        small_udt = self.convert_to_small_udt(udt) # Automatically shrink for quicker searching
        try:
            return self.udt_lookup[small_udt]
        except KeyError:
            return None

    def __init__(self, csv_fp, verbose = False, permissive = False, calibration_offset_frames = None):
        self.__close_csv = False
        self._aidx = 0
        if type(csv_fp) == str:
            csv_fp = open(csv_fp, "r", encoding="iso-8859-1")
            self.__close_csv = True
        sample_path = csv_fp.name
        sample_dir = sample_path[:-len(os.path.basename(sample_path))]
        sample_summary_file = sample_path[:-4] + "_summary.csv"
        self.summary_file = sample_summary_file
        self.permissive = permissive

        if verbose:
            print("Sample directory = " + sample_dir)

        self.csv_data = []
        reader = csv.DictReader(csv_fp, skipinitialspace=True)
        for row in reader:
            csv_data_row = {}
            for key in row:
                csv_data_row[self.__to_snake_case_flowcam_preprocess(key)] = row[key]
            self.csv_data.append(csv_data_row)
        if self.__close_csv:
            csv_fp.close()


        self.frame_rate = 7.0 # Default value
        self.serial_number = None

        with open(sample_summary_file, "r", encoding="iso-8859-1") as sf_fp:
            for line in sf_fp:
                linelow = line.lower()
                if "frame rate," in linelow:
                    fridx = linelow.index("frame rate,")
                    self.frame_rate = float(re.sub("[^\\d\\.]", "", line[fridx + 11:]))
                elif "serialno," in linelow:
                    matchidx = linelow.index("serialno,")
                    self.serial_number = int(re.sub("[^\\d\\.]", "", line[matchidx + 9:]))
                elif "magnification," in linelow:
                    matchidx = linelow.index("magnification,")
                    self.magnification = int(re.sub("[^\\d\\.]", "", line[matchidx + 14:]))
                elif "efficiency," in linelow:
                    matchidx = linelow.index("efficiency,")
                    self.efficiency = float(re.sub("[^\\d\\.]", "", line[matchidx + 11:])) / 100.0 # We report as a 0-1 value in the library
                elif "sample volume aspirated," in linelow:
                    matchidx = linelow.index("sample volume aspirated,")
                    self.volume_aspirated = float(re.sub("[^\\d\\.]", "", line[matchidx + 24:])) # ml
                elif "sample volume processed," in linelow:
                    matchidx = linelow.index("sample volume processed,")
                    self.volume_processed = float(re.sub("[^\\d\\.]", "", line[matchidx + 24:])) # ml
                elif "fluid volume imaged," in linelow:
                    matchidx = linelow.index("fluid volume imaged,")
                    self.volume_imaged = float(re.sub("[^\\d\\.]", "", line[matchidx + 20:])) # ml
                elif "start time," in linelow:
                    matchidx = linelow.index("start time,")
                    match = re.search("[\\d]+-[\\d]+-[\\d]+\\ [\\d]+:[\\d]+:[\\d]+", line[matchidx + 11:])
                    matchval = match.group(0)
                    self.start_time = datetime.strptime(matchval, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
                elif "end time," in linelow:
                    matchidx = linelow.index("end time,")
                    match = re.search("[\\d]+-[\\d]+-[\\d]+\\ [\\d]+:[\\d]+:[\\d]+", line[matchidx + 9:])
                    matchval = match.group(0)
                    self.end_time = datetime.strptime(matchval, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)


        if verbose:
            print("Average frame rate = " + str(self.frame_rate) + "fps")
            print("Serial number = " + str(self.serial_number))
            print("Magnification = " + str(self.magnification))
            print("Volume aspirated = " + str(self.volume_aspirated) + "mL")
            print("Volume processed = " + str(self.volume_processed) + "mL")
            print("Volume imaged = " + str(self.volume_imaged) + "mL")
            print("Efficiency = " + str(self.efficiency * 100) + "%")
            print("Start time = " + self.start_time.strftime("%a, %-d %b %Y %H:%M:%S %Z"))
            print("End time = " + self.end_time.strftime("%a, %-d %b %Y %H:%M:%S %Z"))


        # ['name', 'area_abd_m', 'area_filled_m', 'aspect_ratio', 'average_blue', 'average_green', 'average_red', 'biovolume_cylinder_m', 'biovolume_p_spheroid_m', 'biovolume_sphere_m', 'calibration_factor', 'calibration_image', 'capture_id', 'capture_x_px', 'capture_y_px', 'ch1_area', 'ch1_peak', 'ch1_width', 'ch2_area', 'ch2_peak', 'ch2_width', 'ch2_or_ch1_ratio', 'circle_fit', 'circularity', 'circularity_hu', 'compactness', 'convex_perimeter_m', 'convexity', 'date', 'diameter_abd_m', 'diameter_esd_m', 'diameter_fd_m', 'edge_gradient', 'elapsed_time_s', 'elongation', 'feret_angle_max', 'feret_angle_min', 'fiber_curl', 'fiber_straightness', 'filter_score', 'geodesic_aspect_ratio', 'geodesic_length_m', 'geodesic_thickness_m', 'group_id', 'image_height_px', 'image_width_px', 'intensity', 'length_m', 'particles_per_chain', 'perimeter_m', 'ratio_blue_or_green', 'ratio_red_or_blue', 'ratio_red_or_green', 'roughness', 'sigma_intensity', 'source_image', 'sphere_complement_m', 'sphere_count', 'sphere_unknown_m', 'sphere_volume_m', 'sqrt_circularity', 'sum_intensity', 'symmetry', 'time', 'timestamp', 'transparency', 'uuid', 'volume_abd_m', 'volume_esd_m', 'width_m']

        si_offset = int(self.csv_data[0]["source_image"])
        last_etime = float(self.csv_data[0]["elapsed_time_s"])
        calibration_frames = 1
        if calibration_offset_frames == None:
            calibration_offset_frames = round(last_etime * self.frame_rate) # Try autodetect, this is usually around 33
        cframe = calibration_offset_frames
        cal_images = glob.glob(sample_dir + "cal_image_*.tif")
        raw_images = glob.glob(sample_dir + "rawfile_*.tif")

        if verbose:
            print("Time to first capture = " + str(int(last_etime * 1000)) + "ms")
            print("Calibration offset frame loss = ~" + str(calibration_offset_frames) + " frames per calibration")

        # This is a HORRIBLE bodge, but neccesary because we're missing an accurate source_image column
        idx = 0
        for csv_row in self.csv_data:
            c_etime = float(csv_row["elapsed_time_s"])
            if c_etime > (last_etime + 0.001):
                offset_frames = round((c_etime - last_etime) * self.frame_rate)
                if offset_frames > (calibration_offset_frames - 2): # Whenever we have a large skip, it's usually a calibration event - and this means an extra skipped frame!
                    if verbose:
                        print("Skipped " + str(int((c_etime - last_etime) * 1000)) + "ms (~" + str(offset_frames) + " frames) at ROI " + str(idx) + ", assuming recalibration")
                    calibration_frames += 1
                    #if offset_frames > calibration_offset_frames:
                        #offset_frames = calibration_offset_frames
                else:
                    if offset_frames > 1:
                        if verbose:
                            print("Skipped " + str(int((c_etime - last_etime) * 1000)) + "ms (~" + str(offset_frames) + " frames) at ROI " + str(idx))
                cframe = cframe + offset_frames
                last_etime = c_etime
            csv_row["rawfile_index"] = cframe - calibration_frames
            idx += 1

        max_frame_id = cframe - calibration_frames

        if verbose:
            print("Detected " + str(calibration_frames) + " calibration events and " + str(len(cal_images)) + " calibration images")
        if calibration_frames == len(cal_images):
            if verbose:
                print("As calibration event count matches image count we likely have good synchronisation, continuing")
        else:
            raise IndexError("Could not establish stable frame timings! - This is likely an issue with your data. Consider sending a copy to the developer of libflowcam and raising an issue on GitHub.")

        if verbose:
            print("Detected " + str(max_frame_id) + " frame events and " + str(len(raw_images)) + " frame images")
        if max_frame_id <= len(raw_images):
            if verbose:
                print("As frame event count is less than image count we likely have good synchronisation, continuing")
        else:
            if permissive:
                if verbose:
                    print("Not enough raw files to match frame events - poor synchronisation, but continuing anyway as instructed!")
            else:
                raise IndexError("Could not find enough rawfiles! - This is likely an issue with your data. Consider sending a copy to the developer of libflowcam and raising an issue on GitHub.")

        start_time_ts = self.start_time.timestamp()
        self.udt = self.flowcam_id_to_udt(self.serial_number, start_time_ts)
        self.small_udt = self.convert_to_small_udt(self.udt)

        if verbose:
            print("Sample UDT = " + self.udt)
            print("Compact UDT = " + self.small_udt)

        self.__fp_dict = {}

        self.rois = []
        self.udt_lookup = {}
        roi_index = 1
        for csv_row in self.csv_data:
            if int(csv_row["image_width_px"].split(".")[0]) != 0:
                source_image_index = csv_row["rawfile_index"]
                source_image = sample_dir + "rawfile_" + str(source_image_index).zfill(6) + ".tif"
                udt = self.flowcam_id_to_udt(self.serial_number, start_time_ts, roi_index)
                small_udt = self.convert_to_small_udt(udt)
                roi_def = ROI(self, self.__fp_dict, source_image, int(csv_row["image_width_px"].split(".")[0]), int(csv_row["image_height_px"].split(".")[0]), int(csv_row["capture_x_px"].split(".")[0]), int(csv_row["capture_y_px"].split(".")[0]), roi_index, csv_row, udt, small_udt)
                self.rois.append(roi_def)
                self.udt_lookup[small_udt] = roi_def
            roi_index += 1
