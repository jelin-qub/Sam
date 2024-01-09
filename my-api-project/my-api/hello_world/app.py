import urllib.parse

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
    elif 'Records' in event and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:s3':
        # Process S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])
            print(f"File uploaded to S3 - Bucket: {bucket}, Key: {key}")

    # Your custom logic here

    return {
        'statusCode': 200,
        'body': 'Lambda function executed successfully!'
    }
