# APP_VERSION contains the app's current version.
APP_VERSION = '2.1.9'

# DB_VERSION contains the version of the database schema. The app stores the
# version used to create the cache database in the data folder. If the content
# of DB_VERSION has changed since the last run, the database file is deleted
# and recreated to avoid problems with outdated database schemas. As it's just
# a cache database and I don't want to bother with schema upgrades, I think
# this is the simplest way.
DB_VERSION = '2025-04-16'
