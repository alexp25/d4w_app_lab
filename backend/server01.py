# python modules
import copy
import csv
import datetime
import gevent
import gevent.monkey
import json
import os
import random
import string
import subprocess
import sys
import threading
import time
from dateutil.parser import parse
from flask import Flask
from flask import jsonify
from flask import render_template, send_file, session, Response, request, make_response, send_from_directory
from gevent.pywsgi import WSGIServer
from multiprocessing import Process, Queue

gevent.monkey.patch_time()
# gevent.monkey.patch_all(socket=True, dns=True, time=True, select=True, thread=False, os=False, ssl=True, httplib=False, subprocess=False, sys=False, aggressive=True, Event=False, builtins=True, signal=False)
# from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask_socketio import SocketIO
from flask_socketio import send, emit, disconnect



# app modules
from modules.data import variables
from modules.data.constants import Constants

# only the main modules calls init
# the other modules using the global variables just import "appVariables"
variables.init()

# from AppModules.deprecated.DebugPrintThread import DebugPrintThread
# from AppModules.deprecated.DataBucketThread import DataBucketThread
# from AppModules.deprecated.TCPServerAsync import simple_tcp_server
from modules.core.manager import TestRunnerManager
from modules.control_thread import ControlSystemsThread
# from modules.database_process import DatabaseManagerProcess
from modules.data.log import Log

from modules.test.TCPServer import TCPServer

from machine_learning_main import MachineLearningMain

from modules.network import FindPath


# app config
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
static_folder = "dist"
app = Flask(__name__,static_folder=static_folder, template_folder=tmpl_dir)
# app.debug = appVariables.appConfig['debug']
app.debug = False


def default_json(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis
    raise TypeError('Not sure how to serialize %s' % (obj,))

def process_data():
    variables.machine_learning.assign_class_to_nodes()
    variables.network.set_class_for_consumers(variables.machine_learning.get_info()["nodes"])
    variables.network.calculate_class_for_intermediary_nodes()

socketio = SocketIO(app)

@socketio.on('my_event')
def handle_my_event(jsondata):
    emit('my_response', jsondata)

@socketio.on('get_data')
def handle_get_data(jsondata):
    time.sleep(variables.app_config["params"]["ts_disp"])
    if jsondata['reqtype']=='sensors':
        jsondata['value']=None
        if jsondata['type'] in [1, 2]:
            p = next((x for x in variables.sensor_data if ((x['id'] == jsondata['sensorId']) and (x['type'] == jsondata['type']))), None)
            if p is not None:
                jsondata['value'] = p['value']
                jsondata['value1'] = p['value1']
                jsondata['value2'] = p['value2']
        elif jsondata['type']==100:
            jsondata={
                'sensors': variables.sensor_data,
                'devices': variables.device_data
            }
    elif jsondata['reqtype']=='control':
        jsondata = {
            "info": variables.app_flags,
            "controllers": variables.app_config['controllers'],
            "controller_names": variables.app_config['controller_names']
        }
    # print jsondata['value']
    emit('get_data', jsondata)

@socketio.on('post_data')
def handle_post_data(jsondata):
    variables.log2("socketio - post data", json.dumps(jsondata))

    if jsondata['type'] == 'dev':
        if jsondata['id'] == 1:
            # set pump cmd
            variables.test_manager.set_pump(jsondata['value'])

    elif jsondata['type'] == 'app':
        if jsondata['id'] == 1:
            # change flow ref
            variables.app_flags['ref'] = jsondata['value']
        elif jsondata['id'] == 10:
            # set log flag
            try:
                mode = int(jsondata['value'])
            except:
                mode = jsondata['value']

            if mode == 1:
                if not variables.app_flags['log']:
                    variables.log2("socketio - post data", "start log")
                    variables.new_log()
                    variables.app_flags['log'] = True
            else:
                variables.log2("socketio - post data", "stop log")
                variables.app_flags['log'] = False

        elif jsondata['id'] == 20:
            # change control mode
            try:
                mode = int(jsondata['value'])
            except:
                mode = jsondata['value']
            variables.app_flags['mode'] = mode
            variables.app_aux_flags['spab_index'] = 0
            if variables.app_flags['mode'] not in [1, 5]:
                variables.app_flags['integral'] = 0
        elif jsondata['id'] == 21:
            # change controller model
            variables.app_flags['controller_id'] = jsondata['value']
        elif jsondata['id'] == 30:
            # supervisor
            try:
                mode = int(jsondata['value'])
            except:
                mode = jsondata['value']

            variables.app_flags['supervisor'] = mode


@socketio.on('disconnect_request')
def handle_disconnect_request(jsondata):
    disconnect()


@app.route('/')
def mypisite():
    return render_template('index.html')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"

    r.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/api/database/sensors')
def apiDatabaseSensors():
    try:
        param = request.args.get('param')
        variables.log2("routes", '/api/database/sensors ' + param)
        param = json.loads(param)
        # param['sid']
        # params['n']
        # print(param)
        if param['id'] != 0 and variables.app_config["app"]["db_access"]:
            cursor = variables.cnxn.cursor()
            cursor.execute("SELECT * FROM (SELECT TOP " + str(param['n']) + " * FROM SensorData_Flow WHERE Pipe_ID = ? ORDER BY Timestamp DESC) a ORDER BY Timestamp ASC",param['id'])
            # cursor.execute("SELECT TOP 100 * FROM SensorData_Flow WHERE Pipe_ID = ? ORDER BY Timestamp DESC",param['id'])
            rows = cursor.fetchall()

            columns = [column[0] for column in cursor.description]
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            # print(results)

            return json.dumps(results, default=default_json)
        else:
            result = Constants.RESULT_FAIL
            return json.dumps({"result": result})
    except:
        variables.print_exception("[routes][/api/database/sensors]")
        result = Constants.RESULT_FAIL
        return json.dumps({"result": result})


@app.route('/api/machine-learning/info')
def apiMachineLearningInfo():
    try:
        variables.log2("routes", '/api/machine-learning/info')
        info = variables.machine_learning.get_info()
        return json.dumps({"info": info}, default=default_json)
    except:
        variables.print_exception("[routes][/api/machine-learning/info]")
        result = Constants.RESULT_FAIL
        return json.dumps({"result": result})

@app.route('/api/machine-learning/raw')
def apiMachineLearningRaw():
    try:
        param = request.args.get('param')
        variables.log2("routes", '/api/machine-learning/raw ' + param)
        param = json.loads(param)

        if param["node"] is not None:
            (data, info) = variables.machine_learning.get_raw_data(param["node"])
        else:
            return json.dumps({"result": Constants.RESULT_FAIL})

        if param["node"] != -1:
            info2 = variables.machine_learning.get_info(param["node"])
        else:
            info2 = None

        # print(data)
        return json.dumps({"data": data, "info": info, "extra": info2}, default=default_json)
    except:
        variables.print_exception("[routes][/api/machine-learning/raw]")
        return json.dumps({"result": Constants.RESULT_FAIL})

@app.route('/api/machine-learning/init')
def apiMachineLearningInit():
    try:
        # param = request.args.get('param')
        variables.log2("routes", '/api/machine-learning/init ')
        # param = json.loads(param)
        variables.machine_learning.init()
        return json.dumps({"result": Constants.RESULT_FAIL})
    except:
        variables.print_exception("[routes][/api/machine-learning/init]")
        return json.dumps({"result": Constants.RESULT_FAIL})

@app.route('/api/machine-learning/clusters')
def apiMachineLearningClusters():
    try:
        param = request.args.get('param')
        variables.log2("routes", '/api/machine-learning/clusters ' + param)
        param = json.loads(param)
        res = None
        n_clusters = 3
        n_clusters_final = 4
        if param["dual_clustering"] == 0:
            if param["node"] != -1:
                # get clusters for the specified node
                if param["node"] is not None:
                    res = variables.machine_learning.run_clustering_on_node_id(param["node"], n_clusters)
                else:
                    return json.dumps({"result": Constants.RESULT_FAIL})
            else:
                # get clusters from all nodes
                res = variables.machine_learning.run_clustering_on_node_range(0, param["new_node"], n_clusters)
        else:
            # get clusters from clusters from all nodes
            # this will recalculate all clusters and reassign nodes
            try:
                res = variables.machine_learning.run_dual_clustering_on_node_range(0, param["new_node"], n_clusters, n_clusters_final)
            except:
                # different number of clusters
                variables.print_exception("/api/machine-learning/clusters")
                variables.machine_learning.init()
                res = variables.machine_learning.run_dual_clustering_on_node_range(0, param["new_node"], n_clusters,
                                                                                   n_clusters_final)

            if param["assign"]:
                process_data()

        (data, info) = variables.machine_learning.get_display_data(res, global_scale=param["global_scale"])

        if param["node"] != -1:
            info2 = variables.machine_learning.get_info(param["node"])
        else:
            info2 = None

        return json.dumps({"data": data, "info": info, "extra": info2, "params": param}, default=default_json)
    except:
        variables.print_exception("[routes][/api/machine-learning/clusters]")
        result = Constants.RESULT_FAIL
        return json.dumps({"result": result})

@app.route('/api/network/graph')
def apiNetworkGraph():
    try:
        variables.log2("routes", '/api/network/graph ')
        data = json.dumps(variables.network.get_data_format())
        return json.dumps({"data": data}, default=default_json)
    except:
        variables.print_exception("[routes][/api/network/graph]")
        result = Constants.RESULT_FAIL
        return json.dumps({"result": result})

@app.route('/api/download/log', methods=['GET'])
def apiDownloadLog():
    filename = "log.csv"
    return send_file(filename,
                     mimetype='text/plain',
                     attachment_filename=filename,
                     as_attachment=True)

@app.route('/api/reload', methods=['GET'])
def apiReload():
    variables.load_app_config()
    variables.test_manager.update_hil_devices()

    result = Constants.RESULT_OK
    return json.dumps({"result": result})

@app.route('/api/settings', methods=['GET', 'POST'])
def apiSettings():
    if request.method == "GET":
        result = Constants.RESULT_OK
        return json.dumps({"result": result, "data": variables.app_config})
    else:
        print (request.json)
        result = Constants.RESULT_OK
        return json.dumps({"result": result})

@app.route('/api/file/settings', methods=['GET', 'POST'])
def apiFileSettings():
    filename = "config.json"
    filename_full = 'config/' + filename

    if request.method == "GET":
        return send_file(filename_full,
                         mimetype='text/plain',
                         attachment_filename="config.json",
                         as_attachment=True)
    else:
        file = request.files["file"]
        print(file)
        file_extension = file.filename.rsplit('.', 1)
        print(file_extension)
        dev = int(request.form.getlist('id')[0])
        print(dev)
        try:
            if len(file_extension) > 0:
                file_extension = file_extension[1]
            else:
                raise Exception("no file extension")
            if not file_extension == "json":
                raise Exception("file extension mismatch")

            file_contents = file.read()
            file_contents_json = json.loads(file_contents)
            file_contents_new = json.dumps(file_contents_json, indent=2)
            # file.save(os.path.join("config/", filename))
            with open(filename_full, 'w') as f:
                f.write(file_contents_new)

            variables.load_app_config()

            variables.test_manager.update_hil_devices()

        except Exception as inst:
            result = {
                "result": Constants.RESULT_FAIL,
                "msg": "file upload failed. " + inst.__str__(),
            }
            return json.dumps(result)

        # print(file_contents)
        result = Constants.RESULT_OK
        return json.dumps({"result": result})


@app.route('/api/download/log-dbg', methods=['GET'])
def apiDownloadLogDbg():
    filename = variables.app_config["app"]["log_file_stdout"]
    return send_file(filename,
                     mimetype='text/plain',
                     attachment_filename="log_file_stdout",
                     as_attachment=True)

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    q_read_tcp = Queue(maxsize=10)
    q_write_tcp = Queue(maxsize=10)
    time.sleep(1)
    print(variables.app_config["app"]["db_selection"])
    db_info = variables.app_config["db_info"][variables.app_config["app"]["db_selection"]]
    if variables.app_config["app"]["db_access"]:
        import pyodbc
        try:
            variables.cnxn = pyodbc.connect(
                'DRIVER=' + db_info["driver"] + ';SERVER=' + db_info["server"] + ';DATABASE=' +
                db_info["database"] + ';UID=' + db_info["username"] + ';PWD=' + db_info[
                    "password"])
        except:
            variables.print_exception("server")

    variables.test_manager = TestRunnerManager()
    variables.test_manager.start()

    tlog = Log()
    tlog.start()

    thread8 = ControlSystemsThread()
    thread8.start()


    # test server
    from modules.test.TCPServer import TCPServer

    t = TCPServer("127.0.0.1", 9001)
    t.set_function(0)
    t.start()

    t = TCPServer("127.0.0.1", 9002)
    t.set_function(101)
    t.start()

    t = TCPServer("127.0.0.1", 9003)
    t.set_function(1)
    t.start()

    if variables.app_config["app"]["use_mqtt"]:
        from modules.test.mqtt_client import MQTTClient
        m = MQTTClient()
        m.start()

    if variables.app_config["app"]["machine_learning"]:
        variables.machine_learning = MachineLearningMain()
        variables.machine_learning.read_data()

        variables.network = FindPath()
        variables.network.load_data_json("data/network_simple.json")
        variables.network.format_data()


    variables.log2("main", " server started")

    variables.machine_learning.init()
    variables.machine_learning.run_dual_clustering_on_node_range(0, None, 3, 3)
    process_data()


    server = pywsgi.WSGIServer(('0.0.0.0', 8086), app, handler_class=WebSocketHandler)
    server.serve_forever()


