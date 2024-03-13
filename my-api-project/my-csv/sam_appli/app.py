import csv
import urllib.parse

import boto3
import pandas as pd

#change 3
def lambda_handler(event, context):
    print("Lambda function triggered!")

    # Check if the event is from SQS
    if 'Records' in event and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:sqs':
        # Process SQS message
        for record in event['Records']:
            if 'body' in record and record['body']:
                body = record['body']
                print(f"Received message from SQS: {body}")
            else:
                print("SQS message body is empty or missing.")



    # Check if the event is from S3
    elif 'Records' in event and 'eventSource' in event['Records'][0] and event['Records'][0][
            'eventSource'] == 'aws:s3':
        # Process S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])

            print(f"File uploaded to S3 - Bucket: {bucket}, Key: {key}")

            # Check if the file is a CSV file
            if key.lower().endswith('.csv'):
                # If it's a CSV file, parse and print its contents
                parse_and_convert_to_dataframe(bucket, key)
            else:
                print(f"File {key} is not a CSV file. Ignoring.")

    return {
        'statusCode': 200,
        'body': 'Lambda function executed successfully!'
    }


def parse_and_convert_to_dataframe(bucket, key):
    # Download the CSV file from S3
    response = boto3.client('s3').get_object(Bucket=bucket, Key=key)
    csv_content = response['Body'].read().decode('utf-8').splitlines()

    # Parse CSV content
    csv_reader = csv.DictReader(csv_content)
    csv_data = [row for row in csv_reader]

    # Convert CSV data to DataFrame
    df = pd.DataFrame(csv_data)

    # Print DataFrame
    print(df)

