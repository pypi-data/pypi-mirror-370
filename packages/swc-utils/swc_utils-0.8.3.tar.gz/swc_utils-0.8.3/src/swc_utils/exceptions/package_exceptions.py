class MissingDependencyError(Exception):
    """Exception raised when a required dependency is missing."""

    def __init__(self, package_name: str or list[str], alt_source: str = None):
        self.package_name = package_name
        super().__init__(f"Missing required dependenc{'y' if isinstance(package_name, str) else 'ies'}: {package_name}. \n "
                         f"Please install {'it' if isinstance(package_name, str) else 'them'} using 'pip install "
                         f"{package_name if isinstance(package_name, str) else ' '.join(package_name)}' "
                         f"or 'pip 'install swc_utils[{alt_source or 'extras'}]'.")
