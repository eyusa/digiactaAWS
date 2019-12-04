from urllib.parse import urlparse

print(urlparse('s3://<MEDIABUCKET>/HLS/').path)
print(urlparse('s3://emc-watchfolder-mediabucket-bhnoiqbsaky7/ple20191112/Default/HLS/').path)