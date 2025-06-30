Command to build the application. PLease remeber to change the project name and application name

gcloud builds submit --tag gcr.io/questionai-460617/questionsai  --project=questionai-460617

Command to deploy the application

gcloud run deploy --image gcr.io/questionai-460617/questionsai --platform managed  --project=questionai-460617 --allow-unauthenticated
