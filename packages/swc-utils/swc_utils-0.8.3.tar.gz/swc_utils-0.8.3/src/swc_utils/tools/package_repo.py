import os
from importlib.metadata import version


def check_package_version_requirements(working_dir: str, requirements_file: str, exit_on_fail: bool = True):
    """
    Check if the installed packages are at the required version. Check is done by comparing the installed version with
    the version specified in the requirements file. If the installed version is not the same as the required version,
    the function will print an error message and exit the program if exit_on_fail is set to True.
    Requirement entries that start with '#' are ignored.
    Requirement entries that do not contain '==' are ignored, as such entries with valid version ranges are skipped.
    :param working_dir: The directory where the requirements file is located.
    :param requirements_file: The name of the requirements file.
    :param exit_on_fail: If set to True, the function will exit the program if a package is not at the required version.
    :return:
    """
    with open(os.path.join(working_dir, requirements_file)) as f:
        requirements = f.readlines()

    for requirement in requirements:
        if requirement.startswith("#") or requirement == "\n" or requirement == "" or "==" not in requirement:
            continue

        package_name, package_version = requirement.split("==")
        package_version = package_version.strip()

        try:
            installed_version = version(package_name)

            if installed_version != package_version:
                print(f"Package '{package_name}' is not at the required version! Should be: '{package_version}' but is '{installed_version}'.")
                if exit_on_fail:
                    exit(1)

        except Exception as e:
            print(e)
            print(f"Package {package_name} is not installed.")
            if exit_on_fail:
                exit(1)
