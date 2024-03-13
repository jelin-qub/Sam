import csv
import urllib.parse
import json
import boto3
import pandas as pd
import os
import io

# this is change2
# this is change1


def lambda_handler(event, context):
    print("Lambda function triggered!",event)


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
        print("processing s3")
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])

            print(f"File uploaded to S3 - Bucket: {bucket}, Key: {key}")

            # Check if the file is a CSV file
            if key.lower().endswith('.csv'):
                # If it's a CSV file, parse and print its contents
                print("processing d4")
                parse_and_convert_to_dataframe(bucket, key)
            else:
                print(f"File {key} is not a CSV file. Ignoring.")

    return {
        'statusCode': 200,
        'body': 'Lambda function executed successfully!'
    }


def parse_and_convert_to_dataframe(bucket, key):
    try:
        # Download the CSV file from S3
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket, Key=key)
        print("response", response)

        # Try decoding with common encodings
        common_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        csv_content = None
        for encoding in common_encodings:
            try:
                csv_content = response['Body'].read().decode(encoding)
                break  # Successful decoding, exit the loop
            except UnicodeDecodeError:
                pass  # Move to the next encoding


        if csv_content is None:
            raise Exception("Unable to decode the CSV file with any of the common encodings.")

        # Parse CSV content
        csv_reader = csv.DictReader(csv_content.splitlines())
        csv_data = [row for row in csv_reader]
        print("encoded", csv_data)

        # Convert CSV data to DataFrame
        df = pd.DataFrame(csv_data)

        # Print DataFrame
        print("dataframe",df)

        # Assuming send_rows_to_second_sqs is defined elsewhere
        send_rows_to_second_sqs(df)

    except Exception as e:
        # Handle the exception
        print(f"An error occurred while processing the CSV file: {e}")





def send_rows_to_second_sqs(df):
    # queue_arn = os.environ['SECOND_QUEUE_ARN']  # Retrieve from environment variable

    queue_arn = os.environ['SECOND_QUEUE_ARN']
    queue_url = os.environ['SECOND_QUEUE_URL']

    sqs = boto3.client('sqs')
    print(queue_arn)

    for index, row in df.iterrows():
        try:
            # Convert Pandas Series to dictionary
            row_dict = row.to_dict()

            response = sqs.send_message(
                QueueUrl=queue_url,  # Use the queue URL instead of the ARN
                MessageBody=json.dumps(row_dict)
            )

            print(f"Row sent to SQS - MessageId: {response['MessageId']}")
        except Exception as e:
            print(f"Error sending row to SQS: {e}")


def lambda_handler_second(event, context):
    print("Second Lambda function triggered!")

    # Check if the event is from SQS
    if 'Records' in event and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:sqs':
        # Process SQS message from the second queue
        for record in event['Records']:
            if 'body' in record and record['body']:
                body = record['body']
                print(f"Received message from second SQS: {body}")
                # Wrap the JSON string in StringIO
                json_io = io.StringIO(body)

                # Read JSON data into a DataFrame
                df = pd.read_json(json_io, orient='records', lines=True)


                process_dataframe_rows_second(df)
            else:
                print("SQS message body is empty or missing.")

    return {
        'statusCode': 200,
        'body': 'Second Lambda function executed successfully!'
    }

def process_dataframe_rows_second(df_json):
    # Convert the JSON back to a DataFrame
    df = pd.DataFrame(df_json)


    # Process each row (modify as needed)
    for index, row in df.iterrows():
        print(f"Processing row in the second Lambda: {row}")


