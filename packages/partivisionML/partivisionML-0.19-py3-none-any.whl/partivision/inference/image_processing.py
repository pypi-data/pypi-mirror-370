from .data_handler import DataHandler
from .util import Util

import numpy as np
import cv2
import diplib as dip
import torch


class ProcessedImage:
    printed_device = False

    def __init__(self, frame, centerX, window_width, scaling_factor, um_per_pixel, model):

        self.frame = frame
        self.centerX = centerX
        self.window_width = window_width
        self.model = model
        self.scaling_factor = scaling_factor
        self.um_per_pixel = um_per_pixel

        self.data = {
            'area': 0,
            'perimeter': 0,
            'height': 0,
            'circularity': 0,
            'ypos': 0,
            'centerX': None,
            'taylor': 0,
        }

        self.contour = self.get_contour()
        self.process_contour(self.contour)

    def get_dip_measurement(self):
        binary_image = cv2.cvtColor(np.zeros_like(self.frame), cv2.COLOR_BGR2GRAY)
        cv2.drawContours(binary_image, [self.contour], -1, (1), thickness=cv2.FILLED)

        binary_image_dip = dip.Image(binary_image.astype(np.uint8))
        binary_image_dip.Convert('BIN')

        labeled_image = dip.Label(binary_image_dip)
        measurement = dip.MeasurementTool.Measure(
            labeled_image,
            features=['Perimeter', 'SolidArea', 'Roundness', 'Inertia']
        )
        return measurement

    def get_contour(self):
        new_window = Util.get_window(self.frame, self.centerX, self.window_width)
        if new_window is None:
            return None

        h, w, _ = new_window.shape
        new_h = (h // 32) * 32
        new_w = (w // 32) * 32
        if new_h == 0 or new_w == 0:
            resized_window = new_window
            x_scale = y_scale = 1.0
        else:
            resized_window = cv2.resize(new_window, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            x_scale = new_window.shape[1] / resized_window.shape[1]
            y_scale = new_window.shape[0] / resized_window.shape[0]

        # To tensor (N, C, H, W), float, [0,1], move to model's device
        input_tensor = torch.from_numpy(resized_window).permute(2, 0, 1).float().unsqueeze(0) / 255.0
        input_tensor = input_tensor.to(next(self.model.parameters()).device)

        if not ProcessedImage.printed_device:
            print(f"🚀 Inference running on {input_tensor.device}", flush=True)
            ProcessedImage.printed_device = True

        results = self.model(input_tensor, max_det=1, verbose=False)

        if not results or not results[0].masks:
            return None


        mask_pts = []
        for r in results:
            r.plot(boxes=False)
            for x, y in r.masks.xy[0]:
                x_rescaled = int(x * x_scale) + self.centerX - self.window_width
                y_rescaled = int(y * y_scale)
                mask_pts.append(x_rescaled)
                mask_pts.append(y_rescaled)

        ctr = np.array(mask_pts).reshape((-1, 1, 2)).astype(np.int32)
        self.contour = ctr
        return ctr

    def process_contour(self, contour):
        if contour is None:
            return

        M = cv2.moments(contour)
        m10, m00 = M["m10"], M["m00"]
        if m00 != 0:
            self.data['centerX'] = int(m10 // m00)

        _, y, _, h = cv2.boundingRect(contour)
        self.data['height'] = h * self.um_per_pixel / self.scaling_factor
        self.data['ypos'] = (y + (h // 2)) * self.um_per_pixel / self.scaling_factor

        measurement = self.get_dip_measurement()

        self.data['perimeter'] = measurement['Perimeter'][1][0] * self.um_per_pixel / self.scaling_factor
        self.data['area'] = measurement['SolidArea'][1][0] * pow(self.um_per_pixel, 2) / pow(self.scaling_factor, 2)
        self.data['circularity'] = measurement['Roundness'][1][0]

        major_axis = None
        minor_axis = None
        for obj in measurement['Inertia']:
            major_axis = obj[0]
            minor_axis = obj[1]
        if major_axis is not None and minor_axis is not None and (major_axis + minor_axis) != 0:
            taylor_param = (major_axis - minor_axis) / (major_axis + minor_axis)
            self.data['taylor'] = taylor_param

    def get_parameter(self, parameter):
        return self.data[parameter]
