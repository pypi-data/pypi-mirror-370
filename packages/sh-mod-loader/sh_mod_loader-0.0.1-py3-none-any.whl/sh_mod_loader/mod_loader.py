import pkg_resources
import importlib
import os
from pathlib import Path
from typing import Callable


class ModLoadingException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidModException(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class DependencyError(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class ModIsNotExists(ModLoadingException):
    def __init__(self, *args):
        super().__init__(*args)


class DirectoryIsNotMod(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class PackageIsNotMod(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class ModNotImplementsInterface(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class ModNotHaveName(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class RequiredPackageNotExists(DependencyError):
    def __init__(self, *args):
        super().__init__(*args)


class RequiredModNotExists(DependencyError):
    def __init__(self, *args):
        super().__init__(*args)


class ModElementNotImplementsInterface(InvalidModException):
    def __init__(self, *args):
        super().__init__(*args)


class Mod:
    name: str
    title: str = "Untitled mod"
    version: str = "1.0.0"
    description: str = "Description is not provided."
    requires_mods: list[str] = []
    requires_packages: list[str] = []

    def __init__(self):
        pass

    def pre_load(self):
        pass

    def on_load(self):
        pass


class ModLoader:
    def load_python_package(path: str):
        print(f"Loading package '{path}'...")

    loaded_mods: list[Mod] = []
    mods_will_loaded: list[str] = []

    processors: dict[str, Callable[[str], None]] = {
        "python_packages": load_python_package
    }

    def __init__(self):
        pass

    def load_mod(self, path: str):
        if not os.path.exists(path):
            raise ModIsNotExists(f"Directory {path} is not exists")

        if not os.path.exists(f"{path}/mod.py"):
            raise DirectoryIsNotMod(
                f"Directory {path} is not mod because it is not contains 'mod.py'"
            )

        mod_package_dir = (
            os.path.relpath(path, start=os.path.curdir)
            .replace("/", ".")
            .replace("\\", ".")
        )

        print(f"Mod package dir: {mod_package_dir}")
        mod_module = importlib.import_module(".mod", mod_package_dir)

        if not hasattr(mod_module, "init"):
            raise PackageIsNotMod(
                f"Package '{mod_package_dir}' not implements mod package interface"
            )

        mod: Mod = mod_module.init()

        if not isinstance(mod, Mod):
            raise ModNotImplementsInterface(f"Mod is not implements interface")

        if not hasattr(mod, "name"):
            raise ModNotHaveName(f"Mod '{mod_package_dir}' not have name")

        for required_mod in mod.requires_mods:
            if required_mod not in self.mods_will_loaded:
                raise RequiredModNotExists(
                    f"Required mod '{required_mod}' is not installed. Installed mods: {self.mods_will_loaded}"
                )

        installed_packages = [package.key for package in pkg_resources.working_set]
        for required_package in mod.requires_packages:
            if required_package not in installed_packages:
                raise RequiredPackageNotExists(
                    f"Required package '{required_package}' is not installed. Installed packages: {installed_packages}"
                )

        self.loaded_mods.append(mod)
        mod.pre_load()

        for element_type_dir in os.scandir(path):
            if os.path.isdir(element_type_dir):
                if not element_type_dir.name.startswith("."):
                    if element_type_dir.name in self.processors:
                        for element_dir in os.scandir(element_type_dir):
                            if os.path.isdir(element_dir):
                                self.processors[element_type_dir.name](element_dir.name)

        mod.on_load()
