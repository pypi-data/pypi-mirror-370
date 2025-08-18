"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""


import argparse
import json
import logging
import serial.tools.list_ports # type: ignore
from os.path import join, abspath
import os
import time
from wiliot_api import ManufacturingClient
from wiliot_core import WiliotGateway, GetApiKey
from wiliot_testers.tester_utils import CsvLog, HeaderType, TesterName
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.wiliot_tester_log import WiliotTesterLog, dict_to_csv
from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest
from wiliot_tools.test_equipment.test_equipment import Attenuator, BarcodeScanner, YoctoSensor
from matplotlib import pyplot as plt
import numpy as np

QR_SCANNER_TIMEOUT = 1000  # in msec to scan the external ID


class SampleChamber:

    def __init__(self, mode="offline",
                 external_id=None,
                 test=None,
                 env=None,
                 owner_id=None,
                 surface='no simulation',
                 output_path=None,
                 name=''):
        """
                Initialize the SampleChamber object.

                Parameters: - mode (str): The mode of operation, either "online" or "offline". - external_id (str):
                The external ID of the tag. - test (str): The name of the test to perform according to the tests in
                .default_test_configs.json. - env (str): The environment for cloud connection, either "prod" or
                "test". - surface (str): The surface to simulate, default is 'no simulation' - data according to the
                .default_surfaces.json. - output_path (str): The path where output files will be stored,
                if not mentioned - it will be saved in <USER>/AppData/Local/wiliot/sample/logs directory.

                Initializes various instance variables and starts the test.
                """
        mode = mode.lower() if mode else mode
        env = env.lower() if env else env
        owner_id = owner_id.lower() if owner_id else owner_id
        self.validate_args(mode, env, owner_id)
        self.run_data_path = None
        self.packets_data_path = None
        self.name = None
        self.output = output_path
        self.test_data = None
        self.runDataDict = None
        self.gw_version = None
        self.sensor = None
        self.online = True if mode.lower() == 'online' else False
        self.client = None
        self.owner_id = owner_id
        self.external_id = external_id if external_id is not None else ''
        self.common_run_name = name + time.strftime("_%d%m%y_%H%M%S")
        self.surface = surface
        self.pywiliot_version = get_version()
        self.selected_test_suite = {}
        self.barcode = None
        self.surface_freq_shift = None
        self.test_suite = {}
        self.default_dict = None
        self.test = test
        self.packets_csv = None
        upload = False

        self.logger = self.test_configs()  # Read all default values from JSONs
        self.gateway_obj = self.com_connect(self.default_dict)  # Connect to all HW
        # Init Wiliot Tester SDK
        self.wiliot_tag_test = WiliotTesterTagTest(test_suite=self.selected_test_suite,
                                                   selected_test=self.test,
                                                   logger_name=self.logger.logger.name,
                                                   logger_result_name=self.logger.results_logger.name,
                                                   logger_gw_name=self.logger.gw_logger.name,
                                                   gw_obj=self.gateway_obj)
        if self.online:
            self.connect_to_cloud()

        if self.test in ['BLE_CALIBRATION', 'BEACON_CALIBRATION', 'LORA_CALIBRATION']:
            atten_type = self.test.split('_')[0]
            self.perform_calibration_test(atten_type)

        else:
            result = self.start_test()
            if result:
                self.logger.logger.info(f'Test done, \nData stored at {self.logger.log_path}')

                if result and self.online:
                    upload = self.cloud_upload(env=env)

                if not upload:
                    if self.online:
                        self.logger.logger.warning('Failed to upload data to the cloud, please upload it manually')
                    else:
                        self.logger.logger.warning('Please upload data manually to cloud to complete post process')

        self.gateway_obj.exit_gw_api()

    @staticmethod
    def validate_args(mode, env, owner_id):
        """
                Validate the arguments passed to the constructor.

                Parameters:
                - mode (str): The mode of operation, either "online" or "offline".
                - env (str): The environment for cloud connection.
                - external_id (str): The external ID of the tag.

                Raises ValueError if the arguments are not valid.
                """
        if mode == "online" and ((not env) or (not owner_id)):
            raise ValueError("In 'online' mode - env and owner_id is mandatory")

    def test_configs(self):
        """
        Configure the test environment.

        Reads configurations from JSON files and validates them.
        Also sets up logging and test suites according to the test provided.
        """

        def convert_test_suite():
            """
            Converting the test from .default_test_configs.json to test suite that
            will fit to Wiliot Tester SDK pattern
            """
            return {
                self.test: {
                    "plDelay": 0,
                    "rssiThresholdHW": int(self.default_dict.get('rssiThresholdHW', 0)),
                    "rssiThresholdSW": int(self.default_dict.get('rssiThresholdSW', 9999)),
                    "tests": [{
                        "name": 'Sample_Test',
                        "rxChannel": self.test_suite[self.test].get('channel'),
                        "energizingPattern": self.test_suite[self.test].get('pattern'),
                        "timeProfile": [int(self.test_suite[self.test].get('tOn')),
                                        int(self.test_suite[self.test].get('tTotal'))],
                        "absGwTxPowerIndex": -1,
                        "maxTime": self.test_suite[self.test].get('testTime'),
                        "delayBeforeNextTest": int(self.test_suite[self.test].get('sleep')),
                        "stop_criteria": {'tbp_mean': [0, 9999]},
                        "quality_param": {}
                    }]
                }
            }

        def convert_calibration_suite():
            return {
                self.test: {
                    "plDelay": 0,
                    "rssiThresholdHW": int(self.default_dict.get('rssiThresholdHW', 0)),
                    "rssiThresholdSW": int(self.default_dict.get('rssiThresholdSW', 9999)),
                    "tests": [{
                        "name": 'Calibration',
                        "rxChannel": 37,
                        "energizingPattern": self.test_suite[self.test].get('pattern'),
                        "timeProfile": [int(self.test_suite[self.test].get('tOn')),
                                        int(self.test_suite[self.test].get('tTotal'))],
                        "absGwTxPowerIndex": -1,
                        "maxTime": self.test_suite[self.test].get('testTime'),
                        "delayBeforeNextTest": int(self.test_suite[self.test].get('sleep')),
                        "stop_criteria": {'tbp_mean': [0, 9999]},
                        "quality_param": {}
                    }]
                }
            }

        logger = None
        try:

            timestamp = time.strftime("_%d%m%y_%H%M%S")
            name = str(self.external_id) + '_' + str(timestamp) if self.external_id else str(timestamp)
            logger = WiliotTesterLog(run_name=name)
            self.run_data_path, self.packets_data_path = logger.create_data_dir(self.output,
                                                                                tester_name='SampleChamber',
                                                                                run_name=name)
            logger.set_logger(log_path=self.output, tester_name='SampleChamber')
            logger.set_console_handler_level(logger.logger, logging.DEBUG)
            logger.set_console_handler_level(logger.gw_logger, logging.WARNING)
            logger.set_console_handler_level(logger.results_logger, logging.DEBUG)
            sample_test_dir = os.getcwd()
            config_dir = abspath(join(sample_test_dir, 'configs'))

            with open(abspath(join(config_dir, '.defaults.json')), 'r') as defaultComs:
                self.default_dict = json.load(defaultComs)

            with open(abspath(join(config_dir, '.default_test_configs.json')), 'r') as defaultTestConfig:
                self.test_suite = json.load(defaultTestConfig)
                if self.test in ['BLE_CALIBRATION', 'BEACON_CALIBRATION', 'LORA_CALIBRATION']:
                    self.selected_test_suite = convert_calibration_suite()
                else:
                    self.selected_test_suite = convert_test_suite()

            with open(abspath(join(config_dir, '.default_surfaces.json')), 'r') as defaultSurfaces:
                surface_configs = json.load(defaultSurfaces)
                self.default_freq = surface_configs['EmulateSurface'].get('no simulation', {})
                self.surface_freq_shift = surface_configs['EmulateSurface'].get(self.surface, {})

        except Exception as e:
            if logger is not None:
                logger.logger.error(f'Could not read configs: {e}')
            raise Exception(e)

        return logger

    def com_connect(self, default_coms=None):
        """
                Connect to all hardware components.

                Parameters:
                - default_coms (dict): Dictionary containing default COM port configurations.

                Connects to the Gateway, Attenuators [BLE and LORA],
                Barcode Scanner (if available), and Temperature Sensors (if available).
                """
        self.default_dict = default_coms
        gateway_obj = None
        try:
            gw_comport = self.default_dict.get('gw')
            atten_comport = self.default_dict.get('atten')

            # Connect to the GW
            gateway_obj = WiliotGateway(auto_connect=False, port=gw_comport,
                                        logger_name=self.logger.gw_logger.name)
            if gateway_obj.is_connected():
                self.gw_version = gateway_obj.get_gw_version()
                self.logger.logger.info('GW connected')
                if self.surface_freq_shift != self.default_freq:
                    gateway_obj.write('!set_sub_1_ghz_energizing_frequency {}'.format(self.surface_freq_shift),
                                      with_ack=True)
            else:
                raise Exception('GW is not connected')

            # Connect to attenuators
            if atten_comport.get('Ble') != '':
                self.ble_atten = Attenuator('API', comport=atten_comport.get('Ble')).GetActiveTE()

                if self.ble_atten.is_open():
                    self.ble_atten.Setattn(
                        float(self.test_suite[self.test].get('attenBle', 0)))  # Line to set attenuation
                    self.logger.logger.info(f'BLE Attenuator connected - Attenuation is {self.ble_atten.Getattn()}')

                else:
                    raise Exception('BLE Attenuator not connected')

            if atten_comport.get('LoRa') != '':
                self.lora_atten = Attenuator('API', comport=atten_comport.get('LoRa')).GetActiveTE()

                if self.lora_atten.is_open():
                    self.lora_atten.Setattn(
                        float(self.test_suite[self.test].get('attenLoRa', 0)))  # Line to set attenuation
                    self.logger.logger.info(f'LORA Attenuator connected - Attenuation is {self.lora_atten.Getattn()}')

                else:
                    raise Exception('LORA Attenuator not connected')

            # Connect to barcode if needed
            if not self.external_id and self.online:
                try:
                    barcode_comport = self.default_dict.get('barcodes')
                    self.barcode = BarcodeScanner(com_port=barcode_comport, timeout=str(QR_SCANNER_TIMEOUT))
                    if not self.barcode.is_open():
                        try:
                            self.barcode.open_port(com_port=self.default_dict.get('barcodes'),
                                                   timeout=str(QR_SCANNER_TIMEOUT))
                        except Exception as e:
                            raise Exception(f'Could not connect to barcode scanner and external ID was not passed {e}')

                    self.external_id, _, _, _ = self.barcode.scan_ext_id()

                    if not self.external_id:
                        raise Exception()

                except Exception as e:
                    self.logger.logger.error(
                        f'Unable to connect to barcode scanner, need external id or scanner to scan the tag {e}')

            # Connect to sensor if available
            sensor_comport = self.default_dict.get('temperature_sensors', '')
            if len(sensor_comport) > 0:
                self.sensor = YoctoSensor(logger=self.logger.logger.name)
                self.sensor.connect()
                self.logger.logger.info('LORA Attenuator connected')

        except Exception as e:
            available_ports = [port.description for port in serial.tools.list_ports.comports()]
            self.logger.logger.error(
                f'Please redefine the comports in defaults.json, \nAvailable comports: {available_ports}, {e}')
            exit()

        return gateway_obj

    def connect_to_cloud(self):
        """
        Establishes a secure connection to the cloud service for data storage and validation.

        Parameters: - env (str): Specifies the cloud environment to connect to. It can be either 'prod' for
        production or 'test' for testing.

        Steps:
        1. Reads the user's cloud configuration file to obtain API keys and owner IDs.
        2. Validates the owner ID against a predefined list of valid owner IDs.
        3. Initializes the cloud client using the API key and specified environment.
        4. Logs the successful establishment of the cloud connection.

        Note: If the connection fails or configurations are invalid, the function will raise an exception and close
        the Gateway port.
        """
        try:
            env = 'prod'
            g = GetApiKey(gui_type='ttk', env=env, owner_id=self.owner_id)
            api_key = g.get_api_key()
            if not api_key:
                raise Exception(f'Could not found an api key for owner id {self.owner_id} and env {env}')

            self.client = ManufacturingClient(api_key=api_key, env=env, logger_=self.logger.logger.name)
            self.logger.logger.info('Connection to the cloud was established')

        except Exception as e:
            self.close_gw_port()
            raise Exception(f'Problem connecting to cloud {e}')

    def close_gw_port(self):
        """
                Close the connection to the Gateway.

                If the Gateway is connected, this function will close the port.
                """
        self.gateway_obj.exit_gw_api()

    def perform_calibration_test(self, atten_type):
        calibration_data = {}
        end_calib = False
        if atten_type == 'LORA' or atten_type == 'BEACON':
            self.gateway_obj.write('!sub1g_sync 1', with_ack=True)
            self.wiliot_tag_test.selected_test['tests'][0]['sub1g_power'] = 29
        selected_tag = None
        for atten in range(0, 31):  # Sweep from 0 to 30
            self.set_attenuation(atten_type, atten)
            res = self.wiliot_tag_test.run()
            if not res.is_results_empty():
                list_of_tags = list(res.tests[0].all_tags.tags.keys())
                if not selected_tag:
                    selected_tag = res.tests[0].selected_tag[0].packet_data['adv_address']
                for tag in list_of_tags:
                    if tag != selected_tag:
                        self.wiliot_tag_test.black_list.append(tag)
                        self.wiliot_tag_test.add_to_blacklist([tag])
                tbp = res.tests[0].selected_tag.get_statistics().get('tbp_mean', 0)
                if int(tbp) > 0:
                    end_calib = False
                    calibration_data[atten] = tbp
                else:
                    if end_calib:
                        break
                    end_calib = True
            else:
                if end_calib:
                    break
                end_calib = True
        self.generate_graph(calibration_data, f'{atten_type} Calibration')

    def set_attenuation(self, atten_type, atten_value):
        if atten_type == 'BLE' or atten_type == 'BEACON':
            self.ble_atten.Setattn(atten_value)
            self.logger.results_logger.info(f'BLE Atten set to {self.ble_atten.Getattn()}')
        elif atten_type == 'LORA':
            self.lora_atten.Setattn(atten_value)
            self.logger.results_logger.info(f'LORA Atten set to {self.lora_atten.Getattn()}')
        else:
            raise ValueError(f'Unknown attenuation type: {atten_type}')

    def find_slope_point(self, x, y):
        """
        Find the point where the slope is approximately equal to 1.
        """
        slopes = np.diff(y) / np.diff(x)
        closest_index = np.argmin(np.abs(slopes - 1))
        return x[closest_index], y[closest_index]

    def find_saturation_point(self, y, window_size=5, threshold=0.01):
        """
        Find the saturation point in the calibration curve.
        """
        y_diff = np.abs(np.diff(y, n=1))
        rolling_avg_change = np.convolve(y_diff, np.ones(window_size) / window_size, mode='valid')
        saturation_index = np.argmax(rolling_avg_change < threshold)
        return saturation_index + window_size // 2

    def generate_graph(self, data, title):

        plt.figure(figsize=(10, 6))
        x, y = zip(*data.items())
        plt.plot(x, y, marker='o', linestyle='-')

        if title == 'BLE Calibration' or title == 'LORA Calibration':
            slope_point = self.find_slope_point(x, y)
            plt.plot(slope_point[0], slope_point[1], 'ro')  # Red dot at the slope point
        elif title == 'BEACON Calibration':
            saturation_point = self.find_saturation_point(y)
            plt.plot(x[saturation_point], y[saturation_point], 'ro')  # Red dot at the saturation point

        plt.title(title)
        plt.xlabel('Attenuation')
        plt.ylabel('TBP Value')
        plt.grid(True)
        plt.show()

    def start_test(self):
        """
        Initiates and executes the test sequence for Wiliot pixie.

        This function performs several key tasks:
        1. Initializes the data structures for storing test results in CSV format.
        2. Executes the test by calling the `run()` method on the `wiliot_tag_test` object.
        3. Collects statistics and summary information about the test.
        4. Populates the run data dictionary with test results and statistics.
        5. Updates the packets data CSV with packet-level information.
        6. If in 'online' mode, it also validates the test results by comparing them with cloud data.

        Returns:
        - True: If the test and optional validation are successful.
        - False: If the test or validation fails.

        Note: This function will also close the Gateway port in case of an exception.
        """
        try:
            self.initialize_csv_data()  # Init the run result dictionary
            res = self.wiliot_tag_test.run()  # Begin the run

            if res.is_results_empty():
                #   Failed
                self.logger.logger.error('Test failed')
                self.runDataDict['tested'] = 0
                self.runDataDict['responded'] = 0
                self.runDataDict['passed'] = 0
                raise Exception('something went wrong during test and test was not preformed')

            selected_tag_statistics = res.tests[0].selected_tag.get_statistics()  # Get all the statistics
            test_sum = res.tests[0].get_summary()

            self.runDataDict['tested'] = 1
            self.runDataDict['testTime'] = str(res.get_total_test_duration())
            self.runDataDict['passed'] = int(res.is_all_tests_passed())
            self.runDataDict['responded'] = int(1 if res.tests[0].all_packets.__len__() > 0 else 0)
            self.runDataDict['responding[%]'] = str(
                self.runDataDict['responded'] / self.runDataDict['tested'] * 100) + '%'
            self.runDataDict['passed[%]'] = str(self.runDataDict['passed'] / self.runDataDict['tested'] * 100) + '%'

            if self.runDataDict['passed']:
                self.logger.logger.info('Test passed')
                selected_tag_first_payload = res.tests[0].selected_tag[0].get_payload()
            elif self.runDataDict['responded']:
                selected_tag_statistics = res.tests[0].all_packets.get_statistics()
                selected_tag_first_payload = res.tests[0].all_packets[0].get_payload()
                self.logger.logger.info('Test failed, tag responded but tbp could not be calculated')
            else:
                self.logger.logger.info('Test failed, tag did not respond')

            # save files:
            self.populate_run_data(selected_tag_statistics, test_sum)  # Fill run result dictionary
            self.update_packets_data(res, selected_tag_statistics)

            # Compare if online
            if self.online and self.runDataDict['responded']:
                validation = self.compare_tag(selected_tag_first_payload)
            else:
                validation = True
                self.logger.results_logger.info('Validation pass')

            if not validation:
                self.logger.logger.error('Validation went wrong')

            self.wiliot_tag_test.exit_tag_test()
            return validation

        except Exception as e:
            self.close_gw_port()
            self.logger.logger.error(f'Problem starting the test {e}')

    def compare_tag(self, payload):
        """
                Compare the tag data with cloud data.

                Parameters:
                - payload (str): The payload to compare.

                Returns True if the comparison is successful, otherwise returns False.
                """
        try:
            cloud_data = self.client.resolve_payload(payload=payload,
                                                     owner_id=self.owner_id)

            selected_tag_external_id = cloud_data['externalId']
            self.logger.results_logger.info(
                f'External_ID from cloud: {selected_tag_external_id}\nExternal_ID to compare is {self.external_id}')
            return self.external_id.upper() == selected_tag_external_id.upper()

        except Exception as e:
            self.close_gw_port()
            self.logger.logger.error(f'Problem comparing {e}')

    def initialize_csv_data(self):
        """
                Initialize the CSV data structures.

                Sets up dictionaries for run data and packet data.
                """

        test_values = self.selected_test_suite[self.test]['tests'][0]
        self.common_run_name = self.external_id + self.common_run_name if self.external_id is not None else self.common_run_name

        self.runDataDict = {
            'testerStationName': 'WiliotSample',
            'commonRunName': self.common_run_name,
            'batchName': '',
            'testerType': 'sample',
            'comments': '',
            'errors': '',
            'timeProfile': test_values.get('timeProfile', ''),
            'txPower': test_values.get('absGwTxPowerIndex', ''),
            'energizingPattern': test_values.get('energizingPattern', ''),
            'tested': '0',
            'passed': '0',
            'yield': '0',
            'inlay': self.default_dict['inlay'][0],
            'responded': '0',
            'responding[%]': '0',
            'passed[%]': '0',
            'testStatus': 'False',
            'operator': 'Wiliot',
            'testTime': '',
            'runStartTime': '',
            'runEndTime': '',
            'antennaType': 'TIKI',
            'surface': self.surface,
            'numChambers': '1',
            'gwVersion': self.gw_version,
            'pyWiliotVersion': self.pywiliot_version,
            'bleAttenuation': self.default_dict['atten']['Ble'],
            'loraAttenuation': self.default_dict['atten']['LoRa'],
            'testTimeProfilePeriod': test_values.get('timeProfile'[1], ''),
            'testTimeProfileOnTime': test_values.get('timeProfile'[0], ''),
            'ttfpAvg': '',
            'tbpAvg': '',
            'tbpStd': '',
            'rssiAvg': '',
            'maxTtfp': '',
            'controlLimits': self.default_dict.get('controlLimits', ''),
            'hwVersion': '',
            'sub1gFrequency': self.surface_freq_shift,
            'failBinStr': '',
            'failBin': ''
        }

        self.test_data = {
            'commonRunName': self.common_run_name,
            'encryptedPacket': '',
            'time': '',
            'externalId': self.external_id,
            'reel': self.common_run_name,
            'ttfp': '',
            'tbp': '',
            'adv_address': '',
            'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)': '',
            'status': '',
            'chamber': '',
            'temperature_from_sensor': ''}

        dict_to_csv(dict_in=self.runDataDict, path=self.run_data_path, append=False, only_titles=True)
        self.packets_csv = CsvLog(header_type=HeaderType.PACKETS, path=self.packets_data_path,
                                  tester_type=TesterName.SAMPLE)
        self.packets_csv.open_csv()

    def populate_run_data(self, selected_tag_statistics, test_sum):
        """
                Populate the run data dictionary.

                Parameters:
                - selected_tag_statistics (dict): Statistics of the selected tag.
                - test_sum (dict): Summary of the test.

                Fills the run data dictionary with test results and statistics.
                """
        self.runDataDict['testStatus'] = bool(test_sum['is_test_pass'])
        self.runDataDict['runStartTime'] = test_sum['test_start_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        self.runDataDict['runEndTime'] = test_sum['test_end_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        self.runDataDict['ttfpAvg'] = str(selected_tag_statistics.get('ttfp', 'nan'))
        self.runDataDict['tbpAvg'] = str(selected_tag_statistics.get('tbp_mean', 'nan'))
        self.runDataDict['tbpStd'] = str(selected_tag_statistics.get('tbp_std', 'nan'))
        self.runDataDict['rssiAvg'] = str(selected_tag_statistics.get('rssi_mean', 'nan'))
        self.runDataDict['maxTtfp'] = str(selected_tag_statistics.get('ttfp', 'nan'))
        dict_to_csv(dict_in=self.runDataDict, path=self.run_data_path, append=True, only_titles=False)

    def update_packets_data(self, res=None, stats=None):
        """
                Update the packets data CSV.

                Parameters:
                - res (object): The result object containing test data.
                - stats (dict): Statistics of the selected tag.

                Updates the packets data CSV with packet information.
                """

        if res:
            r = res.tests[0]
            if r.selected_tag.__len__() > 0:  # pass
                tag_data = r.selected_tag
            elif r.all_packets.__len__() > 0:  # responded but did not pass
                tag_data = r.all_packets
            else:  # No response
                self.test_data.update({
                    'encryptedPacket': '',
                    'time': '',
                    'chamber': 0,
                    'status': r.is_test_passed,
                    'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)': -2,
                    'ttfp': str(stats.get('ttfp', 'nan')),
                    'tbp': str(stats.get('tbp_min', 'nan')),
                    'adv_address': '',
                    'temperature_from_sensor': self.sensor.get_temperature()
                    if self.sensor is not None else 'nan'})
                return

            for p in tag_data:
                for i in range(p.gw_data['gw_packet'].size):
                    if p.gw_data["time_from_start"].size > 1:
                        time_from_start = p.gw_data["time_from_start"][i]
                    else:
                        time_from_start = p.gw_data["time_from_start"].item()
                    self.test_data.update({
                        'encryptedPacket': p.get_packet_content(get_gw_data=True, sprinkler_num=i),
                        'time': time_from_start,
                        'chamber': 0,
                        'status': r.is_test_passed,
                        'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)': 0 if stats[
                            'tbp_mean'] else -1,
                        'ttfp': str(stats.get('ttfp', 'nan')),
                        'tbp': str(stats.get('tbp_min', 'nan')),
                        'adv_address': res.get_test_unique_adva(),
                        'temperature_from_sensor': self.sensor.get_temperature()
                        if self.sensor is not None else 'nan'})
                    self.packets_csv.append_dict_as_row([self.test_data])

    def cloud_upload(self, env):
        """
        Uploads the collected test data to the cloud for further analysis and storage.

        Parameters: - env (str): Specifies the cloud environment to upload to. It can be either 'prod' for production
        or 'test' for testing.

        The function performs the following tasks:
        1. Calls the `upload_to_cloud_api` function to upload both run data and packets data CSV files.
        2. Logs the status of the upload operation.

        Returns:
        - True: If the data upload to the cloud is successful.
        - False: If the data upload fails for any reason.

        Note: The function uses the owner ID and API key that were set during the cloud connection phase.
        """
        success = upload_to_cloud_api(batch_name='',
                                      tester_type='sample-test',
                                      run_data_csv_name=self.run_data_path,
                                      packets_data_csv_name=self.packets_data_path,
                                      is_path=True,
                                      env=env,
                                      owner_id=self.owner_id,
                                      logger_=self.logger.logger.name)

        return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample Chamber")

    parser.add_argument('-n', '--name', default="", help="The test name (common run name prefix)")
    parser.add_argument('-m', '--mode', default="offline", choices=['online', 'offline'],
                        help="Online mode when using cloud, Offline with barcode scanner")
    parser.add_argument('-o', '--ownerid',
                        help="Owner ID for getting api_key from the cloud - required in online mode")
    parser.add_argument('-e', '--externalID', help="Tag External ID")
    parser.add_argument('-t', '--test', required=True, choices=['TIKI_LORA', 'TIKI_BLE',
                                                                'BLE_CALIBRATION', 'BEACON_CALIBRATION',
                                                                'LORA_CALIBRATION'],
                        help="Test to perform")
    parser.add_argument('--env', choices=['prod', 'test'], help="Environment from cloud")
    parser.add_argument('-s', '--surface', default="no simulation",
                        choices=['simulate cardboard', 'simulated RPC', 'no simulation'], help="Surface to simulate")
    parser.add_argument('--output', help="Files output")

    args = parser.parse_args()

    chamber = SampleChamber(mode=args.mode, external_id=args.externalID, test=args.test, env=args.env,
                            owner_id=args.ownerid, surface=args.surface, output_path=args.output,
                            name=args.name)

    # Examples for console:
    # python sample_chamber.py --mode offline --test TIKI_BLE --externalID (01)00850027865010(21)04z3T0049
    # python sample_chamber.py --mode online --test TIKI_BLE --externalID (01)00850027865010(21)04z3T0049 --env prod

    # Examples to execute from code:
    # mode = 'Online'
    # externalID = ''
    # test = 'TIKI_LORA'
    # env = 'prod'
    # owner_id = 'wiliot-ops'
    # surface = 'simulate cardboard'
    # chamber = SampleChamber(mode=mode, external_id=externalID, test=test, env=env, owner_id=owner_id, surface=surface)
