# Acryl Executor

Remote execution agent used for running DataHub tasks, such as ingestion powered through the UI. 


```bash
python3 -m venv --upgrade-deps venv
source venv/bin/activate
pip3 install .
```

## Notes

By default, this library comes with a set of default task implementations: 

### RUN_INGEST Task

- **SubprocessProcessIngestionTask** - Executes a metadata ingestion run by spinning off a subprocess. Supports ingesting from a particular version, and with a specific plugin (based on the platform type requested) 

- **InMemoryIngestionTask** - Executes a metadata ingestion run using the datahub library in the same process. Not great for production where we can see strange dependency conflicts when certain packages are executed together. Use this for testing, as it has no ability to check out a specific DataHub Metadata Ingestion plugin. 

### Cloud Logging (S3)

There is one implementation of a cloud logging client that writes logs to S3. This is used by the Acryl Executor to write logs to S3.
To enable it you should set the following environment variables:
`ENV DATAHUB_CLOUD_LOG_BUCKET` - The S3 bucket to write logs to
`ENV DATAHUB_CLOUD_LOG_PATH` - The S3 path to write logs to

The logs are compressed with tar and gzipped before being uploaded to S3 to the following path:
`s3://CLOUD_LOG_BUCKET/CLOUD_LOG_PATH/<pipeline_id>/year=/month=/day=/<run_id>/`
