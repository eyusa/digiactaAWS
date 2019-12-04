# digiactaAWS
Project S3-AWS MediaConvert-S3

## AWS STACK CREATION

### AWS stack setup for MediaConvert WatchFolder
 Folder 'emc-watchfolder-stack' contains the required Cloudfront template and the lambda function code.
 
 To setup the AWS Stack perform teh following Steps:
 1. Under AWS, create an IAM Group called `CloudFormation-MediaConvert-Watchfolder-API`
 
 2. Add following policies to the group
    - `AWSLambdaFullAccess`
    - `IAMFullAccess`
    - `AmazonS3FullAccess`
    - `CloudWatchFullAccess`
    - `AmazonSNSFullAccess`
    - `AWSCloudFormationFullAccess`
 3. Create a user called `cfCreate_Admin` with programatic access and add the user to the above group.  
 
 4. Make a note of the access key and access secret for this user
 
 5. On the system, install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv1.html)
 
 6. Configure AWS CLI by running following command <br>

        awc configure
    Give the aws-key,aws-secret, aws-region and output as json
 
 7. Make sure make utility is installed ont eh system.
 
 8. Open the file `emc-watchfolder-stack/CF_Template_EMC_WatchFolder.yaml` and replace the email address user Parameters section.
 
 9. Run following commands to create cloudfront dependencies. <br>
    
        make create-s3
        make deploy-cf-dep-s3
    These will create an s3 bucket, lambda zip and push the lambda zip and cloudfront template to the created s3 bucket.  
 
 10. Run following commands to create cloudfront stack. <br>

         make create-cf-stack
        This will create full stack for mediaConvert watch folder.  
    
 Once the stach creation is complete it will create 2 S# buckets named: <br>
 - `emc-media-watchfolder` : This bucket will be used to store/load `.mp4` files
 - `emc-media-hls-bucket` : This folder will store the converted HLS formated files created by the MediaConvert.
    
Once a .mp4 file is uploaded to the `emc-media-watchfolder` folder a job is automatically trigger towards MediaConvert by the lambda function.
    
### Test the stack
To test the stack simply place an `.mp4` file in the s3 bucket called `emc-media-watchfolder` under folder `inputs`. Once the MediaConvert completes the job, you will get an email notification on teh email provided and can see the output folder under the bucket called `emc-media-hls-bucket`

Please use the sample file `test.mp4` in this folder for testing.  

## UPLOAD OF MP4 FILES TO S3 INPUT FOLDER

Install the requirements on teh system as defined in `requirements.txt` by running the command:

    pip install -r requirements.txt

To upload files from local system to the created s3 bucket as watch folder `emc-media-watchfolder` run the script called `upload-media-s3.py`.

        Usage: upload-media-s3.py [OPTIONS]        
        Options:
          -b, --bucket TEXT  S3 Bucket Name  [default: emc-media-watchfolder]
          -k, --key TEXT     AWS Key. If not provided it will be picked uop from the
                             aws config.
          -s, --secret TEXT  AWS Secret. If not provided it will be picked uop from
                             the aws config.
          -f, --file PATH    File to upload  [required]
          --help             Show this message and exit.

