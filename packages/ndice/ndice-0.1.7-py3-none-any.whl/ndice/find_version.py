from pathlib import Path


def find_version() -> str:
    file_path = Path(__file__)
    try:
        import importlib.metadata

        package_name = file_path.parent.name
        return importlib.metadata.version(package_name)
    except:
        try:
            import tomllib

            root = file_path.parents[2]
            pyproject_path = root / 'pyproject.toml'
            pyproject_toml = pyproject_path.read_text()
            pyproject = tomllib.loads(pyproject_toml)
            return pyproject['project']['version']
        except:
            return '0.0.0+unknown'


if __name__ == '__main__':
    print(find_version())
