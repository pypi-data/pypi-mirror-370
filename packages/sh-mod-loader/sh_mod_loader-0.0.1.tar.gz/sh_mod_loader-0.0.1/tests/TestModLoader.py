import unittest
import sh_mod_loader.mod_loader


class TestModLoader(unittest.TestCase):
    def test_mod_is_not_exists(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.ModIsNotExists,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("non_existent_dir"),
        )

    def test_directory_is_not_mod(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.DirectoryIsNotMod,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_0"),
        )

    def test_mod_package_not_implements_interface(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.PackageIsNotMod,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_1"),
        )

    def test_mod_not_implements_interface(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.ModNotImplementsInterface,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_2"),
        )

    def test_mod_not_has_name(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.ModNotHaveName,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_3"),
        )

    def test_required_mod_not_installed(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.RequiredModNotExists,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_4"),
        )

    def test_required_package_not_installed(self):
        self.assertRaises(
            sh_mod_loader.mod_loader.RequiredPackageNotExists,
            lambda: sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_5"),
        )

    def test_required_package_installed(self):
        sh_mod_loader.mod_loader.ModLoader().load_mod("tests/test_mod_6")

    def test_required_mod_installed(self):
        mod_loader = sh_mod_loader.mod_loader.ModLoader()
        mod_loader.mods_will_loaded = ["test_dependency"]
        mod_loader.load_mod("tests/test_mod_7")

    def test_element_loading(self):
        mod_loader = sh_mod_loader.mod_loader.ModLoader()
        mod_loader.load_mod("tests/test_mod_8")
