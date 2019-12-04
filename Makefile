LAMBDA_BUCKET:= cf-template-support

create-s3:
	aws s3 mb s3://${LAMBDA_BUCKET}

build-lambda-zip:
	rm -rf build
	mkdir -p build
	cp emc-watchfolder-stack/convert.py build/convert.py
	cp emc-watchfolder-stack/job.json build/job.json
	cd build && zip lambda . -r

push-lambda-s3:
	aws s3 cp build/lambda.zip s3://${LAMBDA_BUCKET}/lambda/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers

push-cf-template-s3:
	aws s3 cp emc-watchfolder-stack/CF_Template_EMC_WatchFolder.yaml s3://${LAMBDA_BUCKET}/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers

deploy-cf-dep-s3: build-lambda-zip push-lambda-s3 push-cf-template-s3

create-cf-stack:
	aws cloudformation create-stack --stack-name emc-watchfolder --capabilities CAPABILITY_NAMED_IAM --template-url https://s3.amazonaws.com/${LAMBDA_BUCKET}/CF_Template_EMC_WatchFolder.yaml

