#!/usr/bin/env python
"""CHIME/FRB Event Tracer API."""

import enum
import logging

import pymongo

# Setup
log = logging.getLogger(__name__)


class Status(enum.Enum):
    """Status enum."""

    complete = 1
    incomplete = 2
    not_required = 3


tsar_classification_stage = "tsar_classification"
baseband_callback_request_stage = "baseband_callback_request"
baseband_conversion_stage = "baseband_conversion"
data_registration_stage = "data_registration"
data_replication_to_minoc_stage = "data_replication_to_minoc"


site_pipeline_stages = [
    baseband_callback_request_stage,
    baseband_conversion_stage,
    data_registration_stage,
    data_replication_to_minoc_stage,
]

sites = ["chime", "kko", "gbo", "hco"]


class TraceUpdater:
    """CHIME/FRB Trace Updater API."""

    def __init__(self, event_no, site, db_host=""):
        """Initialize Trace Updater API. Needs event number.

        Args:
            event_no: CHIME/FRB Event number
            site: Site at which we are call this.
            db_host: MongoDB host to connect to if at all.
                     If not provided, we will use REST api.
                     Connecting to database directly will be more robust.
        """
        assert site in sites
        self.site = site
        self.event_no = int(event_no)
        self.db = None
        if db_host:
            client = pymongo.MongoClient(host=db_host, port=27017)
            self.db = client.frb_master

    def create_trace(self, tsar_classification_needed=False):
        """Create a new trace.

        Args:
            tsar_classification_needed: Is tsar classifiation required for this event.
        """
        if self.db.trace.find_one({"event_no": self.event_no}) is not None:
            log.error(f"Found existing trace for the event {self.event_no}.")
            return
        trace = {"event_no": self.event_no}
        s = (
            Status.not_required
            if tsar_classification_needed is False
            else Status.incomplete
        )
        trace[self.__generate_common_key(tsar_classification_stage)] = s.name

        for site in sites:
            for stage in site_pipeline_stages:
                key = self.__generate_site_key(stage, site)
                trace[key] = Status.incomplete.name
        self.db.trace.insert_one(trace)

    def set_tsar_classification_complete(self):
        """Sets tsar classification stage as complete."""
        if self.db.trace.find_one({"event_no": self.event_no}) is None:
            log.error(
                f"Could not find existing trace for the event {self.event_no}."
            )
            return
        trace = {}  # noqa: F841
        key = self.__generate_common_key(tsar_classification_stage)
        self.db.trace.find_one_and_update(
            {"event_no": self.event_no}, {"$set": {key: Status.complete.name}}
        )

    def set_baseband_callback_request_complete(self):
        """Sets baseband callback request as complete."""
        self.__update_trace_via_direct_db(
            baseband_callback_request_stage, Status.complete
        )

    def set_baseband_conversion_complete(self):
        """Sets baseband conversion as complete."""
        self.__update_trace_via_direct_db(
            baseband_conversion_stage, Status.complete
        )

    def set_data_registration_complete(self):
        """Sets data registration as complete."""
        self.__update_trace_via_direct_db(
            data_registration_stage, Status.complete
        )

    def set_data_replication_to_minoc_complete(self):
        """Sets data replication to minoc as complete."""
        self.__update_trace_via_direct_db(
            data_replication_to_minoc_stage, Status.complete
        )

    def __generate_common_key(self, stage):
        """Generates common key."""
        assert stage != ""
        return f"stages/{stage}"

    def __generate_site_key(self, stage, site):
        """Generates site key."""
        assert stage != ""
        assert stage in site_pipeline_stages
        return f"stages/{stage}/sites/{site}"

    def __update_trace_via_direct_db(self, stage, status):
        """Updates the trace.

        Args:
            stage: Stage to update for the trace.
        """
        if self.db.trace.find_one({"event_no": self.event_no}) is None:
            log.error(
                f"Could not find existing trace for the event {self.event_no}."
            )
            return
        trace = {}  # noqa: F841
        assert stage in site_pipeline_stages
        key = self.__generate_site_key(stage, self.site)
        self.db.trace.find_one_and_update(
            {"event_no": self.event_no}, {"$set": {key: status.name}}
        )
