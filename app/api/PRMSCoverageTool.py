__author__ = 'jerickson'

import netCDF4
import shutil
import os
import time

from numpy import reshape

from client.model_client.client import ModelApiClient
from client.swagger_client.apis.default_api import DefaultApi


class ScenarioRun:
    """
    Scenario Run object representation of the process of creating and running
    a PRMS Scenario
    """

    scenario_file = ""

    def __init__(self, basefile):
        self.basefile = basefile
        self.working_scenario = None
        self.scenario_name = None

    def initialize(self, scenario_name):
        '''
        Starts a new scenario based on the original file under a new name

        :param scenario_name: Name of scenario to make a new file;
            .nc will be appended
        :return:
        '''
        if self.working_scenario is not None:
            raise Exception("Working Scenario already open")
            return

        if os.path.exists("{0}.nc".format(scenario_name)):
            sequence = 2
            while os.path.exists("{0}-{1}.nc".format(scenario_name, sequence)):
                sequence = sequence + 1
            self.scenario_file = "{0}-{1}.nc".format(scenario_name, sequence)
        else:
            self.scenario_file = "{0}.nc".format(scenario_name)

        shutil.copyfile(self.basefile, self.scenario_file)
        self.working_scenario = netCDF4.Dataset(self.scenario_file, 'r+')

        self.scenario_name = scenario_name

    def end(self):
        '''
        Close the working scenario and free our references to it
        :return:
        '''
        if self.working_scenario is None:
            return
        self.working_scenario.close()
        self.working_scenario = None

    def debug_display_cov_type(self, hru):
        '''
        For debug purposes; given a list of hrus, display the
        coverage type for each coordinate

        :param coords: List of coordinates
        :return:
        '''
        if self.working_scenario is None:
            raise Exception("No working scenario defined")
            return

        print self.working_scenario.variables['cov_type'][hru]

    def update_cov_type(self, hru, val):
        '''
        Update coverage type in a single hru using 2d coordinates
        :param hru (list): list of HRU to set to a new value, val
        :param val: value to set hru to
        :return:
        '''
        if self.working_scenario is None:
            raise Exception("No working scenario defined")
            return

        if hru != []:
            ctmat = self.working_scenario.variables['cov_type'][:]
            ctvec = ctmat.flatten()
            ctvec[hru] = val
            self.working_scenario.variables['cov_type'][:] = \
                reshape(ctvec, ctmat.shape)

    def run(self, auth_host=None, model_host=None,
            app_username=None, app_password=None):
        """
        Run PRMS on model server using the updated parameters file and
        standard data.nc and control.nc files.

        Arguments:
            auth_host (str): hostname for the authentication server
            model_host (str): hostname for the modeling server
            app_username (str): username used on modeling/auth server
            app_password (str): username used on modeling/auth server

        Returns:
            (client.swagger_client.models.model_run.ModelRun)
        """
        if self.working_scenario is None:
            raise Exception("No working scenario defined")
            return

        auth_host = 'http://192.168.99.100:5005/api'
        model_host = 'http://192.168.99.100:5000/api'
        app_username = 'maturner01@gmail.com'
        app_password = 'ajajaj'

        cl = ModelApiClient(auth_host=auth_host, model_host=model_host)
        cl.authenticate_jwt(username=app_username, password=app_password)

        api = DefaultApi(api_client=cl)

        mr = api.create_modelrun(
            modelrun=dict(title=self.scenario_name, model_name='prms')
        )

        api.upload_resource_to_modelrun(
            mr.id, 'control', 'app/static/data/LC.control'
        )
        api.upload_resource_to_modelrun(
            mr.id, 'data', 'app/static/data/LC.data.nc'
        )
        api.upload_resource_to_modelrun(
            mr.id, 'param', self.scenario_file
        )

        api.start_modelrun(mr.id)

        run_not_finished = True
        while run_not_finished:
            state = api.get_modelrun_by_id(mr.id).progress_state
            run_not_finished = (
                state != 'FINISHED' and
                state != 'ERROR'
            )
            time.sleep(0.5)

        if state == 'ERROR':
            raise RuntimeError('Model server execution failed!')

        return api.get_modelrun_by_id(mr.id)


if __name__ == "__main__":
    prmsfile = ScenarioRun("parameter.nc")

    coord_list_old = [(0, 0), (0, 1), (0, 2),
                      (1, 0), (1, 1), (1, 2),
                      (2, 0), (2, 1), (2, 2)]

    coord_list = [0,   1,   2,
                  96,  97,  98,
                  192, 193, 194]

    try:
        prmsfile.begin("test")
        prmsfile.debug_display_cov_type(coord_list)
        prmsfile.debug_display_cov_type(coord_list_old)
        prmsfile.block_update_cov_type(coord_list, 2)
        prmsfile.debug_display_cov_type(coord_list)
        prmsfile.debug_display_cov_type(coord_list_old)
        prmsfile.end()

    except Exception as ex:
        print "Test run failed: " + ex.message

    print "Testing exceptions..."
    try:
        prmsfile.debug_display_cov_type(coord_list)
    except Exception as ex:
        print "DebugDisplayCovType properly failed"
    try:
        prmsfile.update_cov_type(coord_list)
    except Exception as ex:
        print "BlockUpdateCovType properly failed"
