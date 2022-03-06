# fantasyNBA.data

Tools:
- Python
- Terraform
- Azure Data Lake
- Snowflake
- DBT

Step 1. Scrape basketball-reference data
Step 2. Write data to lake 


## Steps in Snowflake to add blob storage
# Blob
create storage integration azure_int
  type = external_stage
  storage_provider = azure
  enabled = true
  azure_tenant_id = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab'
  storage_allowed_locations = ('azure://fantasynba.blob.core.windows.net/gamesplayed/');

desc storage integration azure_int;

use schema mydb.public;

create stage mystage
  url='azure://fantasynba.blob.core.windows.net/gamesplayed/'
  storage_integration = azure_int;

create or replace external table ext_table
 integration = 'MY_NOTIFICATION_INT'
 with location = @mystage/path1/
 file_format = (type = json);



# Queue
create notification integration azure_queue_int
  enabled = true
  type = queue
  notification_provider = azure_storage_queue
  azure_storage_queue_primary_uri = 'https://fantasynba.queue.core.windows.net/snowflakequeue'
  azure_tenant_id = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab';

desc notification integration azure_queue_int;



create stage mystage
  url='azure://fantasynba.blob.core.windows.net/gamesplayed/'
  storage_integration = azure_int;

create or replace external table gamesplayed
 integration = 'AZURE_QUEUE_INT'
 with location = @mystage/gamesplayed/
 file_format = (type = csv);

alter external table gamesplayed refresh;



use role sysadmin;
create database if not exists dataload;
create schema if not exists dataload.external_table;
use database dataload; 
use schema external_table;

CREATE FILE FORMAT CSV_FF TYPE = 'CSV' COMPRESSION = 'AUTO' FIELD_DELIMITER = ',' RECORD_DELIMITER = '\n' SKIP_HEADER = 0 FIELD_OPTIONALLY_ENCLOSED_BY = 'NONE' TRIM_SPACE = FALSE ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE ESCAPE = 'NONE' ESCAPE_UNENCLOSED_FIELD = '\134' DATE_FORMAT = 'AUTO' TIMESTAMP_FORMAT = 'AUTO' NULL_IF = ('\\N');

use role accountadmin;

CREATE STORAGE INTEGRATION AZURE_STORAGE_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = AZURE
  ENABLED = TRUE
  AZURE_TENANT_ID = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab'
  STORAGE_ALLOWED_LOCATIONS = ('azure://fantasynba.blob.core.windows.net/gamesplayed/');

desc storage integration AZURE_STORAGE_INT;
-> click on consent URL
-> save AZURE_MULTI_TENANT_APP_NAME

-> Add role of Data Contributor to storage account (AZURE_MULTI_TENANT_APP_NAME)

create or replace stage azure_stage
  storage_integration = AZURE_STORAGE_INT
  url = 'azure://fantasynba.blob.core.windows.net/gamesplayed/'
  file_format = CSV_FF;

create or replace external table
  games_played
  LOCATION = @azure_stage/files/
  AUTO_REFRESH = FALSE -- AUTO_REFRESH will be set to TRUE below
  FILE_FORMAT = CSV_FF;


SELECT 
  *
FROM 
  games_played;





### Setup in Snowflake
-- Setup database and schema
use role sysadmin;
create database if not exists nba;
create schema if not exists nba.external_table;
use database nba;
use schema external_table;

-- Setup storage intergration
use role accountadmin;
create storage integration azure_nba_gamesplayed
  type = external_stage
  storage_provider = azure
  enabled = true
  azure_tenant_id = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab'
  storage_allowed_locations = ('azure://fantasynba.blob.core.windows.net/gamesplayed/');

create storage integration azure_nba_playerstats
  type = external_stage
  storage_provider = azure
  enabled = true
  azure_tenant_id = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab'
  storage_allowed_locations = ('azure://fantasynba.blob.core.windows.net/playerstats/');

desc storage integration azure_nba_gamesplayed;
-- SnowflakePACInt1397 -> this is the Principle in Azure for IAM


-- Setup notification integration
create notification integration nba_notification
  enabled = true
  type = queue
  notification_provider = azure_storage_queue
  azure_storage_queue_primary_uri = 'https://fantasynba.queue.core.windows.net/nbastoragequeue'
  azure_tenant_id = '1909a595-5f96-4b0c-9d43-df6ca3afa9ab';

desc notification integration nba_notification;


-- Setup stage
use schema nba.public;

create stage nba_stage_playedgames
  url='azure://fantasynba.blob.core.windows.net/gamesplayed/'
  storage_integration = azure_nba_gamesplayed;

create stage nba_stage_playerstats
  url='azure://fantasynba.blob.core.windows.net/playerstats/'
  storage_integration = azure_nba_playerstats;
  

-- Setup external table
create or replace external table playedgames
 integration = 'NBA_NOTIFICATION'
 with location = @nba_stage_playedgames/
 file_format = (type = csv);

create or replace external table playerstats
 integration = 'NBA_NOTIFICATION'
 with location = @nba_stage_playerstats/
 file_format = (type = csv);
