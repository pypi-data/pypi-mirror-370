#!/bin/python3

# Copyright 2024, A Baldwin, National Oceanography Centre
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

import re

# This function will automatically convert PascalCase/camelCase strings to lower_snake_case
# It will also substitute symbols for close approximations and swallow multiple and leading/trailing underscores
def to_snake_case(str_in):
    # Replacing some common symbols with textual equivalents
    str_out = str_in.replace("&", " and ")
    str_out = str_out.replace("%", "percent")
    str_out = str_out.replace("$", "S")
    str_out = str_out.replace("@", " at ")
    str_out = str_out.replace("+", " plus ")
    str_out = str_out.replace("#", " number ")
    str_out = str_out.replace("-", " minus ")
    str_out = str_out.replace("?", " question ")
    str_out = str_out.replace("*", " star ")
    str_out = str_out.replace("~", " tilde ")
    str_out = str_out.replace("=", " equals ")
    str_out = str_out.replace("/", " or ")
    str_out = str_out.replace("\\", " or ")
    str_out = re.sub("((?<![A-Z])(?=[A-Z]+))|((?=[A-Z][a-z]))", "_", str_out).lower() # Prepend all strings of uppercase with an underscore
    # This rule specifically will make the following transformations:
    # ADCFileFormat -> ADC_File_Format
    # RoiWidth -> Roi_Width
    # ROIWidth -> ROI_Width
    # MCConly -> MC_Conly
    # As this is just regex, we can't account for examples like the above that rely on human intuition for word boundaries rather than being strictly Pascal/Camel case
    str_out = re.sub("[^a-z0-9]", "_", str_out) # Replace all non-alphanumeric with underscore
    str_out = re.sub("_+", "_", str_out) # Clean up double underscores
    str_out = re.sub("(^_)|(_$)", "", str_out) # Clean up trailing or leading underscores
    return str_out
