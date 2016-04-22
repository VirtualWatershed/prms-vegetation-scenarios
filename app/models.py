import json
import netCDF4
import os
import shutil
import time

from numpy import reshape

from client.model_client.client import ModelApiClient
from client.swagger_client.apis.default_api import DefaultApi

from . import db


class Hydrograph(db.EmbeddedDocument):
    """
    Hydrograph output data
    """
    time_array = db.ListField(db.DateTimeField())
    streamflow_array = db.ListField(db.FloatField())


class VegetationMapByHRU(db.EmbeddedDocument):
    """
    Vegetation map by HRU, modified as requested by the user
    """
    bare_ground = db.ListField(db.IntField())
    elevation = db.ListField(db.FloatField())
    grasses = db.ListField(db.IntField())
    shrubs = db.ListField(db.IntField())
    trees = db.ListField(db.IntField())
    conifers = db.ListField(db.IntField())
    projection_information = db.EmbeddedDocumentField('ProjectionInformation')


class ProjectionInformation(db.EmbeddedDocument):
    """
    Information used to display gridded data on a map
    """
    ncol = db.IntField()
    nrow = db.IntField()
    xllcorner = db.FloatField()
    yllcorner = db.FloatField()
    xurcorner = db.FloatField()
    yurcorner = db.FloatField()
    cellsize = db.FloatField()


class Inputs(db.EmbeddedDocument):
    """
    download links to control, data, and parameter files for a given scenario
    """
    control = db.URLField(default='http://example.com/control.dat')
    parameter = db.URLField(default='http://example.com/parameter.nc')
    data = db.URLField(default='http://example.com/data.nc')


class Outputs(db.EmbeddedDocument):
    """
    download links to PRMS outputs from scenario
    """
    statsvar = db.URLField(default='http://example.com/statvar.nc')


class Scenario(db.Document):
    """
    Scenario data and metadata
    """
    name = db.StringField(required=True)
    user = db.StringField(default='anonymous')

    time_received = db.DateTimeField(required=True)
    time_finished = db.DateTimeField()

    veg_map_by_hru = db.EmbeddedDocumentField('VegetationMapByHRU')

    inputs = db.EmbeddedDocumentField('Inputs')
    outputs = db.EmbeddedDocumentField('Outputs')

    hydrograph = db.EmbeddedDocumentField('Hydrograph')

    run = None

    def initialize_runner(self, base_file):

        self.runner = ScenarioRun(base_file)

        self.runner.initialize(self.name)

        return self.runner

    def to_json(self):
        """
        Override db.Document's to_json for custom date fomratting
        """
        base_json = db.Document.to_json(self)

        js_dict = json.loads(base_json)

        js_dict['hydrograph']['time_array'] = [
            d.isoformat() for d in self.hydrograph.time_array
        ]

        js_dict['time_received'] = self.time_received.isoformat()
        js_dict['time_finished'] = self.time_finished.isoformat()

        js_dict['id'] = str(self.pk)

        return json.dumps(js_dict)

    def __str__(self):

        return \
            '\n'.join(["{}: {}".format(k, self[k])
                       for k in self._fields_ordered])


class ScenarioRun:
    """
    Scenario Run object representation of the process of creating and running
    a PRMS Scenario
    """

    scenario_file = ""

    def __init__(self, base_file):
        self.base_file = base_file
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

        if not os.path.exists('.tmp'):
            os.mkdir('.tmp')

        self.scenario_file = os.path.join('.tmp', self.scenario_file)

        shutil.copyfile(self.base_file, self.scenario_file)
        self.working_scenario = netCDF4.Dataset(self.scenario_file, 'r+')

        self.scenario_name = scenario_name

    def finalize_run(self):
        '''
        Finalize the updates to the param file and free our references to it
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
        if self.working_scenario is not None:
            raise Exception(
                "Working Scenario is still being updated! `finalize_run` first"
            )
            return

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
        # clean up scenario file after upload
        os.remove(self.scenario_file)

        api.start_modelrun(mr.id)

        run_not_finished = True
        while run_not_finished:
            state = api.get_modelrun_by_id(mr.id).progress_state
            run_not_finished = (
                state != 'FINISHED' and
                state != 'ERROR'
            )
            time.sleep(1)

        if state == 'ERROR':
            raise RuntimeError('Model server execution failed!')

        return api.get_modelrun_by_id(mr.id)
