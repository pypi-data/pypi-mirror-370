from nomnomdata.engine.components import Connection, Parameter, ParameterGroup
from nomnomdata.engine.parameters import (
    Boolean,
    Code,
    CodeDialectType,
    Enum,
    Int,
    Password,
    String,
    Text,
)

ADPConnection = Connection(
    alias="ADP API Credentials",
    description="Credentials to use to authenticate with ADP via the API.",
    connection_type_uuid="ADPLD-APITK",
    categories=["ADP"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="client_id",
                display_name="Client ID",
                description="Provided by ADP Partner Support.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="client_secret",
                display_name="Client Secret",
                description="Provided by ADP Partner Support.",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="cert",
                display_name="Certificate",
                description="Provided by ADP Partner Support in a .cer file.",
                type=Text(),
                required=True,
            ),
            Parameter(
                name="key",
                display_name="Private Key",
                description="Provided by ADP Partner Support in .key file.",
                type=Password(),
                required=True,
            ),
            name="adp_credentials",
            display_name="ADP Credentials",
        ),
    ],
)

ADPWebConnection = Connection(
    alias="ADP Web Credentials",
    description="Security information to use to authenticate with ADP via the web.",
    connection_type_uuid="ADPLD-WEBLG",
    categories=["ADP"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="user_id",
                display_name="User ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="security_questions",
                display_name="Security Questions and Answers",
                description='In this format: {"Question1":"Answer1","Question2":"Answer2"}',
                type=Password(),
                required=True,
            ),
            name="adp_web_credentials",
            display_name="ADP Web Access",
        ),
    ],
)

AmTrustConnection = Connection(
    connection_type_uuid="ATRST-APICR",
    alias="AmTrust Credentials",
    description="Credentials to use to authenticate with AmTrust.",
    categories=["AmTrust", "API"],
    parameter_groups=[
        ParameterGroup(
    Parameter(
                type=String(),
                name="client_id",
                display_name="Client ID",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="client_secret",
                display_name="Client Secret",
                required=False,
            ),
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="Required for identity-based tokens and will be supplied by AmTrust.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Required for identity-based tokens and will be supplied by AmTrust.",
                required=False,
            ),
            Parameter(
                type=String(),
                name="subscriber_id",
                display_name="Subscriber ID",
                description="Subscriber ID provided by AmTrust and required for all calls.",
                required=True,
            ),
            name="amtrust_params",
            display_name="AmTrust Params",
        ),
    ],
)

AppAnnieConnection = Connection(
    connection_type_uuid="APP1E-T0NXM",
    alias="AppAnnie:API:Token",
    description="App Annie API token.",
    categories=["mobile attribution", "app annie", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(type=Password(), name="token", display_name="Token", required=True),
            name="app_annie_params",
            display_name="App Annie Params",
        ),
    ],
)

AppleAppStoreConnection = Connection(
    connection_type_uuid="APPLE-APITK",
    alias="Apple App Store Connect Keys",
    description="Private key and other information used to connect to Apple's App Store Connect API.",
    categories=["Apple"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="issuer_id",
                display_name="Issuer ID",
                description="Displayed on the API Keys tab under Users and Access in App Store Connect.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="vendor_number",
                display_name="Vender Number",
                description="Displayed under Payments and Financial Reports in App Store Connect.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="key_id",
                display_name="Key ID",
                description="Identifier of the API key.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="private_key",
                display_name="Private Key",
                description="Private portion of the API key.",
                required=True,
            ),
            name="appstore_params",
            display_name="Apple App Store Connect Access",
        ),
    ],
)

AppsFlyerConnection = Connection(
    connection_type_uuid="AFLYR-APITK",
    alias="AppsFlyer Credentials",
    description="Token to use to connect to AppsFlyer.",
    categories=["AppsFlyer"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="Token",
                description="API Token or V2 Auth Token.",
                required=True,
            ),
            name="appsflyer_params",
            display_name="AppsFlyer Access",
        ),
    ],
)

AppLovinConnection = Connection(
    connection_type_uuid="APLVN-APITK",
    alias="AppLovin SDK Key",
    description="Key to use to connect to AppLovin.",
    categories=["AppLovin"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="SDK Key",
                description="AppLovin SDK Key.",
                required=True,
            ),
            name="applovin_params",
            display_name="AppLovin Access",
        ),
    ],
)


AWSS3BucketConnection = Connection(
    connection_type_uuid="AWSS3-BKH32",
    alias="AWS:S3:Bucket+Token",
    description="AWS Bucket Name and connection credentials.",
    categories=["aws", "bucket", "storage"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="bucket",
                display_name="Bucket",
                description="Name of the Bucket",
                required=True,
            ),
            Parameter(
                type=String(),
                name="endpoint_url",
                display_name="S3 Endpoint URL",
                description="S3 Endpoint url for non-AWS hosted buckets.",
            ),
            Parameter(
                type=String(),
                name="prefix",
                display_name="Folder Path Prefix",
                description="Path prefix to apply towards any requests to this bucket.",
            ),
            Parameter(
                type=String(),
                name="s3_temp_space",
                display_name="S3 Temporary Path",
                description="Folder in which Tasks using this Connection may create temporary files. A folder named temp in the root of the bucket will be used if left blank.",
            ),
            name="bucket_info",
            display_name="Bucket Info",
        ),
        ParameterGroup(
            Parameter(
                type=Password(),
                name="access_key_id",
                display_name="Access Key ID",
                description="First part of the Access Key.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="secret_access_key",
                display_name="Secret Access Key",
                description="Second part of the Access Key.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

AWSBucketConnection = Connection(
    connection_type_uuid="AWSS3-BUCKT",
    alias="AWS:Bucket",
    description="AWS Bucket Name and region information.  Does not include credentials that have access to said bucket.",
    categories=["aws", "bucket", "storage"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="bucket",
                display_name="Bucket",
                description="Name of the bucket.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="prefix",
                display_name="Folder Path Prefix",
                description="Path prefix to apply towards any requests to this bucket.",
            ),
            Parameter(
                type=String(),
                name="endpoint_url",
                display_name="S3 Endpoint URL",
                description="S3 Endpoint url for non-AWS hosted buckets.",
            ),
            Parameter(
                type=String(),
                name="region",
                display_name="Region",
                description="Region where the bucket is located.",
                required=True,
            ),
            name="bucket_info",
            display_name="Bucket Info",
        ),
    ],
)

AWSTokenConnection = Connection(
    connection_type_uuid="AWS5D-TO99M",
    description="AWS Access Key Information.",
    alias="AWS:Token",
    categories=["aws", "access", "credentials"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="aws_access_key_id",
                display_name="Access Key ID",
                description="First part of the Access Key.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="aws_secret_access_key",
                display_name="Secret Access Key",
                description="Second part of the Access Key.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="region",
                display_name="Region",
                description="Specify the AWS region that the session will be created within.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

AzureStorageConnection = Connection(
    alias="Azure Storage Credentials",
    description="Credentials to use to authenticate with Azure Storage Service.",
    connection_type_uuid="AZURE-CONST",
    categories=["Azure", "Microsoft"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="account_name",
                display_name="Account Name",
                description="Account Name provided by Azure Storage Service.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="account_key",
                display_name="Account Key",
                description="Account Key provided by Azure Storage Service.",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="shared_access_signature",
                display_name="Shared Access Signature",
                description="Shared Access Signature (SAS) to be used by Azure native services.",
                type=Password(),
                required=False,
            ),
            name="azure_storage_credentials",
            display_name="Azure Storage Credentials",
        ),
    ],
)

BrightreeConnection = Connection(
    alias="Brightree Credentials",
    description="Credentials to use to access Brightree.",
    connection_type_uuid="BRITR-CONCR",
    categories=['Brightree'],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="username",
                display_name="Username",
                description="User name used to log in.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Password associated with the user name.",
                type=Password(),
                required=True,
            ),
            name="brightree_parameters",
            display_name="Brightree Credentials",
        )
    ]
)

BonfireConnection = Connection(
    alias="Bonfire Credentials",
    description="Credentials to use to access Bonfire.",
    connection_type_uuid="BNFIR-CONCR",
    categories=['Bonfire'],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="email",
                display_name="Email",
                description="Email address used to log in.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Password associated with the email address.",
                type=Password(),
                required=True,
            ),
            name="bonfire_parameters",
            display_name="Bonfire Credentials",
        )
    ]
)

BoxConnection = Connection(
    connection_type_uuid="BOXFS-JWTAU",
    alias="Box Access Credentials",
    description="Client Credentials Grant or Key Pair authentication.",
    categories=["Box"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="client_id",
                display_name="Client ID",
                description="Required for both Client Credentials Grant and Key Pair authentication.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="client_secret",
                display_name="Client Secret",
                description="Required for both Client Credentials Grant and Key Pair authentication.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="jwt_key_id",
                display_name="Public Key ID",
                description="Required if a Private Key is specified.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="rsa_private_key_data",
                display_name="Private Key",
                description="Required if a Public Key ID is specified.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="rsa_private_key_passphrase",
                display_name="Private Key Passphrase",
                description="Required if a Private Key is specified and is protected by a passphrase.",
                required=False,
            ),
            Parameter(
                type=String(),
                name="enterprise_id",
                display_name="Enterprise ID",
                description="Required for both Client Credentials Grant and Key Pair authentication.",
                required=True,
            ),
            name="box_params",
            display_name="Box Access",
        ),
    ],
)

BrightSitesToken = Connection(
    alias="Bright Sites API Token",
    description="API Token to connect to Bright Sites.",
    connection_type_uuid="B1IPT-S83BM",
    categories=["Bright Sites", "API Token"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="api_key",
                display_name="API Token",
                type=Password(min=16, max=24),
                required=True,
            ),
            Parameter(
                type=String(),
                name="subdomain",
                display_name="Subdomain",
                description="Specify the subdomain associated with your Bright Sites data.  For example, if your domain is yourcompany.mybrightsights.com, type in just yourcompany.",
                required=True,
            ),
            name="API Information",
            display_name="API Information",
        ),
    ],
)

CalendlyConnection = Connection(
    alias="Calendly Access Token",
    description="Personal Access Token to access Calendly's REST API's.",
    connection_type_uuid="CLDLY-APITK",
    categories=["Calendly", "Access Token"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="Personal Access Token",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

CosmosDatabaseConnection = Connection(
    alias="Cosmos Database",
    description="Database access information.",
    connection_type_uuid="COSMS-DTBCN",
    categories=["Cosmos", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="uri",
                display_name="URI",
                description="URI used to connect to the database server.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="access_key",
                display_name="Access Key",
                description="Primary or Secondary Access Key.",
                type=Password(),
                required=True,
            ),
            name="cosmos_parameters",
            display_name="Cosmos Database Access",
        ),
    ],
)

CustomInkConnection = Connection(
    alias="Custom Ink Access",
    description="Credentials to access Custom Ink.",
    connection_type_uuid="CSINK-LPCON",
    categories=["Custom Ink"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="user",
                display_name="E-mail Address",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=True,
            ),
            name="customink_params",
            display_name="Custom Ink Access",
        )
    ],
)

CybersourceConnection = Connection(
    alias="Cybersource Access",
    description="Authentication details to access Cybersource.",
    connection_type_uuid="CBSRC-CNNHD",
    categories=["Cybersource"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="merchant_id",
                display_name="Merchant ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="merchant_key_id",
                display_name="Shared Secret Key ID",
                type=String(),
                required=False,
            ),
            Parameter(
                name="merchant_secret_key",
                display_name="Shared Secret Key Value",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="p12_certificate",
                display_name="P12 Certificate",
                type=Text(),
                required=False,
            ),
            Parameter(
                name="api_endpoint",
                display_name="Endpoint",
                type=Enum(
                    choices=[
                        "https://apitest.cybersource.com",
                        "https://api.cybersource.com",
                    ]
                ),
                required=True,
            ),
            name="cybersource_params",
            display_name="Cybersource Access",
        ),
    ],
)

DatabaseMySQLConnection = Connection(
    alias="Database:Mysql",
    description="MySQL database config.",
    connection_type_uuid="COCDB-MYSQL",
    categories=["MySQL", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 3306 is the typical port for MySQL.",
                type=String(),
                required=True,
                default="3306",
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=False,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="db_engine",
                display_name="Engine Type",
                description="Database type to connect to.",
                type=String(),
                required=True,
                default="mysql",
            ),
            name="connection_parameters",
            display_name="Connection Parameters",
        ),
    ],
)

DatabricksConnection = Connection(
    alias="Databricks Access Token",
    description="Personal Access Token to use to access Databricks' REST API's.",
    connection_type_uuid="DBKR5-RPIKJ",
    categories=["Databricks"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="machine",
                display_name="Host",
                description="Databricks host name.  Formatted as: <instance-name>.cloud.databricks.com",
                type=String(),
                required=True,
            ),
            Parameter(
                name="token",
                display_name="Token",
                description="Personal Access Token.",
                type=Password(),
                required=True,
            ),
            name="databricks_parameters",
            display_name="Databricks Access",
        ),
    ],
)

DialpadConnection = Connection(
    alias="Dialpad Access Token",
    description="API Key or OAuth Token to access Dialpad REST API's.",
    connection_type_uuid="DILPD-ACCESS",
    categories=["Dialpad", "Access Token"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="Access Token",
                description="API Key or OAuth Token.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

DOAccessTokenConnection = Connection(
    alias="DigitalOcean Access Token",
    description="Personal Access Token or OAuth Token to access DigitalOcean REST API's.",
    connection_type_uuid="DOKEY-ACCESS",
    categories=["DigitalOcean", "Access Token", "OAuth"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="Access Token",
                description="Personal Access Token or OAuth Token.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

DOSpacesKeysConnection = Connection(
    alias="DigitalOcean Spaces Key Pair",
    description="Access Key and Secret Access Key used to access Spaces.",
    connection_type_uuid="DOKEY-SPACE",
    categories=["DigitalOcean", "Spaces", "Access Key"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="do_access_key_id",
                display_name="Access Key ID",
                description="First part of the Access Key.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="do_secret_access_key",
                display_name="Secret Access Key",
                description="Second part of the Access Key.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

ElasticSearchConnection = Connection(
    connection_type_uuid="ELSTC-CNCTN",
    alias="Elasticsearch Credentials",
    description="Endpoint, optional user name and password or api token.",
    categories=["Elasticsearch"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="endpoint",
                display_name="Endpoint",
                description="Elasticsearch cluster endpoint URL. Formatted as: https://CLUSTER_ID.REGION.CLOUD_PLATFORM.DOMAIN:PORT",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="api",
                display_name="API Key",
                description="Optional. Api key to use instead of basic authentication.",
            ),
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="Optional. User name for basic authentication.",
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Optional. Password associated with the username.",
            ),
            name="elastic_params",
            display_name="Elasticsearch Parameters",
        )
    ],
)

FacebookConnection = Connection(
    connection_type_uuid="FB83P-AD8BP",
    alias="Facebook Credentials",
    description="Access Token and other information needed for access.",
    categories=["Facebook"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="access_token",
                display_name="Access Token",
                required=False,
            ),
            Parameter(
                type=String(),
                name="app_id",
                display_name="App ID",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="app_secret",
                display_name="App Secret",
                required=False,
            ),
            name="facebook_params",
            display_name="Facebook Parameters",
        ),
    ],
)


FileMakerJDBCConnection = Connection(
    connection_type_uuid="FMKER-3JDBC",
    alias="FileMaker JDBC Credentials",
    description="Credentials to connect to a FileMaker server via JDBC.",
    categories=["FileMaker", "JDBC"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="database",
                display_name="Database URL",
                default="jdbc:filemaker://{{ IPADDRESS }}/{{ DATABASE NAME }}.fmp12",
                required=True,
            ),
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                required=True,
            ),
            name="filemaker_jdbc_params",
            display_name="FileMaker JDBC Parameters",
        )
    ],
)


FireboltDatabaseConnection = Connection(
    connection_type_uuid="FRBLT-DTBCN",
    alias="Firebolt Database",
    description="Firebolt database access information",
    categories=["Firebolt", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="account_name",
                display_name="Account Name",
                description="Name of the account where database is located.",
                type=String(),
                required=False,
            ),
            Parameter(
                name="engine",
                display_name="Engine Name",
                description="Name of the database engine to use.",
                type=String(),
                required=True,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

FTPConnection = Connection(
    alias="FTP",
    description="FTP, FTPS or SFTP configuration.",
    connection_type_uuid="FTP92-TS0BZ",
    categories=["ftp", "sftp", "ftps"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="type",
                display_name="FTP Type",
                description="Type of FTP authentication to use",
                type=Enum(choices=["FTP", "FTPS Explicit", "SFTP"]),
                required=True,
            ),
            name="authentication_parameters",
            display_name="Authentication Parameters",
        ),
        ParameterGroup(
            Parameter(
                name="host_name",
                display_name="Hostname",
                description="DNS Host name of the server.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="FTP Port",
                description="Port 21 is the typical port for FTP and explicitly negotiated FTPS. Port 22 is the typical port for SFTP.",
                type=Int(min=1, max=65535),
                required=True,
                default=21,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=False,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="ssh_key",
                display_name="SSH Private Key",
                description="This field is only used for key based SFTP authentication.",
                type=Password(),
                required=False,
            ),
            name="server_parameters",
            display_name="Server Parameters",
        ),
    ],
)

GenericDatabaseConnection = Connection(
    alias="Generic:Database",
    description="Basic database access information.",
    connection_type_uuid="GNC8L-BG2T3",
    categories=["generic", "database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 3306 is the typical port for MySQL.",
                type=Int(min=1, max=65535),
                required=True,
                default=3306,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="db_engine",
                display_name="Database Type",
                description="Type of database to connect to.",
                type=Enum(choices=["mysql", "postgres"]),
                required=True,
                default="mysql",
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=False,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

GlofoxConnection = Connection(
    connection_type_uuid="GLFOX-APICN",
    alias="Glofox Credentials",
    description="Key and token and key for Glofox API access.",
    categories=["Glofox", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="url",
                display_name="URL",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="x_api_key",
                display_name="API Key",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="x_glofox_api_token",
                display_name="API Token",
                required=True,
            ),
            name="glofox_params",
            display_name="Glofox Parameters",
        )
    ]
)

GNUPrivacyGuardConnection = Connection(
    connection_type_uuid="GNUPG-PSHRS",
    alias="GNU Privacy Guard Credentials",
    description="Used to decrypt GPG files.",
    categories=["GNU Privacy Guard"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Text(),
                name="public_key_data",
                display_name="Public Key",
                description="Not required for symmetric key encryption.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="private_key_data",
                display_name="Private Key",
                description="Not required for symmetric key encryption.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="passphrase",
                display_name="Passphrase",
                description="Used for private key access, if needed, or symmetric key encryption.",
                required=False,
            ),
            name="gpg_params",
            display_name="GNU Privacy Guard Parameters",
        )
    ]
)

GoodDataConnection = Connection(
    connection_type_uuid="GC29M-VU5MG",
    alias="GoodData:Credentials",
    description="GoodData Credentials",
    categories=["GoodData", "Domain", "Username", "Password"],
    parameter_groups=[
        ParameterGroup(
            Parameter(type=String(), name="email", display_name="Email", required=True),
            Parameter(
                type=Password(), name="password", display_name="Password", required=True
            ),
            Parameter(type=String(), name="domain", display_name="Domain", required=True),
            name="gooddata_params",
            display_name="GoodData Parameters",
        ),
    ],
)

GoogleAdsConnection = Connection(
    alias="Google Ads Credentials",
    description="Developer Token and Manager Account used to access Google Ads.",
    connection_type_uuid="GLASD-ADDTL",
    categories=["Google"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="developer_token",
                display_name="Developer Token",
                description="Specify the Google Ads Developer Token.",
                required=True,
                help_header_id="Developer Token",
            ),
            Parameter(
                type=String(),
                name="impersonated_email",
                display_name="Manager Account Email Address",
                description="Specify the e-mail address associated with the Manager Account storing the Developer Token.  This account will be impersonated with the developer token.",
                required=True,
                help_header_id="Manager Account Email Address",
            ),
            name="google_ads_parameters",
            display_name="Google Ads Parameters",
        )
    ]
)

GoogleCloudConnection = Connection(
    alias="Google:ServiceAccount",
    description="Google Service Account Key JSON",
    connection_type_uuid="GOOGLE-SERVICE-ACCOUNT",
    categories=["google", "service"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="json",
                display_name="Service Account Keyfile JSON",
                description="Contents of the Keyfile which should be valid JSON",
                type=Password(),
                required=True,
            ),
            name="google_parameters",
            display_name="Google Parameters",
        ),
    ],
)

HanoverConnection = Connection(
    alias="Hanover Credentials",
    description="Credentials to use to authenticate with the Hanover.",
    connection_type_uuid="HNOVR-CICSC",
    categories=["API", "Hanover"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name to use to connect to the Hanover service.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="auth_hostname",
                display_name="Authentication Server",
                description="DNS name to use to connect to the authentication service for Hanover.",
                type=String(),
                required=True,
            ),
            Parameter(
                type=String(),
                name="client_id",
                display_name="Client ID",
                description="Required for both Client Credentials Grant.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="client_secret",
                display_name="Client Secret",
                description="Required for both Client Credentials Grant.",
                required=True,
            ),
            name="hanover_parameters",
            display_name="Hanover Access",
        )
    ]
)


HelpshiftConnection = Connection(
    alias="Helpshift API Key",
    description="API Key to use to authenticate with the Helpshift.",
    connection_type_uuid="HPST3-0BKDP",
    categories=["API", "HelpShift"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="domain",
                display_name="Domain",
                description="Specify the subdomain name associated with your Helpshift account.  For example, if your domain name is yourcompany.helpshift.com, type in just yourcompany.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="token",
                display_name="API Key",
                description="API Key to use to connect to Helpshift's REST API.",
                type=Password(),
                required=True,
            ),
            name="helpshift_parameters",
            display_name="Helpshift Access",
        ),
    ],
)

HubspotConnection = Connection(
    connection_type_uuid="HBSPT-APITK",
    alias="Hubspot Credentials",
    description="API Key or Access Token to connect to Hubspot.",
    categories=["Hubspot"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="Token",
                description="Enter your Hubspot API Key or Access Token.",
                required=True,
            ),
            Parameter(
                name="token_type",
                display_name="Token Type",
                description="Select token type. Note: HubSpot ceased support for API Keys on November 30, 2022.",
                type=Enum(
                    choices=["Access Token", "API Key"],
                ),
                default="Access Token",
                required=False,
            ),
            name="hubspot_params",
            display_name="Hubspot Parameters",
        ),
    ],
)

HunterIOToken = Connection(
    alias="Hunter.io:APIKey",
    description="API key used to connect to Hunter.io",
    connection_type_uuid="HTR10-API3B",
    categories=["hunter.io", "api", "key"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="api_key",
                display_name="API Key",
                description="API Key used to connect to Hunter.io.",
                type=Password(min=32, max=64),
                required=True,
            ),
            name="API Information",
            display_name="API Information",
        ),
    ],
)

HygraphConnection = Connection(
    connection_type_uuid="HGRPH-URTKN",
    alias="Hygraph Credentials",
    description="App URL and API Token",
    categories=["Hygraph"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="app_url",
                display_name="App URL",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="token",
                display_name="API Token",
                required=True,
            ),
            name="hygraph_params",
            display_name="Hygraph Access",
        ),
    ],
)

IMAPServerConnection = Connection(
    alias="IMAP Credentials",
    description="Credentials needed to access a mailbox via IMAP.",
    connection_type_uuid="IMAPS-MAIL1",
    categories=["IMAP", "Mail"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="E-mail Address",
                description="E-mail address used to access the IMAP account.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Password associated with the username.  Used for basic authentication.",
                required=False,
            ),
            Parameter(
                type=String(),
                name="host",
                display_name="Host Name",
                description="DNS name of the IMAP server.",
                required=True,
            ),
            name="basic_info",
            display_name="Basic IMAP Parameters",
        ),
        ParameterGroup(
            Parameter(
                type=String(),
                name="tenant_id",
                display_name="Tenant ID",
                description="Tenant ID of the Office 365 account containing the mailbox.",
                required=False,
            ),
            Parameter(
                type=String(),
                name="client_id",
                display_name="Client ID",
                description="Client ID of the Office 365 app with access to the mailbox.",
                required=False,
            ),
            Parameter(
                type=Password(),
                name="secret_value",
                display_name="Secret",
                description="Value of the Secret associated with the Client ID.",
                required=False,
            ),
            name="office365_info",
            display_name="Microsoft Office 365 Parameters",
        ),
    ],
)

InfluxDBConnection = Connection(
    connection_type_uuid="INFLX-DTBCN",
    alias="InfluxDB Credentials",
    description="URL, token and organization.",
    categories=["InfluxDB"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="url",
                display_name="Host URL",
                description="Enter the portion of the URL used to access the InfluxDB server that contains the hostname and port.  For example, https://yourserver.yourdomain.com:8086.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="token",
                display_name="API Token",
                description="For InfluxDB 2.x, enter the content of the API token with desired access.  For InfluxDB 1.x, enter username:password.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="organization",
                display_name="Organization",
                description="Enter the name of the organization associated with the API token.  Optional.",
                required=False,
            ),
            Parameter(
                type=String(),
                name="bucket",
                display_name="Bucket",
                description="Enter the name of the bucket where the time series data is stored.  Optional.",
                required=False,
            ),
            name="influxdb_params",
            display_name="InfluxDB Access",
        ),
    ],
)

IntercomConnection = Connection(
    connection_type_uuid="INTCM-APITK",
    alias="Intercom API Key",
    description="API Key to use to connect to Intercom.",
    categories=["Intercom"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="API Key",
                description="Intercom API key",
                required=True,
            ),
            name="intercom_params",
            display_name="Intercom Access",
        ),
    ],
)

IP2LocationConnection = Connection(
    connection_type_uuid="IP2LC-APITK",
    alias="IP2Location API Key",
    description="API Key to use to connect to IP2Connection.",
    categories=["IP2Connection"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="token",
                display_name="API Key",
                description="IP2Location API key",
                required=True,
            ),
            name="ip2location_params",
            display_name="IP2Location Access",
        ),
    ],
)

LookerConnection = Connection(
    alias="Looker:Host+Credentials",
    description="Authentication and endpoint information for accessing the Rest API on a Looker server.",
    connection_type_uuid="LKR38-BKOTZ",
    categories=["looker", "api"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="client_id",
                display_name="Client ID",
                description="Client ID portion of the API3 key associated with a user account on a Looker server.",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="client_secret",
                display_name="Client Secret",
                description="Client Secret portion of the API3 key associated with a user account on a Looker server.",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="looker_url",
                display_name="Looker API Host URL",
                description="URL with the DNS name and port number used to reach a Looker server's API endpoint.",
                type=String(),
                required=True,
            ),
            name="looker_info",
            display_name="Looker Information",
        ),
    ],
)

MailgunConnection = Connection(
    alias="Mailgun Connection",
    description="Credentials used to access Mailgun.",
    connection_type_uuid="MLGUN-CONN",
    categories=["Mailgun", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="api_key",
                display_name="Primary Account API Key",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="domain_name",
                display_name="Domain Name",
                type=String(),
                required=True,
            ),
            name="connection_parameters",
            display_name="Mailgun Information",
        ),
    ],
)

ManageOrdersConnection = Connection(
    alias="ManageOrders Connection",
    description="Credentials used to access ManageOrders.com API.",
    connection_type_uuid="MNG3O-BODP3",
    categories=["ManageOrders", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=True,
            ),
            name="connection_parameters",
            display_name="ManageOrders Information",
        ),
    ],
)

MetaQuestStoreConnection = Connection(
    alias="Meta Quest Store Credentials",
    description="Credentials used to access the Meta Quest store.",
    connection_type_uuid="MTQST-STC0N",
    categories=["Meta", "Quest", "Oculus"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="user",
                display_name="Email",
                description="Email address used to log in.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Password associated with the email address.",
                type=Password(),
                required=True,
            ),
            name="connection_parameters",
            display_name="Meta Quest Access",
        )
    ]
)

MicrosoftConnection = Connection(
    alias="Microsoft Credentials",
    description="Credentials for OAuth2 Authentication using Microsoft Graph",
    connection_type_uuid="MCSFT-GRAPH",
    categories=["Microsoft", "Graph", "OAuth2"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="client_id",
                display_name="Client ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="client_secret",
                display_name="Client Secret",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="tenant_id",
                display_name="Tenant ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Microsoft Account Username",
                description="Some applications require a web login as part of the authorization steps.",
                type=String(),
                required=False,
            ),
            Parameter(
                name="password",
                display_name="Microsoft Account Password",
                description="Some applications require a web login as part of the authorization steps.",
                type=Password(),
                required=False,
            ),
            name="connection_parameters",
            display_name="Microsoft Access",
        ),
    ],
)

MYSQLDatabaseConnection = Connection(
    alias="MySQL Database",
    description="Basic database access information.",
    connection_type_uuid="MYSQL-DTBCON",
    categories=["MySQL", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 3306 is the typical port for MySQL.",
                type=Int(min=1, max=65535),
                required=True,
                default=3306,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="ca_certificate",
                display_name="CA Certificate",
                description="SSL root certificate (PEM format).",
                type=Text(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

Neo4jConnection = Connection(
    connection_type_uuid="NEO4J-DTBCN",
    alias="Neo4j Credentials",
    description="Username, password and URI.",
    categories=["Neo4j"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="Username for authentication.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Password associated with the username.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="url",
                display_name="Host URI",
                description="Enter a URI that contains the scheme, hostname, port and database name.",
                required=True,
                default="neo4j://yourserver.yourcompany.com:7687/yourdatabase",
            ),
            name="neo4j_params",
            display_name="Neo4j Access",
        ),
    ],
)

NetSuiteConnection = Connection(
    alias="NetSuite Credentials",
    description="NetSuite Credentials",
    connection_type_uuid="NTSUT-CRDNT",
    categories=["NetSuite"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="account_id",
                display_name="Account ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="scope",
                display_name="Scope",
                default="restlets, rest_webservices",
                type=String(),
                required=True,
            ),
            Parameter(
                name="client_id",
                display_name="Client ID",
                type=String(),
                required=True,
            ),
            Parameter(
                name="private_key",
                display_name="Private Key",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="certificate_id",
                display_name="Certificate ID",
                type=String(),
                required=True,
            ),
            name="connection_parameters",
            display_name="NetSuite Access",
        ),
    ],
)

NowCertsConnection = Connection(
    connection_type_uuid="NCRTS-APICR",
    alias="NowCerts Credentials",
    description="Credentials to use to authenticate with NowCerts.",
    categories=["NowCerts", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="client_id",
                display_name="Client ID",
                type=Password(),
                required=True,
            ),
            name="nowcerts_params",
            display_name="NowCerts Access",
        ),
    ],
)

OracleDatabaseConnection = Connection(
    alias="Oracle Database",
    description="Basic database access information.",
    connection_type_uuid="ORACL-SRVDB",
    categories=["SQL", "Oracle"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 1521 is the typical port for Oracle Servers.",
                type=Int(min=1, max=65535),
                required=True,
                default=1521,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

OrderMyGearConnection = Connection(
    alias="Order My Gear Authorization Token",
    description="Authorization Token to connect to Order My Gear.",
    connection_type_uuid="ORMGR-AZTKN",
    categories=["Order My Gear", "Token"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="auth_token",
                display_name="Authorization Token",
                type=Password(),
                required=True,
            ),
            name="connection_parameters",
            display_name="Order My Gear Access",
        ),
    ],
)

POP3ServerConnection = Connection(
    alias="POP3 Credentials",
    description="Username and password to access the Hostname via POP3.",
    connection_type_uuid="POP3S-MAIL1",
    categories=["POP3", "Mail"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="Username or e-mail address used to access the POP3 account.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Password associated with the username.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="host",
                display_name="Host Name",
                description="DNS name of the POP3 server.",
                required=True,
            ),
            name="secret_info",
            display_name="Secret Info",
        ),
    ],
)

PostgresDatabaseConnection = Connection(
    alias="Postgres Database",
    description="Basic database access information.",
    connection_type_uuid="PSTGRS-DTBCON",
    categories=["Postgres", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 5432 is the typical port for Postgres.",
                type=Int(min=1, max=65535),
                required=True,
                default=5432,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="ca_certificate",
                display_name="CA Certificate",
                description="SSL root certificate (PEM format).",
                type=Text(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

PropagoConnection = Connection(
    connection_type_uuid="PRPGO-CNCTN",
    alias="Propago Credentials",
    description="Username and password to access Propago.",
    categories=["Propago"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                required=True,
            ),
        ),
    ],
)

QuickBooksConnection = Connection(
    connection_type_uuid="QCKBK-CNCTN",
    alias="QuickBooks Credentials",
    description="OAuth2 details used to access QuickBooks.",
    categories=["QuickBooks", "OAuth2"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="client_id",
                display_name="Client ID",
                description="Specified in the Keys & OAuth portion of the Developer section of the Developer Account dashboard.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="client_secret",
                display_name="Client Secret",
                description="Specified in the Keys & OAuth portion of the Developer section of the Developer Account dashboard.",
                type=Password(),
                required=True,
            ),
            Parameter(
                name="environment",
                display_name="Environment",
                description="Sandbox or Production environment.",
                type=Enum(choices=["Sandbox", "Production"]),
                default="Sandbox",
                required=True
            ),
            name="quickbooks_params",
            display_name="QuickBooks Parameters",
        )
    ]
)


RedisConnection = Connection(
    connection_type_uuid="REDIS-CNCTN",
    alias="Redis Credentials",
    description="Hostname, port and optional password used to access Redis.",
    categories=["Redis"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="host",
                display_name="Host",
                description="DNS name of server hosting Redis.",
                required=True,
            ),
            Parameter(
                type=Int(min=1, max=65535),
                name="port",
                display_name="Port",
                description="TCP Port that Redis is listening on. Port 6379 is typical.",
                required=True,
                default=6379,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Optional password for authentication.",
                required=False,
            ),
            name="redis_params",
            display_name="Redis Parameters",
            description="",
        )
    ],
)

RedshiftDatabaseConnection = Connection(
    alias="Redshift Database",
    description="Redshift database access information.",
    connection_type_uuid="AWSDB-RSCON",
    categories=["AWS", "redshift", "database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the cluster endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 5439 is the typical port for Redshift clusters.",
                type=Int(min=1150, max=65535),
                required=True,
                default=5439,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to within the cluster.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="db_engine",
                display_name="Database Type",
                description="Don't change this field value.",
                type=String(),
                required=True,
                default="redshift",
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=False,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

SalesforceConnection = Connection(
    connection_type_uuid="SFAPI-T0NXM",
    alias="Salesforce Access Token",
    description="Access Token to use to authenticate with Salesforce.",
    categories=["Salesforce", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="token",
                display_name="Access Token",
                description="Access Token to use to connect to Salesforce's REST API.",
                type=Password(),
                required=True,
            ),
            name="salesforce_parameters",
            display_name="Salesforce Access",
        ),
    ],
)

SanMarPOWSConnection = Connection(
    alias="SanMar Purchase Orders",
    description="Credentials to access SanMar's Purchase Ordering web service.",
    connection_type_uuid="S2MA4-SP38J",
    categories=["SanMar"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="endpoint_type",
                display_name="Endpoint Type",
                description="Type of Purchase Ordering web service to access.",
                type=Enum(choices=["Development", "Production"]),
                required=True,
            ),
            Parameter(
                name="sanMarCustomerNumber",
                display_name="Customer Number",
                description="Customer number to use to access SanMar's Purchase Ordering web service.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="sanMarUserName",
                display_name="Username",
                description="Username to use to access SanMar's Purchase Ordering web service.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="sanMarUserPassword",
                display_name="Password",
                description="Password to use to access SanMar's Purchase Ordering web service.",
                type=Password(),
                required=True,
            ),
            name="sanmar_parameters",
            display_name="SanMar Purchase Order Access",
        ),
    ],
)

SendGridConnection = Connection(
    alias="SendGrid API Key",
    description="API Key to use to authenticate with SendGrid.",
    connection_type_uuid="SNDGD-O3BXD",
    categories=["API", "SendGrid"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="token",
                display_name="API Key",
                description="API Key to use to connect to SendGrid's REST API.",
                type=Password(),
                required=True,
            ),
            name="sendgrid_parameters",
            display_name="SendGrid Access",
        ),
    ],
)


SentryConnection = Connection(
    alias="Sentry Auth Token",
    description="Auth Token to use to authenticate with Sentry.",
    connection_type_uuid="S9NTY-APTK7",
    categories=["API", "Sentry"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="org_slug",
                display_name="Organization Slug",
                description="Specify the slug of the organization associated with your Sentry account.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="token",
                display_name="Auth Token",
                description="Auth Token to use to connect to Sentry's REST API.",
                type=Password(),
                required=True,
            ),
            name="sentry_parameters",
            display_name="Sentry Access",
        ),
    ],
)


ShipHeroConnection = Connection(
    alias="ShipHero Credentials",
    description="Credentials to use to authenticate with ShipHero.",
    connection_type_uuid="SHPHR-CONCR",
    categories=['ShipHero'],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="username",
                display_name="Username",
                description="User name needed to generate an access token.",
                type=String(),
                required=False,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Password associated with the user name.",
                type=Password(),
                required=False,
            ),
            Parameter(
                type=Password(),
                name="refresh_token",
                display_name="Refresh Token",
                required=False,
            ),
            name="shiphero_parameters",
            display_name="ShipHero Access",
        )
    ]
)


ShipStationConnection = Connection(
    alias="ShipStation Credentials",
    description="Credentials to use to authenticate with ShipStation.",
    connection_type_uuid="SHPST-APITK",
    categories=["API", "ShipStation"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="api_key",
                display_name="API Key",
                type=String(),
                required=True,
            ),
            Parameter(
                name="api_secret",
                display_name="API Secret",
                type=Password(),
                required=True,
            ),
            name="shipstation_parameters",
            display_name="ShipStation Access",
        ),
    ],
)

ShopifyConnection = Connection(
    connection_type_uuid="SHPFY-APITK",
    alias="Shopify Access",
    description="Credentials to use to authenticate with Shopify.",
    categories=["Shopify", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(type=Password(), name="api_key", display_name="API Key", required=True),
            Parameter(type=Password(), name="password", display_name="Access Token", required=True),
            name="shopify_params",
            display_name="Shopify Access",
        ),
    ],
)


SingularConnection = Connection(
    connection_type_uuid="SNG1E-P9VDW",
    alias="Singular:API:Token",
    description="Singular API token",
    categories=["Singular", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(type=Password(), name="token", display_name="Token", required=True),
            name="singular_params",
            display_name="Singular Parameters",
        ),
    ],
)

SlackAPIConnection = Connection(
    alias="Slack:API:Token",
    description="Slack API token.",
    connection_type_uuid="SLKTK-O2B8D",
    categories=["API", "Slack"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="token",
                display_name="Token",
                description="Token string used to connect to Slack REST API's.",
                type=Password(),
                required=True,
            ),
            name="slack_parameters",
            display_name="Slack Parameters",
        ),
    ],
)

SMTPConnection = Connection(
    alias="SMTP Connection",
    description="SMTP Server Configuration",
    connection_type_uuid="EMAIL-SMTP",
    categories=["SMTP", "TLS", "Email"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="user",
                display_name="Username",
                type=String(),
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
            ),
            Parameter(
                name="tls",
                display_name="TLS Enabled",
                description="Must be enabled for OAuth2 authentication.",
                type=Boolean(),
                default=False,
            ),
            Parameter(
                name="host",
                display_name="Hostname",
                description="Host, url, or IP to connect to",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="Port Number",
                type=String(),
                required=True,
            ),
            name="server_parameters",
            display_name="Server Parameters",
        ),
    ],
)


SnowflakeDatabaseConnection = Connection(
    alias="Snowflake Database",
    description="Snowflake database access information.",
    connection_type_uuid="SNFK3-WHC0N",
    categories=["Snowflake", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="user",
                display_name="User",
                description="Login name for the user.",
                type=String(max=256),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Password for the user.",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="private_key",
                display_name="Private Key",
                description="Private Key for Key-Pair authentication.",
                type=Text(),
                required=False,
            ),
            Parameter(
                name="private_key_password",
                display_name="Private Key Encrypted Password",
                description="Private Key Encrypted Password for Key-Pair authentication.",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="account",
                display_name="Account",
                description="Name of your account (provided by Snowflake). For more details, see https://docs.snowflake.com/en/user-guide/python-connector-api.html#label-account-format-info.",
                type=String(max=256),
                required=True,
            ),
            Parameter(
                name="warehouse",
                display_name="Warehouse",
                description="Name of the default warehouse to use. You can include USE WAREHOUSE in your SQL to change the warehouse.",
                type=String(max=256),
                required=False,
            ),
            Parameter(
                name="database",
                display_name="Database",
                description="Name of the default database to use. You can include USE DATABASE in your SQL to change the database.",
                type=String(max=256),
                required=False,
            ),
            Parameter(
                name="role",
                display_name="Role Name",
                description="Name of the default role to use. After login, you can include USE ROLE in your SQL to change the role.",
                type=String(max=256),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

SQLServerDatabaseConnection = Connection(
    alias="SQL Server Database",
    description="Basic database access information.",
    connection_type_uuid="MSSQL-DTBCN",
    categories=["Microsoft", "SQL", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the database server or endpoint.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 1433 is the typical port for Microsoft SQL Servers.",
                type=Int(min=1, max=65535),
                required=True,
                default=1433,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="master_key",
                display_name="Database Master Key",
                type=Password(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

SSHHostConnection = Connection(
    alias="SSH Host",
    description="Remote Server SSH Session.",
    connection_type_uuid="SSH01-HOST1",
    categories=["SSH", "Secure", "Shell"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name of the host machine.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used for the secure shell connection. Port 22 is the typical port for SSH.",
                type=Int(min=1, max=65535),
                required=True,
                default=22,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                description="Optional.  Used for password based authentication.",
                type=Password(),
                required=False,
            ),
            Parameter(
                name="connect_timeout",
                display_name="TCP Connection Timeout",
                description="Optional.  Amount of seconds to wait for a successful TCP connection.",
                type=Int(),
                required=False,
            ),
            Parameter(
                name="private_key",
                display_name="Private Key",
                description="Optional.  Used for private key authentication and encryption.",
                type=Password(),
                required=False,
            ),
            name="server_parameters",
            display_name="Server Parameters",
        ),
    ],
)

SSHPrivateKeyConnection = Connection(
    alias="SSH Private Key",
    description="Private Key for SSH Authentication and Encryption.",
    connection_type_uuid="PVKEY-SSH01",
    categories=["SSH", "RSA", "Key"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="ssh_key",
                display_name="SSH Private Key",
                description="Private key string.",
                type=Password(),
                required=True,
            ),
            name="authentication_parameters",
            display_name="Authentication Parameters",
        ),
    ],
)

SteamWebConnection = Connection(
    connection_type_uuid="STEAM-WBCON",
    alias="Steam Access",
    description="Credentials to use to authenticate with Steam.",
    categories=["Steam"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="account_name",
                display_name="Account Name",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                required=True,
            ),
        )
    ]
)

StripeConnection = Connection(
    alias="Stripe Access",
    description="Credentials to use to authenticate with Stripe.",
    connection_type_uuid="STRIP-APICN",
    categories=["Stripe"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="secret_key",
                display_name="Secret Key",
                type=Password(),
                required=True,
            ),
            name="stripe_parameters",
            display_name="Stripe Parameters",
        )
    ]
)

SupplyLogicConnection = Connection(
    alias="SupplyLogic Access",
    description="Credentials to use to authenticate with SupplyLogic.",
    connection_type_uuid="SPPLY-LOGIC",
    categories=["SupplyLogic"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="token",
                display_name="Token",
                type=Password(),
                required=True,
            ),
            name="supplylogic_parameters",
            display_name="SupplyLogic Parameters",
        )
    ]
)

SyncoreConnection = Connection(
    connection_type_uuid="SYNCR-APITK",
    alias="Syncore Access",
    description="Credentials to use to authenticate with Syncore.",
    categories=["Syncore", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(type=Password(), name="api_key", display_name="API Key", required=True),
            name="syncore_params",
            display_name="Syncore Access",
        ),
    ],
)


SyncoreWebConnection = Connection(
    connection_type_uuid="SYNCR-WBSCR",
    alias="Syncore Web Credentials",
    description="Security information to use to authenticate with Syncore via the web.",
    categories=["Syncore"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="E-mail address of the user account with access the to Syncore data...",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Syncore password associated with the e-mail address.",
                required=True,
            ),
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS host name of the Syncore website.",
                type=String(),
                required=True,
            ),
            name="syncore_web_credentials",
            display_name="Syncore Web Access",
        )
    ]
)


TableauConnection = Connection(
    alias="Tableau Credentials",
    description="Tableau server access information.  Default or Personal tokens can be used.",
    connection_type_uuid="TBLU3-CN3PX",
    categories=["Tableau"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="server",
                display_name="Server URL",
                description="URL of Tableau server.",
                required=True,
                default="https://yourserver.yourcompany.com",
            ),
            Parameter(
                type=Enum(
                    choices=[
                        "8.3",
                        "9.0.X",
                        "9.1",
                        "9.2",
                        "9.3",
                        "10.0",
                        "10.1",
                        "10.2",
                        "10.3",
                        "10.4",
                        "10.5",
                        "2018.1",
                        "2018.2",
                        "2018.3",
                        "2019.1",
                        "2019.2",
                        "2019.3",
                        "2019.4",
                        "2020.1",
                        "2020.2",
                        "2020.3",
                        "2020.4",
                        "2021.1",
                        "2021.2",
                        "2021.3",
                        "2021.4",
                        "2022.1",
                        "2022.2",
                        "2022.3",
                        "2022.4",
                        "2023.1",
                    ]
                ),
                name="version",
                display_name="Tableau Server Version",
                description="Version of the Tableau server.",
                required=True,
                default="2023.1",
            ),
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                description="Username or the name of a personal access token.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Password for the username or the personal access token secret.",
                required=True,
            ),
            Parameter(
                type=Boolean(),
                name="is_personal_access_token",
                display_name="Personal Access Token",
                description="Enable if the credentials above are from a personal access token.",
                required=True,
                default=False,
            ),
            name="tableau_parameters",
            display_name="Tableau Parameters",
        ),
    ],
)

VerticaDatabaseConnection = Connection(
    alias="Vertica Database",
    description="Vertica database access information.",
    connection_type_uuid="VRTCA-DTBCON",
    categories=["Vertica", "Database"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="hostname",
                display_name="Hostname",
                description="DNS name used to connect to the Vertica server.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="port",
                display_name="Port",
                description="TCP Port used to connect. Port 5433 is the typical port for Vertica.",
                type=Int(min=1, max=65535),
                required=True,
                default=5433,
            ),
            Parameter(
                name="database",
                display_name="Database Name",
                description="Name of the database to connect to.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="username",
                display_name="Username",
                type=String(),
                required=True,
            ),
            Parameter(
                name="password",
                display_name="Password",
                type=Password(),
                required=False,
            ),
            name="db_parameters",
            display_name="Database Parameters",
        ),
    ],
)

VultrObjectStorageKeysConnection = Connection(
    alias="Vultr Object Storage Keys",
    description="Hostname and S3 credential keys to access Vultr Object Storage.",
    connection_type_uuid="VULTR-ACCESS",
    categories=["Vultr", "Object Storage"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=Password(),
                name="access_key_id",
                display_name="Access Key",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="secret_access_key",
                display_name="Secret Key",
                required=True,
            ),
            name="vultr_params",
            display_name="Access Credentials",
        ),
    ],
)

WebServerConnection = Connection(
    alias="Web Server Credentials",
    connection_type_uuid="WBSRV-CONN3C",
    description="Username and password to sign in to a webserver.",
    categories=["Web Server", "Sign in", "Username", "Password"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="username",
                display_name="Username",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                required=True,
            ),
        ),
    ],
)

WooCommerceConnection = Connection(
    alias="WooCommerce Credentials",
    description="Credentials to use to authenticate with WooCommerce.",
    connection_type_uuid="WCMRC-APITK",
    categories=["WooCommerce", "API"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="consumer_key",
                display_name="Consumer Key",
                type=String(),
                required=True,
            ),
            Parameter(
                name="consumer_secret",
                display_name="Consumer Secret",
                type=Password(),
                required=True,
            ),
            name="woocommerce_parameters",
            display_name="WooCommerce Parameters",
        ),
    ],
)

ZendeskConnection = Connection(
    connection_type_uuid="Z3GK9-XPGG3",
    alias="Zendesk:Subdomain+Credentials",
    description="E-mail address, password and subdomain used to access Zendesk data.",
    categories=["Zendesk", "Username", "Password"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                type=String(),
                name="email",
                display_name="E-Mail Address",
                description="E-mail address of the user account with access the to Zendesk data.",
                required=True,
            ),
            Parameter(
                type=Password(),
                name="password",
                display_name="Password",
                description="Zendesk password associated with the e-mail address.",
                required=True,
            ),
            Parameter(
                type=String(),
                name="subdomain",
                display_name="Subdomain",
                description="Specify the subdomain associated with your Zendesk data.  For example, if your domain is yourserver.zendesk.com, type in just yourserver.",
                required=True,
            ),
            name="zendesk_params",
            display_name="Zendesk Parameters",
        ),
    ],
)

ZenPlannerConnection = Connection(
    alias="Zen Planner Credentials",
    description="Credentials to use to authenticate with Zen Planner.",
    connection_type_uuid="ZNPLN-APITK",
    categories=["API", "Zen Planner"],
    parameter_groups=[
        ParameterGroup(
            Parameter(
                name="client_id",
                display_name="Client ID",
                description="Username provided when the API credentials were generated.",
                type=String(),
                required=True,
            ),
            Parameter(
                name="client_secret",
                display_name="Client Secret",
                description="Password provided when the API credentials were generated.",
                type=Password(),
                required=True,
            ),
            name="zenplanner_parameters",
            display_name="Zen Planner Access",
        ),
    ],
)
