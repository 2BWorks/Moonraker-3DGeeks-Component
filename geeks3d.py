
import uuid
import logging
import asyncio
import json 

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode

GEEKS3D_NAMESPACE = "geeks"
AWS_LAMBDA_ENDPOINT = "https://qx8eve27wk.execute-api.eu-west-2.amazonaws.com/prod/moonraker-push"
VERSION = 1
VERSION_NAME = "1.0"

class Geeks3D:
    def __init__(self, config):

        # Init values
        self.last_progress = 0
        self.printer_cfg = {}
        self.current_state = "None"
        self.current_job_name = "Unknown"
        self.error_message = ""
        self.current_progress = 0
        self.current_time_passed = 0
        self.total_print_time = 0
        self.current_eta = 0
        self.printer_state = {}
        self.server = config.get_server()
        self.name = config.get_name()

        self.klippy_apis = self.server.lookup_component('klippy_apis')
        self.database = self.server.lookup_component("database")
        self.database.register_local_namespace(GEEKS3D_NAMESPACE)
        self.db_ns = self.database.wrap_namespace(GEEKS3D_NAMESPACE)

        # Percentage interval to notify phone, for example when set to 25
        # You will be notified when the print hits the: 25%, 50%, 75%, 100% mark
        # Default: 10, Minimum: 5, Maximum: 100
        self.notify_update_interval = config.getfloat("notify_update_interval", 10)
        if self.notify_update_interval < 5:
            self.notify_update_interval = 5
        # Machine is the name that gets displayed in the push notifications, Default: Klipper
        self.machine_name = config.get("machine_name", "Klipper")
        # Wether or not notify whenever a print starts, Default: True
        self.notify_print_started = config.getboolean("notify_print_started", True)
        # Wether or not to notify user whenever a print pauses, Default: True
        self.notify_print_paused = config.getboolean("notify_print_paused", True)
        # Wether or not to notify user whenever a print resumes, Default: True
        self.notify_print_resumed = config.getboolean("notify_print_resumed", True)
        # Wether or not to notify user whenever a print completes, Default: True
        self.notify_print_completed = config.getboolean("notify_print_completed", True)
        # Wether or not to notify user whenever a print is cancelled, Default: True
        self.notify_print_cancelled = config.getboolean("notify_print_cancelled", True)
        # Wether or not to notify user whenever a print fails, the reason will also be put in the notification
        # Default: True
        self.notify_print_failed = config.getboolean("notify_print_failed", True)
        # Wether or not to notify user when the server comes online
        # Default: True
        self.notify_server_startup = config.getboolean("notify_server_startup", True)
        # Wether or not to notify user when the server comes online
        # Default: True
        self.notify_klippy_disconnect = config.getboolean("notify_klippy_disconnect", True)
        # Wether or not to notify user when klippy is ready
        # Default: True
        self.notify_klippy_ready = config.getboolean("notify_klippy_ready", True)
        # Wether or not to notify user when klippy is shutdown
        # Default: True
        self.notify_klippy_shutdown = config.getboolean("notify_klippy_shutdown", True)
        # The endpoint that get's called whenever an event happens. You can substitute this for your own.
        # see: _call_notification_endpoint() for the implementation of the POST Body
        # Default: AWS_LAMBDA_ENDPOINT
        self.notify_endpoint = config.get("notification_endpoint", AWS_LAMBDA_ENDPOINT)

        # Create the push token, it's the magic link between app and moonraker
        # It's secret and should be treated as a password
        # Do not share with anybody
        self._create_push_token()

        # Geeks 3D Moonrake API
        self.server.register_endpoint("/server/geeks3d/push_token", ['GET'],
                                      self._get_push_token)


        # Refresh push token
        self.server.register_endpoint("/server/geeks3d/refresh_push_token", ['GET'],
                                      self._refresh_push_token)
        # Send a test push notification to verify setup is correct
        self.server.register_endpoint("/server/geeks3d/test_push_token", ['GET'],
                                      self._test_push)

        # Send a test push notification to verify setup is correct
        self.server.register_endpoint("/server/geeks3d/version", ['GET'],
                                      self._get_version_info)

        # Only register this endpoint for debug purposes
        self.server.register_endpoint("/server/geeks3d/status", ['GET'],
                                      self._get_last_status)
    
        # Register server events
        self.server.register_event_handler(
            "server:klippy_ready", self._handle_klippy_ready)
        self.server.register_event_handler(
            "server:klippy_shutdown", self._handle_klippy_shutdown)
        self.server.register_event_handler(
            "server:klippy_disconnect", self._handle_klippy_disconnect)
        self.server.register_event_handler(
            "server:status_update", self._handle_status_update)

        # Notify server has started up
        if self.notify_server_startup:
            payload = self._create_payload("startup")
            self._call_notification_endpoint(payload)

    def _create_push_token(self):
        # Your push token is very secret. Do not share! Treat it as a password.
        self.push_token = self.db_ns.get("geeks_push_token")
        if self.push_token == None :
            self.push_token = str(uuid.uuid4())
            self.db_ns.insert("geeks_push_token", self.push_token)   
            self.fresh_push_token = True   
        else :
            self.fresh_push_token = False    

    async def _refresh_push_token(self, web_request):
        self.push_token = str(uuid.uuid4())
        self.db_ns.update_child("geeks_push_token", self.push_token)   
        self.fresh_push_token = True   
        return {"push_token": self.push_token, "is_refreshed": True, "is_fresh": self.fresh_push_token}



    async def _get_push_token(self, web_request):
        return {"push_token": self.push_token, "is_fresh": self.fresh_push_token}


    async def _get_version_info(self, web_request):
        return {"version_code": VERSION, "version_name": VERSION_NAME}


    async def _test_push(self, web_request):
        pl =  self._create_payload("test")
        self._call_notification_endpoint(pl)
        return {"sent_push": True, "push_token" : self.push_token, "payload" : pl}

    async def _get_last_status(self, web_request):
        return {
            "printer_state": self.printer_state,
            "printer_config" : self.printer_cfg, 
            "name": self.name, 
            "payload": self._create_payload("PrintProgress")
        }

    ## Event handlers

    async def _handle_klippy_disconnect(self):
        if self.notify_klippy_disconnect:
            payload = self._create_payload("disconnected")
            self._call_notification_endpoint(payload)

    
    async def _handle_klippy_shutdown(self):
        if self.notify_klippy_shutdown:
            payload = self._create_payload("shutdown")
            self._call_notification_endpoint(payload)

    async def _handle_klippy_ready(self):
        # Request "info" and "configfile" status
        retries = 10
        printer_info = cfg_status = {}
        while retries:
            try:
                printer_info = await self.klippy_apis.get_klippy_info()
                cfg_status = await self.klippy_apis.query_objects(
                    {'configfile': None})
            except self.server.error:
                logging.exception("3D Geeks initialization request failed")
                retries -= 1
                if not retries:
                    raise
                await gen.sleep(1.)
                continue
            break

        config = cfg_status.get('configfile', {}).get('config', {})
        self.printer_cfg = config.get('printer', {})
        self.kinematics = self.printer_cfg.get('kinematics', "none")

        # Initalize printer state and make subscription request
        self.printer_state = {
            'virtual_sdcard': {},
            'display_status': {}, 
            'print_stats': {},
            'gcode_move': {}, 
            'toolhead': {}
        }

        sub_args = {k: None for k in self.printer_state.keys()}
        self.extruder_count = 0
        try:
            status = await self.klippy_apis.subscribe_objects(sub_args)
        except self.server.error:
            logging.exception("Unable to complete subscription request")
        else:
            self.printer_state.update(status)
        self.is_shutdown = False
        self.is_ready = True

        if self.notify_klippy_ready:
            payload = self._create_payload("connected")
            self._call_notification_endpoint(payload)


    async def _handle_status_update(self, status):
        for obj, items in status.items():
            if obj in self.printer_state:
                self.printer_state[obj].update(items)
            else:
                self.printer_state[obj] = items
        
        print_stats = self.printer_state["print_stats"]
        display_status = self.printer_state["display_status"]
        virtual_sdcard = self.printer_state["virtual_sdcard"]
        self.current_job_name = print_stats["filename"]
        self.current_progress = int(virtual_sdcard["progress"] * 100)
        self.current_time_passed = print_stats["print_duration"]
        new_state = print_stats["state"]

        try:
            self.total_print_time =  self.current_time_passed / virtual_sdcard["progress"]
            self.current_eta = self.total_print_time - self.current_time_passed
        except:
            self.total_print_time = 0
            self.current_eta = 0

        # Switch logic for handeling state changes.
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state
            if self.current_state == "printing":
                if old_state == "paused":
                    if self.notify_print_paused:
                        self._handle_resumed_state()
                else :
                    if self.notify_print_started:
                        self._handle_printing_state()
            if self.current_state == "standby":
                if old_state == "printing" or old_state == "paused":
                    if self.notify_print_cancelled:
                        self._handle_cancel_state()
            if self.current_state == "complete" and self.notify_print_completed:
                self._handle_complete_state()
            if self.current_state == "paused" and self.notify_print_paused:
                self._handle_paused_state()
            if self.current_state == "error" and self.notify_print_failed:
                self.error_message = print_stats["message"]
                self._handle_error_state()
        else:
            self.current_state = new_state
        
        # If progress has changed and exceeds or is equal to set threshold
        # Notify the user
        if self.current_progress != 0 and self.current_progress != self.last_progress:
            if self.current_progress - self.last_progress >= self.notify_update_interval:
                self.last_progress = self.current_progress
                self._handle_progression()

    def _handle_printing_state(self):
        payload = self._create_payload("PrintStarted")
        self._call_notification_endpoint(payload)

    def _handle_standby_state(self):
        payload = self._create_payload("Standby")
        self._call_notification_endpoint(payload)

    def _handle_progression(self):
        payload = self._create_payload("PrintProgress")
        self._call_notification_endpoint(payload)

    def _handle_paused_state(self):
        payload = self._create_payload("PrintPaused")
        self._call_notification_endpoint(payload)

    def _handle_resumed_state(self):
        payload = self._create_payload("PrintResumed")
        self._call_notification_endpoint(payload)

    def _handle_complete_state(self):
        payload = self._create_payload("PrintDone")
        self._call_notification_endpoint(payload)
    
    def _handle_cancel_state(self):
        payload = self._create_payload("PrintCancelled")
        self._call_notification_endpoint(payload)

    def _handle_error_state(self):
        # Abbuse job name to also show error message in the notification
        self.current_job_name = self.current_job_name + ": " + self.error_message
        payload = self._create_payload("PrintFailed")
        self._call_notification_endpoint(payload)

    def _create_payload(self, event):
        # Creates the payload which will be handled by Amazon AWS Lambda Function
        pl =  {
            "id" : str(uuid.uuid4()),
            "token" : self.push_token,
            "event": event,
            "printer": self.machine_name,
            "currenttime" : self.current_time_passed,
            "timeleft": self.current_eta,
            "percent" : int(self.current_progress),
            "print": self.current_job_name
        }
        return pl
    
    def _call_notification_endpoint(self, payload): 
        # Call notification endpoint that will result in a notification
        logging.info("Calling notification endpoint")
        http_client = AsyncHTTPClient()
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(payload)
        response =  http_client.fetch(self.notify_endpoint,
                                        raise_error=True,
                                        method='POST',
                                        body=json_data,
                                        headers=headers)


    

def load_component(config):
    return Geeks3D(config)
