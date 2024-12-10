# capital-one-fraud-detection-app

Contributors
- Vidit Agrawal
- Ava Pezza
- Atharva Ketkar
- Abhishek Das

Set-up steps:
(1) set up UI locally, in this repo run "python3 app.py" or "python app.py"
(2) create a transaction, 
(a) if ML determines its fraudulent, a fraud confirmation email will be sent to capitalonecapstonedemo@gmail.com
(b) if ML determines its not fraudulent, no email will send.

Overview of Code:
(1) app.py = has all of the code that connects the UI to the s3 bucket in AWS
(2) templates/index.html = is the frontend for our UI
(3) model_exploration_c1_cipher_shield.ipynb = This is our python notebook we used to train our model, get model metrics and obtain test data results.
(4) ModelWeights/ = This folder has all the required model artifacts to run real-time inference on all the input test data obtained by the users.
(5) Data/ = This folder has all the CTGAN model generated data which we used for training our model
(6) AWSLambdas = contains the code that is used for our lambda functions

What works: 
-The end to end AWS pipeline that is decoupled for maximum throughout capacity. Our project mainly focused on the AWS architecture backend, starting from the origin destination for the transaction data, which is processed in order by Lambda functions that are set on triggers. This entire pipeline is serverless and non-provisioned. All lambda functions and triggers work for our end-to-end process. Furthermore, the model we built was trained on a synthetic dataset that we generated of about 10000 rows with the help of the CTGAN library. The model in particular is a Random Forest Regressor that ensembles predictions across various data points. We also used SMOTE to create balanced data for model training.

What doesn't work: 
-To stay within the allocated resources in our AWS free tier, we had two options for model deployment; an AWS lambda deployment package or using ECR to host the model artifactts. We could not use an AWS Lambda deployment package to use the model artifacts during runtime due to the sheer size of our model artifacts after compression, and using ECR during runtime would have us exceed our Lambda invocation limit. Hence for the purposes of the demo, the dataset in S3 already has a column with the predicted inference (is_fraud_detected) data present. The rest of the pipeline utilizes this result to determine whether to trigger an SNS email notification run or not. Again in our initial plan we intended to send SMS notifications as well, however this was also outside the scope of the AWS free tier. 

What we'd work on next:
-Most of our limitations were due to cost including changing the email notification to text notification, and deployment of our ML model. We could implement our application into the real Capital One app and implement our fraud notification in the app along as through a text/email.