from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures as MySQLDatabaseFeatures


class DatabaseFeatures(MySQLDatabaseFeatures):
    can_return_columns_from_insert = False
    can_return_rows_from_bulk_insert = False


class DatabaseWrapper(MySQLDatabaseWrapper):
    """Temporary compatibility backend for MariaDB 10.4 on Django 6."""

    features_class = DatabaseFeatures

    def check_database_version_supported(self):
        # Skip Django's hard minimum-version check to allow local MariaDB 10.4.
        return
