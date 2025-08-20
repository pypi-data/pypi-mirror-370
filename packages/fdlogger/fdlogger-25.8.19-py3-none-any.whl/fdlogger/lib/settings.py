"""Settings Dialog Class"""

import logging
import os
import pkgutil
from json import dumps, loads
from PyQt5 import QtWidgets, uic


class Settings(QtWidgets.QDialog):
    """Settings dialog"""

    def __init__(self, parent=None):
        """initialize dialog"""
        super().__init__(parent)
        self.logger = logging.getLogger("__name__")
        self.working_path = os.path.dirname(
            pkgutil.get_loader("fdlogger").get_filename()
        )
        data_path = self.working_path + "/data/settings.ui"
        uic.loadUi(data_path, self)
        self.buttonBox.accepted.connect(self.save_changes)
        self.preference = None
        self.setup()

    def setup(self):
        """setup dialog"""
        with open("./fd_preferences.json", "rt", encoding="utf-8") as file_descriptor:
            self.preference = loads(file_descriptor.read())
            self.logger.info("reading: %s", self.preference)
            self.useqrz_radioButton.setChecked(bool(self.preference.get("useqrz")))
            self.usehamdb_radioButton.setChecked(bool(self.preference.get("usehamdb")))
            self.usehamqth_radioButton.setChecked(
                bool(self.preference.get("usehamqth"))
            )
            self.lookup_user_name_field.setText(
                str(self.preference.get("lookupusername", ""))
            )
            self.lookup_password_field.setText(
                str(self.preference.get("lookuppassword", ""))
            )
            self.cloudlogapi_field.setText(str(self.preference.get("cloudlogapi", "")))
            self.cloudlogurl_field.setText(str(self.preference.get("cloudlogurl", "")))
            self.rigcontrolip_field.setText(str(self.preference.get("CAT_ip", "")))
            self.rigcontrolport_field.setText(str(self.preference.get("CAT_port", "")))
            self.usecloudlog_checkBox.setChecked(bool(self.preference.get("cloudlog")))
            self.userigctld_radioButton.setChecked(
                bool(self.preference.get("userigctld"))
            )
            self.useflrig_radioButton.setChecked(bool(self.preference.get("useflrig")))
            self.markerfile_field.setText(str(self.preference.get("markerfile", "")))
            self.generatemarker_checkbox.setChecked(
                bool(self.preference.get("usemarker"))
            )
            self.cwip_field.setText(str(self.preference.get("cwip", "")))
            self.cwport_field.setText(str(self.preference.get("cwport", "")))
            self.usecwdaemon_radioButton.setChecked(
                bool(self.preference.get("cwtype") == 1)
            )
            self.usepywinkeyer_radioButton.setChecked(
                bool(self.preference.get("cwtype") == 2)
            )
            self.usecat4cw_radioButton.setChecked(
                bool(self.preference.get("cwtype") == 3)
            )
            self.connect_to_server.setChecked(bool(self.preference.get("useserver")))
            self.multicast_group.setText(
                str(self.preference.get("multicast_group", ""))
            )
            self.multicast_port.setText(str(self.preference.get("multicast_port", "")))
            self.interface_ip.setText(str(self.preference.get("interface_ip", "")))

            self.send_n1mm_packets.setChecked(
                bool(self.preference.get("send_n1mm_packets"))
            )
            self.n1mm_station_name.setText(
                str(self.preference.get("n1mm_station_name", ""))
            )
            self.n1mm_operator.setText(str(self.preference.get("n1mm_operator", "")))
            self.n1mm_ip.setText(str(self.preference.get("n1mm_ip", "")))
            self.n1mm_radioport.setText(str(self.preference.get("n1mm_radioport", "")))
            self.n1mm_contactport.setText(
                str(self.preference.get("n1mm_contactport", ""))
            )
            self.n1mm_lookupport.setText(
                str(self.preference.get("n1mm_lookupport", ""))
            )
            self.n1mm_scoreport.setText(str(self.preference.get("n1mm_scoreport", "")))

    def save_changes(self):
        """
        Write preferences to json file.
        """

        self.preference["useqrz"] = self.useqrz_radioButton.isChecked()
        self.preference["usehamdb"] = self.usehamdb_radioButton.isChecked()
        self.preference["usehamqth"] = self.usehamqth_radioButton.isChecked()
        self.preference["lookupusername"] = self.lookup_user_name_field.text()
        self.preference["lookuppassword"] = self.lookup_password_field.text()
        self.preference["cloudlog"] = self.usecloudlog_checkBox.isChecked()
        self.preference["cloudlogapi"] = self.cloudlogapi_field.text()
        self.preference["cloudlogurl"] = self.cloudlogurl_field.text()
        self.preference["CAT_ip"] = self.rigcontrolip_field.text()
        self.preference["CAT_port"] = int(self.rigcontrolport_field.text())
        self.preference["userigctld"] = self.userigctld_radioButton.isChecked()
        self.preference["useflrig"] = self.useflrig_radioButton.isChecked()
        self.preference["markerfile"] = self.markerfile_field.text()
        self.preference["usemarker"] = self.generatemarker_checkbox.isChecked()
        self.preference["cwip"] = self.cwip_field.text()
        self.preference["cwport"] = int(self.cwport_field.text())
        self.preference["cwtype"] = 0
        if self.usecwdaemon_radioButton.isChecked():
            self.preference["cwtype"] = 1
        if self.usepywinkeyer_radioButton.isChecked():
            self.preference["cwtype"] = 2
        if self.usecat4cw_radioButton.isChecked():
            self.preference["cwtype"] = 3
        self.preference["useserver"] = self.connect_to_server.isChecked()
        self.preference["multicast_group"] = self.multicast_group.text()
        self.preference["multicast_port"] = self.multicast_port.text()
        self.preference["interface_ip"] = self.interface_ip.text()

        self.preference["send_n1mm_packets"] = self.send_n1mm_packets.isChecked()
        self.preference["n1mm_station_name"] = self.n1mm_station_name.text()
        self.preference["n1mm_operator"] = self.n1mm_operator.text()
        self.preference["n1mm_ip"] = self.n1mm_ip.text()
        self.preference["n1mm_radioport"] = self.n1mm_radioport.text()
        self.preference["n1mm_contactport"] = self.n1mm_contactport.text()
        self.preference["n1mm_lookupport"] = self.n1mm_lookupport.text()
        self.preference["n1mm_scoreport"] = self.n1mm_scoreport.text()

        try:
            self.logger.info("save_changes:")
            with open(
                "./fd_preferences.json", "wt", encoding="utf-8"
            ) as file_descriptor:
                file_descriptor.write(dumps(self.preference, indent=4))
                self.logger.info("writing: %s", self.preference)
        except IOError as exception:
            self.logger.critical("save_changes: %s", exception)
