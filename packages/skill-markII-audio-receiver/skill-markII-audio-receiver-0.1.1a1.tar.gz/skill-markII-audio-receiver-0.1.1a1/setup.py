#!/usr/bin/env python3
from os import walk, path
from setuptools import setup


BASEDIR = path.abspath(path.dirname(__file__))
URL = "https://github.com/NeonGeckoCom/skill-mark2-audio-receiver"
SKILL_CLAZZ = "MarkIIAudioReceiverSkill"  # needs to match __init__.py class name
PYPI_NAME = "skill-markII-audio-receiver"  # pip install PYPI_NAME

# below derived from github url to ensure standard skill_id
SKILL_AUTHOR, SKILL_NAME = URL.split(".com/")[-1].split("/")
SKILL_PKG = "skill_markII_audio_receiver"
PLUGIN_ENTRY_POINT = f"{SKILL_NAME.lower()}.{SKILL_AUTHOR.lower()}={SKILL_PKG}:{SKILL_CLAZZ}"
# skill_id=package_name:SkillClass
BASE_PATH = path.abspath(path.join(path.dirname(__file__), "skill_markII_audio_receiver"))


def get_version():
    """Find the version of the package"""
    version = None
    version_file = path.join(BASE_PATH, "version.py")
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if "VERSION_MAJOR" in line:
                major = line.split("=")[1].strip()
            elif "VERSION_MINOR" in line:
                minor = line.split("=")[1].strip()
            elif "VERSION_BUILD" in line:
                build = line.split("=")[1].strip()
            elif "VERSION_ALPHA" in line:
                alpha = line.split("=")[1].strip()

            if (major and minor and build and alpha) or "# END_VERSION_BLOCK" in line:
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def get_requirements(requirements_filename: str):
    requirements_file = path.join(path.dirname(__file__), requirements_filename)
    with open(requirements_file, "r", encoding="utf-8") as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
    return requirements


def find_resource_files():
    resource_base_dirs = ("locale", "intents", "dialog", "vocab", "regex", "ui")
    package_data = ["*.json"]
    for res in resource_base_dirs:
        if path.isdir(path.join(BASE_PATH, res)):
            for directory, _, files in walk(path.join(BASE_PATH, res)):
                if files:
                    package_data.append(path.join(directory.replace(BASE_PATH, "").lstrip("/"), "*"))
    return package_data


with open(path.join(path.dirname(__file__), "README.md"), "r") as f:
    long_description = f.read()

setup(
    name=PYPI_NAME,
    version=get_version(),
    description="Neon.AI Mark 2 Skill for Audio Receiving - Bluetooth, Airplay, KDE Connect, Raspotify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    author="Mike Gray",
    author_email="mike@graywind.org",
    license_files=["LICENSE.md"],
    package_dir={SKILL_PKG: "skill_markII_audio_receiver"},
    package_data={SKILL_PKG: find_resource_files()},
    packages=[SKILL_PKG],
    include_package_data=True,
    install_requires=get_requirements("requirements.txt"),
    keywords="Neon devicecontrol spotify kdeconnect airplay bluetooth mark2 audio cast",
    entry_points={"ovos.plugin.skill": PLUGIN_ENTRY_POINT},
)
