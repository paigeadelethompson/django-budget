import tomllib
import pathlib
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from pytz import common_timezones


class secret_key_not_configured():
    def __init(self):
        pass

    def __str__(self):
        raise Exception("Secret key not set")


class configurator():
    def default_logging(self):
        log = self.create_dir_if_not_exists(self.get_dot_directory() / "log") / "general.log"
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'standard': {
                    'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    'datefmt': "%d/%b/%Y %H:%M:%S"
                },
            },
            'handlers': {
                'logfile': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': log,
                    'maxBytes': 10240,
                    'backupCount': 3,
                    'formatter': 'standard',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['console'],
                    'propagate': True,
                    'level': 'INFO',
                },
                'django.db.backends': {
                    'handlers': ['console'],
                    'level': 'INFO',
                    'propagate': False,
                },
                '': {
                    'handlers': ['console', 'logfile'],
                    'level': 'DEBUG',
                },
            }
        }

    def default_database(self):
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': self.get_dot_directory() / 'db.sqlite3',
            }
        }

    def default_language_code(self):
        return 'en'

    def default_auto_field(self):
        return 'django.db.models.BigAutoField'

    def default_timezone(self):
        return 'UTC'

    def common_timezones(self):
        return [(tz, tz) for tz in common_timezones]

    def get_project_root(self):
        return Path(__file__).resolve().parent.parent

    def get_metadata_file(self):
        return self.get_project_root() / "pyproject.linked.toml"

    def __init__(self, touch_files=True):
        if pathlib.Path.exists(self.get_metadata_file()):
            data = tomllib.load(open(self.get_metadata_file(), 'rb')).get('tool').get('poetry')
            self.name = data.get('name')
            self.version = data.get('version')
            self.dot_directory = pathlib.Path.home() / ".{}".format(self.name)
            if Path.exists(self.dot_directory):
                pass
            else:
                pathlib.Path.mkdir(self.dot_directory)
                pathlib.Path.touch(self.dot_directory / "settings.py")
                open(self.dot_directory / "settings.py", 'w').writelines([
                    "SECRET_KEY='{}'\n".format(str(self.get_random_secret_key()))])
        else:
            raise Exception("error loading package metadata {}".format(self.get_metadata_file()))

    def get_version(self):
        if self.version is None:
            raise Exception("error loading package metadata")
        return self.version

    def get_name(self):
        if self.name is None:
            raise Exception("error loading package metadata")
        return self.name

    def get_dot_directory(self):
        if self.dot_directory is None or not pathlib.Path.exists(self.dot_directory):
            raise Exception("error loading package metadata")
        return self.dot_directory

    def get_random_secret_key(self):
        return get_random_secret_key()

    def create_dir_if_not_exists(self, check_path: Path, mode=511):
        if check_path.exists():
            return check_path
        else:
            print("creating directory {}".format(check_path))
            check_path.mkdir(parents=True, mode=mode)
            return check_path
