# skill-mark2-audio-receiver

## About

This skill enables voice intents for the following audio receiver options on the Mycroft Mark 2 device:

- Airplay (via [UxPlay](https://github.com/FDH2/UxPlay))
- [KDE Connect](https://kdeconnect.kde.org/)
- Spotify (via [Raspotify](https://dtcooper.github.io/raspotify/))
- Bluetooth

It allows you to:

- Get the status of any of these services on the Mark 2
- Enable/disable the services
- Rename your devices in Airplay/Raspotify
- Pair Bluetooth/KDE Connect with other devices

Supported in Neon versions after mid-August (TODO: Specific version when it's available)

Requires [neon-phal-plugin-audio-receiver](https://github.com/NeonGeckoCom/neon-phal-plugin-audio-receiver), an admin PHAL plugin that handles the portions of the code that require `sudo`.

## Examples

- "Is bluetooth enabled?"
- "Is airplay enabled?"
- "Is Spotify enabled?"
- "Is KDE Connect enabled?"
- "Disable airplay"
- "Deactivate bluetooth"
- "Enable KDE Connect"
- "Activate Spotify"
- "Rename Airplay device"
- "Rename Spotify device"
- "Pair Bluetooth"
- "Pair KDE Connect"

## Credits

[Mike Gray](mike@graywind.org)

## Category

Device Control

## Tags

#Neon #devicecontrol #spotify #kdeconnect #airplay #bluetooth #mark2 #audio #cast
