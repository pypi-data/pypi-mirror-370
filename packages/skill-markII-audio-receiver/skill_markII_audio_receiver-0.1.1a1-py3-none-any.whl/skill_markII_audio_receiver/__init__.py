"""Control various Audio Receiver options for Neon.AI Mark 2 Images."""
from typing import List
from subprocess import CalledProcessError

from ovos_bus_client import Message
from ovos_utils import classproperty
from ovos_utils.parse import fuzzy_match
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from skill_markII_audio_receiver.systemd import get_service_status


def read_file(file_path: str) -> List[str]:
    """
    Read and return the content of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        List[str]: List of strings with each string being a line from the file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def write_to_file(file_path: str, content: List[str]) -> None:
    """
    Write the updated content back to a file.

    Args:
        file_path (str): Path to the file.
        content (List[str]): List of strings to be written to the file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(content)


class MarkIIAudioReceiverSkill(OVOSSkill):
    """Skill to control Audio Receiver options for Neon.AI Mark 2 Images."""

    def __init__(self, *args, **kwargs):
        """The __init__ method is called when the Skill is first constructed.
        Note that self.bus, self.skill_id, self.settings, and
        other base class settings are only available after the call to super().
        """
        super().__init__(*args, **kwargs)
        self.renaming_airplay = False
        self.renaming_spotify = False

    def initialize(self):
        airplay_name = self.airplay_name
        self.log.info("Initializing Mark II Audio Receiver Skill with settings:")
        self.log.info(
            f"Renaming Raspotify device to settings value of {self.raspotify_name}"
        )
        self.bus.emit(
            Message(
                "neon.phal.plugin.audio.receiver.set.raspotify.name",
                {"name": self.raspotify_name},
                {"skill_id": self.skill_id},
            )
        )
        self.log.info(f"Renaming Airplay device to settings value of {airplay_name}")
        self.bus.emit(
            Message(
                "neon.phal.plugin.audio.receiver.set.uxplay.name",
                {"name": airplay_name},
                {"skill_id": self.skill_id},
            )
        )

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=True,
            gui_before_load=False,
            requires_internet=False,
            requires_network=True,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=False,
            no_gui_fallback=True,
        )

    @property
    def bluetooth_timeout(self):
        """Dynamically get the bluetooth_timeout from the skill settings file.
        If it doesn't exist, return the default value.
        This will reflect live changes to settings.json files (local or from backend)
        """
        return self.settings.get("bluetooth_timeout", 60)

    @property
    def kdeconnect_timeout(self):
        """Dynamically get the kdeconnect_timeout from the skill settings file.
        If it doesn't exist, return the default value.
        This will reflect live changes to settings.json files (local or from backend)
        """
        return self.settings.get("kdeconnect_timeout", 30)

    @property
    def raspotify_name(self):
        """Dynamically get the raspotify_name from the skill settings file.
        If it doesn't exist, return the default value.
        This will reflect live changes to settings.json files (local or from backend)
        """
        return self.settings.get("raspotify_name", "Neon Mark 2")

    @property
    def airplay_name(self):
        """Dynamically get the airplay_name from the skill settings file.
        If it doesn't exist, return the default value.
        This will reflect live changes to settings.json files (local or from backend)
        """
        # Note that the default is actually UxPlay@hostname, so for the config we default to ""
        # This is an override setting only
        return self.settings.get("airplay_name", "")

    @intent_handler("check-service-status.intent")
    def handle_check_service_status_intent(self, message) -> None:
        """Check if we have a certain service enabled."""
        service = ""
        status = ""
        transcription = message.data.get("utterance", "")
        try:
            if "bluetooth" in transcription or "blue tooth" in transcription:
                service = "bluetooth"
                status = "running" if get_service_status("bluetooth") else "not running"
            if fuzzy_match("kde connect", transcription) >= 0.8:
                service = "KDE connect"  # Since this is spoken
                status = (
                    "running" if get_service_status("kdeconnect") else "not running"
                )
            if "airplay" in transcription or "air play" in transcription:
                service = "airplay"
                status = "running" if get_service_status("uxplay") else "not running"
            if "spotify" in transcription:
                service = "spotify"
                status = "running" if get_service_status("raspotify") else "not running"
            if service and status:
                self.speak_dialog(
                    "service-status", data={"service": service, "status": status}
                )
            else:
                self.speak_dialog("unsure")
        except CalledProcessError:
            self.speak_dialog("trouble-checking-service", data={"service": service})
        except:
            self.speak_dialog("generic-error")

    # Enable services
    @intent_handler("disable-bluetooth.intent")
    def disable_bluetooth_intent(self, message: Message) -> None:
        """Handle intent to disable Bluetooth."""
        self._disable_service(
            service="bluetooth", spoken_service="bluetooth", message=message
        )

    @intent_handler("disable-airplay.intent")
    def disable_airplay_intent(self, message: Message) -> None:
        """Handle intent to disable Airplay (UxPlay service)."""
        self._disable_service(
            service="uxplay", spoken_service="airplay", message=message
        )

    @intent_handler("disable-kde-connect.intent")
    def disable_kde_connect_intent(self, message: Message) -> None:
        """Handle intent to disable KDE Connect."""
        self._disable_service(
            service="kdeconnect", spoken_service="KDE connect", message=message
        )

    @intent_handler("disable-spotify.intent")
    def disable_spotify_intent(self, message: Message) -> None:
        """Handle intent to disable Spotify."""
        self._disable_service(
            service="raspotify", spoken_service="spotify", message=message
        )

    # Enable services
    @intent_handler("enable-bluetooth.intent")
    def enable_bluetooth_intent(self, message: Message) -> None:
        """Handle intent to enable Bluetooth."""
        self._enable_service(
            service="bluetooth", spoken_service="bluetooth", message=message
        )

    @intent_handler("enable-airplay.intent")
    def enable_airplay_intent(self, message: Message) -> None:
        """Handle intent to enable Airplay (UxPlay service)."""
        self._enable_service(
            service="uxplay", spoken_service="airplay", message=message
        )

    @intent_handler("enable-kde-connect.intent")
    def enable_kde_connect_intent(self, message: Message) -> None:
        """Handle intent to enable KDE Connect."""
        self._enable_service(
            service="kdeconnect", spoken_service="KDE connect", message=message
        )

    @intent_handler("enable-spotify.intent")
    def enable_spotify_intent(self, message: Message) -> None:
        """Handle intent to enable Spotify (Raspotify service)."""
        self._enable_service(
            service="raspotify", spoken_service="spotify", message=message
        )

    # Rename devices in services
    @intent_handler("rename-airplay.intent")
    def rename_airplay_intent(self, message: Message) -> None:
        """Handle intent to rename the Airplay device."""
        self.renaming_airplay = True
        attempts = 0
        # TODO: Text box and keyboard for entry
        new_name, confirmation = self._get_new_device_name()
        if confirmation == "yes":
            try:
                self.renaming_airplay = False
                self.log.debug(f"Renaming Airplay device to {new_name}")
                message.forward(
                    "neon.phal.plugin.audio.receiver.set.uxplay.name",
                    {"name": new_name},
                )
                self.settings["airplay_name"] = new_name
                self.speak_dialog(
                    "renamed-device", data={"service": "airplay", "name": new_name}
                )
            except CalledProcessError:
                self.speak_dialog(
                    "trouble-renaming-device", data={"service": "airplay"}
                )
            except Exception as err:
                self.log.error(err)
                self.speak_dialog("generic-error")
        if confirmation == "no" and attempts <= 3:
            attempts += 1
            new_name, confirmation = self._get_new_device_name()
        if confirmation == "no" and attempts > 3:
            self.renaming_airplay = False
            self.speak_dialog("try-again-later")

    @intent_handler("rename-spotify.intent")
    def rename_spotify_intent(self, message: Message) -> None:
        """Handle intent to rename the Raspotify device advertised to Spotify Connect."""
        self.renaming_spotify = True
        attempts = 0
        # TODO: Text box and keyboard for entry
        new_name, confirmation = self._get_new_device_name()
        if confirmation == "yes":
            try:
                self.renaming_spotify = False
                self.log.debug(f"Renaming Raspotify device to {new_name}")
                message.forward(
                    "neon.phal.plugin.audio.receiver.set.raspotify.name",
                    {"name": new_name},
                )
                self.settings["raspotify_name"] = new_name
                self.speak_dialog(
                    "renamed-device", data={"service": "spotify", "name": new_name}
                )
            except CalledProcessError:
                self.speak_dialog(
                    "trouble-renaming-device", data={"service": "spotify"}
                )
            except Exception as err:
                self.log.error(err)
                self.speak_dialog("generic-error")
        if confirmation == "no" and attempts <= 3:
            attempts += 1
            new_name, confirmation = self._get_new_device_name()
        if confirmation == "no" and attempts > 3:
            self.renaming_airplay = False
            self.speak_dialog("try-again-later")

    @intent_handler("pair-bluetooth.intent")
    def pair_bluetooth_intent(self, message: Message) -> None:
        """Handle intent to pair the Mark 2 as a Bluetooth speaker."""
        if get_service_status("bluetooth") is True:
            timeout = self.bluetooth_timeout
            self.speak_dialog(
                "pairing", data={"service": "bluetooth", "timeout": timeout}
            )
            message.forward(
                "neon.phal.plugin.audio.receiver.pair.bluetooth",
                {"timeout": timeout},
            )
        else:
            self.speak_dialog(
                "service-status", data={"service": "bluetooth", "status": "disabled"}
            )

    @intent_handler("pair-kde-connect.intent")
    def pair_kde_connect_intent(self, message: Message) -> None:
        """Handle intent to pair the Mark 2 to available KDE Connect devices."""
        if get_service_status("kdeconnect") is True:
            timeout = self.kdeconnect_timeout
            self.speak_dialog(
                "pairing", data={"service": "KDE connect", "timeout": timeout}
            )
            message.forward(
                "neon.phal.plugin.audio.receiver.pair.kdeconnect",
                {"timeout": timeout},
            )
        else:
            self.speak_dialog(
                "service-status", data={"service": "KDE connect", "status": "disabled"}
            )

    def stop(self):
        """Optional action to take when "stop" is requested by the user.
        This method should return True if it stopped something or
        False (or None) otherwise.
        """
        if self.renaming_airplay is True:
            self.renaming_airplay = False
        if self.renaming_spotify is True:
            self.renaming_spotify = False

    # "Private" methods
    def _disable_service(self, service: str, spoken_service: str, message: Message):
        """Disable and stop a given systemd service, then speak confirmation to the user."""
        message.forward(
            "neon.phal.plugin.audio.receiver.disable.service",
            {"service": service},
        )
        message.forward(
            "neon.phal.plugin.audio.receiver.stop.service",
            {"service": service},
        )
        self.speak_dialog(
            "disabled-service", data={"service": spoken_service, "status": "disabled"}
        )

    def _enable_service(self, service: str, spoken_service: str, message: Message):
        """Enable and start a given systemd service, then speak confirmation to the user."""
        message.forward(
            "neon.phal.plugin.audio.receiver.enable.service",
            {"service": service},
        )
        message.forward(
            "neon.phal.plugin.audio.receiver.start.service",
            {"service": service},
        )
        self.speak_dialog(
            "enabled-service", data={"service": spoken_service, "status": "enabled"}
        )

    def _get_new_device_name(self):
        new_name = self.get_response("get-new-name")
        if self.gui and new_name:
            self.gui.show_text(new_name)
        confirmation = self.ask_yesno("confirm-new-name", data={"name": new_name})
        return new_name, confirmation
