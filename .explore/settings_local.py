import os
import json
import subprocess
from arcwebbase.settings import *
from configparser import ConfigParser
from os.path import exists as file_exists
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
import saml2

BASEDIR = os.environ.get("BASEDIR", "/var/lib/arcadia")
if not os.path.isdir(BASEDIR):
  os.makedirs(BASEDIR)

DEBUG = False
RUN_FROM_SOURCE_DEBUG = True
ALLOWED_HOSTS = ['*']

if os.getenv('PHANTOMJS_PATH'):
  PHANTOMJS_PATH = os.getenv('PHANTOMJS_PATH')

cdv_mode = os.getenv('CDV_MODE')
if cdv_mode == "cdw":
  if os.getenv('CDV_SUB_MODE') == 'C1C':
    # C1C specific settings
    # - permit thumbnail fetched without auth
    ALLOW_THUMBNAIL_GET_WITHOUT_AUTH = True

    HTTP_HEADERNAME_FOR_TRUSTED_AUTH = "HTTP_X_C1C_ACTOR_USERNAME"



#### DEFAULT METASTORE CONFIGURATION FOR SQLITE IN CDSW / CML ####
metadata_store = os.getenv('METADATA_STORE')
# If the environment variable is set, let's check it for 'mysql', 'postgresql', or 'oracle' values.
#   If a valid external database backend isn't provided, continue with using SQLite database.
if metadata_store not in ('mysql', 'postgresql', 'oracle'):
  dbfile = os.getenv('DJANGO_DBFILE')
  if dbfile:
    DATABASES['default']['NAME'] = dbfile
  else:
    DATABASES['default']['NAME'] = os.path.join(BASEDIR, "arcviz.db")


#### START CDW VIZ METASTORE CONFIGURATION ####
def wait_for_pg(host, port):
  import socket
  import os
  import time

  port = int(port)

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print("Waiting for PG to be active on %s:%s" % (host, port))
  while True:
    try:
      s.connect((host, port))
      s.close()
      print("PG active")
      break
    except socket.error as ex:
      time.sleep(0.1)

# On C1C we overwrite the zviz.ini file zremote_rdsdb.ini se we have to check
# them in a priorty order if they exist
K8SCONFIGMAP_CDW = "/etc/viz/conf/zviz.ini"
K8SCONFIGMAP_C1C = "/etc/viz/conf/zremote_rdsdb.ini"

K8SCONFIGMAP_FILES_BY_PRIO = [
    K8SCONFIGMAP_C1C,
    K8SCONFIGMAP_CDW
]

k8sConfigMap = None
for file in K8SCONFIGMAP_FILES_BY_PRIO:
    if not file_exists(file):
        continue
    k8sConfigMap = file

EXTERNAL_DB_CONFIG = {}
if k8sConfigMap:
    config = ConfigParser()
    config.read(k8sConfigMap)
    if "database" in config:
        dbconfig = config["database"]
        if dbconfig.get("engine") == "postgres":
            print("Using postgres backend from k8s config")
            EXTERNAL_DB_CONFIG['ENGINE'] = "django.db.backends.postgresql"
            EXTERNAL_DB_CONFIG['NAME'] = dbconfig['name']
            EXTERNAL_DB_CONFIG['USER'] = dbconfig['user']
            EXTERNAL_DB_CONFIG['PASSWORD'] = dbconfig['password']
            EXTERNAL_DB_CONFIG['HOST'] = dbconfig['host']
            EXTERNAL_DB_CONFIG['PORT'] = dbconfig['port']
            EXTERNAL_DB_CONFIG['CONN_MAX_AGE'] = 600
            wait_for_pg(EXTERNAL_DB_CONFIG['HOST'], EXTERNAL_DB_CONFIG['PORT'])

# TODO: Check if this deprecated with the CDSW / CML Settings below
if os.environ.get('DJANGO_POSTGRES_ENABLED'):
  print("Using postgres backend from env config")
  EXTERNAL_DB_CONFIG['ENGINE'] = "django.db.backends.postgresql"
  EXTERNAL_DB_CONFIG['NAME'] = os.environ.get('POSTGRES_DB')
  EXTERNAL_DB_CONFIG['USER'] = os.environ.get('POSTGRES_USER')
  EXTERNAL_DB_CONFIG['PASSWORD'] = os.environ.get('POSTGRES_PASSWORD')
  EXTERNAL_DB_CONFIG['HOST'] = os.environ.get('POSTGRES_HOST')
  EXTERNAL_DB_CONFIG['PORT'] = os.environ.get('POSTGRES_PORT')
  wait_for_pg(EXTERNAL_DB_CONFIG['HOST'], EXTERNAL_DB_CONFIG['PORT'])

DATABASES["default"].update(EXTERNAL_DB_CONFIG)
#### END CDW VIZ METASTORE CONFIGURATION ####


CACHES = {
  'default': {
    # To disable caching
    #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
     'BACKEND': 'vizlib.arcfilecache.FileBasedCache',
     'LOCATION': os.path.join(BASEDIR,'django_cache'),
     'TIMEOUT': 31536000,
     'OPTIONS': {
       'MAX_ENTRIES': 10000
     }
  }
}

INSTALLED_APPS = INSTALLED_APPS + ('trustedauth',)
AUTHENTICATION_BACKENDS = (
  'django.contrib.auth.backends.ModelBackend',
)

####### START VIZ LDAP CONFIG #######

K8SLDAPCONFIGMAP = "/etc/viz/conf/ldap.ini"

if file_exists(K8SLDAPCONFIGMAP):
    # Disable local user creation when LDAP is configured
    ENABLE_USER_CREATE = False

    print("Setting up LDAP")
    config = ConfigParser()
    config.read(K8SLDAPCONFIGMAP)
    if 'auth' in config:
        authconfig = config['auth']
        if authconfig.get('backend') == 'desktop.auth.backend.LdapBackend':
            use_ldap = True

            if 'ldap' in config:
                ldapconfig = config['ldap']
                # LDAP server URI
                AUTH_LDAP_SERVER_URI = ldapconfig.get('ldap_url').strip('"')
                # TLS/SSL options
                AUTH_LDAP_START_TLS = ldapconfig.get('use_start_tls') == 'true'
                AUTH_LDAP_GLOBAL_OPTIONS = {
                    # ldap.OPT_X_TLS_CACERTFILE: "/etc/bla.cert",        # Point to CA Cert file
                    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,   # Disable cert checking
                }
                # Bind user
                AUTH_LDAP_BIND_DN = ldapconfig.get('bind_dn').strip('"')

                # support bind_password and bind_password_script in ldap.ini
                AUTH_LDAP_BIND_PASSWORD = ldapconfig.get('bind_password')
                if AUTH_LDAP_BIND_PASSWORD:
                  AUTH_LDAP_BIND_PASSWORD = AUTH_LDAP_BIND_PASSWORD.strip('"')
                else:
                  pwscript = ldapconfig.get('bind_password_script', '').strip().strip('"').strip()
                  if pwscript:
                    AUTH_LDAP_BIND_PASSWORD = subprocess.check_output(["bash", "-c", pwscript]).decode().strip()

                # Connection options
                AUTH_LDAP_CONNECTION_OPTIONS = {
                    ldap.OPT_DEBUG_LEVEL: 1,  # 0 to 255
                    ldap.OPT_REFERRALS: 0,  # For Active Directory
                }

                BASE_DN = ldapconfig.get('base_dn').strip('"')

                AUTH_LDAP_NO_NEW_USERS = ldapconfig.get('create_users_on_login', 'true') != "true"

                AUTHENTICATION_BACKENDS = (
                    'arcweb.arcwebbase.basebackends.VizBaseLDAPBackend',
                    'django.contrib.auth.backends.ModelBackend'
                )

                if 'users' in config:
                    userconfig = config['users']
                    # User config
                    AUTH_LDAP_USER_SEARCH = LDAPSearch(BASE_DN,
                                                       ldap.SCOPE_SUBTREE, "(" + userconfig.get('user_name_attr').strip('"') + "=%(user)s)")
                    # Map LDAP attributes to Django
                    AUTH_LDAP_USER_ATTR_MAP = {
                        "first_name": "givenName",
                        "last_name": "sn",
                        "email": "mail"
                    }

                if 'groups' in config:
                    groupconfig = config['groups']
                    # group config
                    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(BASE_DN,
                                                        ldap.SCOPE_SUBTREE, "(" + groupconfig.get('group_filter').strip('"') + ")")
                    # Group Settings
                    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr=groupconfig.get('group_name_attr').strip('"'),)
                    # AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
                    AUTH_LDAP_FIND_GROUP_PERMS = True
                    AUTH_LDAP_MIRROR_GROUPS = False

                    # Cache settings
                    # Note this may cause a delay when groups are changed in LDAP
                    AUTH_LDAP_CACHE_GROUPS = True
                    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300

####### END VIZ LDAP CONFIG #######


####### START VIZ SAML CONFIG #######

# Helper function to parse attribute maps that come from the saml.ini file generated with SSO configurations
def map_saml_attributes(attributes):
    # Expects a dictionary of key/value pairs from saml.ini
    #   Example: {'uid': 'username', 'first_name': 'first_name', 'last_name': 'last_name'}
    #
    # Returns: {'uid': ('username', ), 'givenName': ('first_name', ), 'sn': ('last_name', )}
    #
    saml_attributes_formatted = {}
    for k,v in attributes.items():
        saml_attributes_formatted[k] = (v,)
    return saml_attributes_formatted

K8SSAMLCONFIGMAP = "/etc/viz/conf/saml.ini"

if file_exists(K8SSAMLCONFIGMAP):
    #
    # Disable local user creation when SAML is configured
    ENABLE_USER_CREATE = False
    print("Setting up SAML")

    #
    # Initiate config parser to read saml.ini
    config = ConfigParser()
    config.read(K8SSAMLCONFIGMAP)

    #
    # djangosaml2 changes from Django 3.x upgrade
    idx = MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')
    MIDDLEWARE.insert(idx + 1, 'djangosaml2.middleware.SamlSessionMiddleware')
    SAML_SESSION_COOKIE_NAME = 'saml_session'  # default saml session cookie name
    # Session middleware will set SameSite=None. This attribute requires that the "Secure" attribute also be added.
    SESSION_COOKIE_SECURE = True
    # Set referrer policy to avoid CORS related issues when communicating with IDPs
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

    #
    # Check saml.ini for auth config block
    if 'auth' in config:
        authconfig = config['auth']

        ##
        ## TODO: Check if this if/else block is really required. Doesn't seem like we use this backend argument for anything
        ##
        if authconfig.get('backend') == 'libsaml.backend.SAML2Backend':
            use_saml = True

            #
            # Check saml.ini for libsaml config block
            if 'libsaml' in config:
                samlconfig = config['libsaml']

                #
                # Add djangosaml module and Saml2 backends to enable SAML auth
                INSTALLED_APPS += ('djangosaml2',)
                AUTHENTICATION_BACKENDS = (
                    # Commenting out ModelBackend will disable local login
                    'django.contrib.auth.backends.ModelBackend',
                    'arcweb.arcwebbase.basebackends.VizBaseSaml2Backend',
                )

                # Define SAML login and home url endpoints
                LOGIN_URL = samlconfig.get('login_url','/arc/saml2/login/')
                HOME_URL = samlconfig.get('home_url','/arc/apps/home')
                #
                # Specify if logouts from SAML will redirect to a logout page
                # For use with SAML or other federated auth
                USE_LOGOUT_PAGE = samlconfig.get('logout_enabled') == 'true'
                # Use the following setting to choose your preferred binding for SP initiated logout requests
                SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT if samlconfig.get('logout_request_preferred_binding') == 'saml2.BINDING_HTTP_REDIRECT' else saml2.BINDING_HTTP_POST
                if USE_LOGOUT_PAGE:
                    LOGOUT_REDIRECT_URL = samlconfig.get('logout_request_preferred_binding', samlconfig.get('base_url') + LOGIN_URL)
                #
                # Close session when browser closes/quits
                SESSION_EXPIRE_AT_BROWSER_CLOSE = samlconfig.get('session_expire_at_browser_close') == 'true'
                #
                # If user does not exist during login, create the User object
                SAML_CREATE_UNKNOWN_USER = samlconfig.get('create_unknown_user') == 'true'

                #
                # Require Group checks turned on by default with CDW
                SAML_REQUIRED_GROUPS_CHECK = True

                #
                # If Groups are being asserted via SAML, intercept the list of groups by using a group attribute name
                if samlconfig.get('required_groups_attribute', False):
                    SAML_GROUP_ATTRIBUTE_NAME = samlconfig.get('required_groups_attribute').strip('"') # 'ds_groups' used to be the default group attribute name
                SAML_USE_NAME_ID_AS_USERNAME = samlconfig.get('username_source') == 'nameid'
                if not SAML_USE_NAME_ID_AS_USERNAME:
                    SAML_DJANGO_USER_MAIN_ATTRIBUTE = samlconfig.get('username_source','nameid')
                #
                # Automatically create groups from SAML assertions, but ignore virtual groups generated by CDP Roles:
                #   Example: _c_cm_admins_1aa82c29, _c_nifi_admins_6d0cce4a, _c_ml_users_4cfa8d8d
                CDW_SAML_IGNORE_GROUP_PREFIXES = ["_c_"]
                SAML_CREATE_UNKNOWN_GROUP = samlconfig.get('create_unknown_group') == 'true'

                CDW_IMPALA_USERNAME = samlconfig.get('proxy_user_config', '')
                #
                # Define SAML assertion attribute mapping to Django User object fields
                # DEFAULT_SAML_ATTRIBUTE_MAPPING = {
                #  'uid': ('username', ),
                #  'givenName': ('first_name', ),
                #  'sn': ('last_name', ),
                # }

                SAML_ATTRIBUTE_MAPPING = map_saml_attributes(json.loads(samlconfig.get('user_attribute_mapping').strip("'")))

                # Groups
                # On the old version of CDW the required_groups and
                # required_admin_groups are not provided, to have backwards
                # compatibility we differentiate between no value and empty
                # list so no default values are provided here
                if samlconfig.get('required_groups', False):
                    SAML_REQUIRED_GROUPS = json.loads(samlconfig.get('required_groups').strip("'"))
                if samlconfig.get('required_admin_groups', False):
                    SAML_REQUIRED_ADMIN_GROUPS = json.loads(samlconfig.get('required_admin_groups').strip("'"))

                SAML_CONFIG = {
                  # full path to the xmlsec1 binary programm
                  'xmlsec_binary': samlconfig.get('xmlsec_binary', '/usr/bin/xmlsec1'),

                  # your entity id, usually your subdomain plus the url to the metadata view
                  'entityid': samlconfig.get('entity_id').strip('"'),
                  # directory with attribute mapping
                  'attribute_map_dir': samlconfig.get('attribute_map_dir', '/etc/viz/conf/saml/saml_attributes'),

                  # this block states what services we provide
                  'service': {
                    # we are just a lonely SP
                    'sp': {
                      'name': 'viz',
                      # Name ID Format Reference:
                      #     https://github.com/IdentityPython/pysaml2/blob/master/src/saml2/saml.py
                      'name_id_format': samlconfig.get('name_id_format', 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent').strip('"'),
                      'allow_unsolicited': samlconfig.get('allow_unsolicited') == 'true',
                      'logout_requests_signed': samlconfig.get('logout_requests_signed') == 'true',
                      'authn_requests_signed': samlconfig.get('authn_requests_signed') == 'true',
                      'want_response_signed': samlconfig.get('want_response_signed') == 'true',
                      'want_assertions_signed': samlconfig.get('want_assertions_signed') == 'true',
                      'endpoints': {
                        # url and binding to the assertion consumer service view
                        # do not change the binding or service name
                        'assertion_consumer_service': [
                          ('%s/arc/saml2/acs/' % samlconfig.get('base_url'), saml2.BINDING_HTTP_POST),
                        ],
                        # url and binding to the single logout service view
                        # do not change the binding or service name
                        'single_logout_service': [
                            ('%s/arc/saml2/ls/' % samlconfig.get('base_url'), saml2.BINDING_HTTP_REDIRECT),
                            ('%s/arc/saml2/ls/post/' % samlconfig.get('base_url'), saml2.BINDING_HTTP_POST),
                        ],
                      },

                      # attributes that this project need to identify a user
                      'required_attributes': samlconfig.get('required_attributes', ["uid"]).strip('][').replace("'","").split(","),

                      # attributes that may be useful to have but not required
                      'optional_attributes': samlconfig.get('optional_attributes', []).strip('][').replace("'","").split(","),
                    },
                  },
                  # Specify where the IDP metadata.xml file is stored
                  'metadata': {
                    'local': [samlconfig.get('metadata_file', '/etc/viz/conf/saml/idpmetadata.xml')],
                  },

                  # Set to 1 to output debugging information
                  'debug': 1,

                  # SSL Key/Certificate for signing SAML requests/responses
                  'key_file': samlconfig.get('key_file', '/etc/viz/conf/samlcert/server.key'),  # private part
                  'cert_file': samlconfig.get('cert_file', '/etc/viz/conf/samlcert/server.crt'),  # public part

                  'valid_for': 24,  # how long is our metadata valid
                }

####### END VIZ SAML CONFIG #######

AUDIT_LOGFILE = os.path.join(BASEDIR, "querylog")
AUDIT_FILE_MAXBYTES = 10*1024*1024
ARCENGINE_VALIDATE_ACCESS = False

if HTTP_HEADERNAME_FOR_TRUSTED_AUTH or cdv_mode in ["cml", "cdsw", "runtime"]:
  AUTHENTICATION_BACKENDS = (
    'arcweb.arcwebbase.basebackends.VizBaseRemoteBackend',
    'django.contrib.auth.backends.ModelBackend',
  )

  idx = MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')
  MIDDLEWARE.insert(idx + 1, 'arcwebbase.middleware.CustomHeaderMiddleware')

# Logging config
# Set the env variable "LOGGING_LEVEL" to control logging
# Specific loggers can be configured as well
# The default log level is INFO. If DEBUG is True then it DEBUG.
# The default output is console.
# The default filename for file output is /tmp/arcviz.log
DEFAULT_LOGGING_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL",DEFAULT_LOGGING_LEVEL)
LOGGING_LEVEL_ARCVIZ = os.environ.get("LOGGING_LEVEL_ARCVIZ", LOGGING_LEVEL)
LOGGING_LEVEL_DJANGO = os.environ.get("LOGGING_LEVEL_DJANGO", LOGGING_LEVEL)
LOGGING_LEVEL_DJANGO_REQUEST = os.environ.get("LOGGING_LEVEL_DJANGO_REQUEST", "WARNING")
LOGGING_LEVEL_DJANGO_DB = os.environ.get("LOGGING_LEVEL_DJANGO_DB", "WARNING")
LOGGING_LEVEL_LDAP = os.environ.get("LOGGING_LEVEL_LDAP", LOGGING_LEVEL)
#LOG_FILE = os.environ.get("LOG_FILE", "/tmp/arcviz.log")
LOG_FILE = os.path.join(BASEDIR,"arcviz.log")
# LOG_HANDLERS env var is comma separated list of handlers. "console" or "file"
LOG_HANDLERS = [ h.strip() for h in os.environ.get("LOG_HANDLERS", "console,file").split(',') ]

# Map the above into current logging configuration
ARCVIZ_LOGFILE = LOG_FILE
ARCVIZ_LOGLEVEL = LOGGING_LEVEL_ARCVIZ

if IS_MASTER and 'console' in LOG_HANDLERS:
  LOGGING['loggers']['arcweb']['handlers'].append('console')

if 'file' not in LOG_HANDLERS:
  ARCVIZ_LOGFILE = None

ADDITIONAL_LOGGERS.extend([('root', LOGGING_LEVEL),
                           ('django', LOGGING_LEVEL_DJANGO),
                           ('django.request', LOGGING_LEVEL_DJANGO_REQUEST),
                           ('django.db.backends', LOGGING_LEVEL_DJANGO_DB),
                           ('django_auth_ldap', LOGGING_LEVEL_LDAP)])

del BASEDIR
ADMIN_API_DEMO_LIST = ['*']
ADMIN_API_URL_LIST  = ['*']
DATA_API_ENABLED = True
ENABLE_DSREQ_PERF_DISPLAY = True
ENABLE_API_KEYS = True

ENABLE_VISUAL_ACTION = True
ENABLE_VISUAL_TIMELINE = True
ENABLE_WEBHOOK = True
ENABLE_TIMEWARP = True

# For testing
# CHROMIUM_PATH = "*"

ENABLE_APP_ACCELERATION = False

ENABLE_ADVANCED_SETTINGS = not (os.environ.get('NO_CUSTOM_SETTINGS') or \
  cdv_mode == 'cdw')

# To change the value of existent feature flippers, use the following syntax:
# FEATURE_FLIPPERS.append({'id': 'example_flipper',  'value': False})
