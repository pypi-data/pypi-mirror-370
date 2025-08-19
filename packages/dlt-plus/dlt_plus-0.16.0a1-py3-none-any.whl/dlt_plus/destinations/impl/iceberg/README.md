## Catalog AWS [glue]
```toml
[destination.iceberg_glue]
catalog_name="aws_glue_catalog"
catalog_type="glue"
[destination.iceberg_glue.filesystem]
bucket_url="dlt-ci-glue-test-bucket"
[destination.iceberg_glue.credentials]
aws_access_key_id="XXXX"
aws_secret_access_key="XXXX"
region_name="eu-central-1"
```

## Catalog AWS [glue-rest] 
```toml
[destination.iceberg_glue_rest]
catalog_name="aws_rest_catalog"
catalog_type="glue-rest"
[destination.iceberg_glue_rest.credentials]
warehouse="267388281016:s3tablescatalog/dlt-ci-glue-test-bucket"
uri="https://glue.eu-central-1.amazonaws.com/iceberg"
aws_access_key_id="XXXX"
aws_secret_access_key="XXXX"
region_name="eu-central-1"
[destination.iceberg_glue_rest.credentials.properties]
"rest.sigv4-enabled"  = "true"
"rest.signing-name"   = "glue"
"rest.signing-region" = "eu-central-1"
```

## Catalog AWS [s3tables-rest] rest
```toml
[destination.iceberg_s3tables_rest]
catalog_name="aws_rest_catalog"
catalog_type="s3tables-rest"
[destination.iceberg_s3tables_rest.credentials]
warehouse="arn:aws:s3tables:eu-central-1:267388281016:bucket/dlt-ci-s3tables-test-bucket"
uri="https://s3tables.eu-central-1.amazonaws.com/iceberg"
aws_access_key_id="XXXX"
aws_secret_access_key="XXXX"
region_name="eu-central-1"
[destination.iceberg_s3tables_rest.credentials.properties]
"rest.sigv4-enabled"  = "true"
"rest.signing-name"   = "s3tables"
"rest.signing-region" = "eu-central-1"
```
