Place holder for Jenkins pipeline.

This section assumes you do not have access to source control and would like to run these workflows natively in Jenkins.

## Plugin Requirements
- <b>Managed Files Plugin:</b> Stores the node and image definition json templates.
- <b>Config File Provider Plugin:</b> Feeds the .json templates into your groovy script.
- <b>Credentials Binding Plugin and Credentials Plugin:</b> These will allow us to pass our credentials safely between pipelines and stages.
- <b>Environmental Injector Plugin:</b> Allows us to set build related variables.
- <b>httpRequest Plugin:</b> Used to send payloads to CML.
- <b>Pipeline Utility Steps:</b> Includes the read and write json plugins.

## Backlog Items
These are items that will be updated once primary workflow is completed:

- <b> Only update nodes that are not running current image release</b> - Current pipeline targets, stops, wipes, and updates all nodes matching user input node name.
- <b> Config backup or extraction </b> - Backup current config and store it using the managed files plugin or as an archieve item. When new image is booted up, apply previous config. Second option - basline config is always stored externally and applied to new node.
- <b> Image Type Check </b> - Add logic to check if image is already available as a .qcow2 or a .img for easy conversion. If not, proceed with .iso to .qcow2 converstion. This will give any users the ability to still use the pipeline even if they need to manually convert the .iso.
- <b> Clean Up Error Checks and Comments </b>

## Required Environment Variables
To successfully execute this pipeline, you will need to set the following Jenkins environment variables:

- <b> CML_HOST: </b> This will be the IP address of your CML server. We will use this to SCP the .qcow2 image onto the server.
- <b> CML_LAB: </b> This is the name of your existing lab that you want to target for the node updates.
- <b> CML_URL: </b> This is the https://cml-address of your CML server that will be used for API calls.
- <b> NODE_DEFINITION: </b> This is the name of your node that we will target.
- <b> IMAGE_DEFINITION_STORAGE: </b> This is an interger that will be used to clean up the images. This will be the number of images assigned to your specified node at any given time. For example, If you set it to 4, when the 5th image is uploaded, it will delete the 1st image.
- <b> JENKINS_URL: </b> Seems silly, but to avoid more plugins, we are primarily using CURL commands to make API calls. This will be used to check artifacts in other pipelines.
- <b> IMAGE_URL: </b> This is the URL where your .img is posted. We are testing with an ubuntu build URL - https://cloud-images.ubuntu.com/daily/server/jammy/20240403/
- <b> IMAGE_KEYWORD: </b> This will be used to help identify any keyword you may need to grab the right .img file. For example, we want to download the ubuntu image for amd64.

## Setting Credentials

You will also need to set required credentials that will be used to authenticate against both Jenkins and CML. To avoid using additional plugins, this pipeline interacts with both Jenkins and CML using CURL. You will need the following set under Manage Jenkins -> Credentials.

You can set these by navigating to Manage Jenkins -> System. Then select System -> Global Credentials. Select "Add Credentials" in the top right corner. Select Username with Password and (You guessed it!) enter your CML username and password. use the ID "cml_credentials". The scripts in the pipeline reference this ID.

![Screenshot 2024-05-06 at 4 40 02 PM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/7790bc05-e415-48c0-999f-3ecdd8a1a43d)

Next, we want to generate our API token to be used to call Jenkins. Select your username in the top right corner. Under API token, select Add New Token and generate a token associated with your username.

![Screenshot 2024-05-06 at 4 47 06 PM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/0028b80c-c9f7-488a-be3c-426da61d6250)

Copy your token someplace safe. Navigate back to Manage Jenkins -> Credentials -> System -> Global Credentials and select "Add Credentials" again. Go ahead and select Usernamd and Password as the Kind. This time you are going to use your Jenkins username as the username and your token will be your password. Make sure you make the ID "jenkins-api-token". This ID will be referenced in the pipeline.

![Screenshot 2024-05-06 at 4 50 43 PM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/20356b5c-9aa4-4793-acdc-f7bdb173e3eb)


## Adding Definition Files to Jenkins

If you haven't installed the Managed Files plugin, go to Manage Jenkins -> Plugins -> Available Plugins and install it. If you cannot use the Managed Files plugin, this is only being used to pass two JSON files into our pipeline in order to update the node and image definitions in CML. You can store these just about anywhere for Jenkins to access, or you can modify the scripts in the JenkinsFile to generate the properly formatted Payload.

Once installed, navigate to Manage Jenkins -> Managed Files 
![Screenshot 2024-05-03 at 9 27 11 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/f1160510-1e7c-4ffe-acc9-c6b80c61daa2)

Select Create New File -> Json file and then select Next at the bottom.
![Screenshot 2024-05-03 at 9 27 53 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/30a13de7-a324-4be5-9761-304cf6e2fecb)

You can copy the JSON from the file in this repository under the definitions folder and simply paste it into the content box. Name the file "image_definition.json". Note: I'm sure there is a cool automated API way to do this, but meh. Copy and Paste works just as well.
![Screenshot 2024-05-03 at 9 30 27 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/34b56021-7d70-4f33-abde-3ff51df1f16a)

Do the same thing for the node_defintion.json file.
![Screenshot 2024-05-03 at 9 32 50 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/8a1816ca-a719-48b0-8564-c2896b1f8cc0)

You should have both of your definition files uploaded and accessible to your pipleine now. Take note of the IDs for each file. We need to reference them in our pipeline later.
![Screenshot 2024-05-03 at 9 33 52 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/dc778fe5-115f-43bd-a8a9-79a2fa236d6f)

## Preparing the Pipeline

Alright, so we have our environment variables set and we are ready to get our pipeline set up. First thing we need to do is grab our Jenkins files from this repository and copy them into Jenkins. There are three jenkins files and three different pipelines:

- <b> cml-qcow-create.jenkinsfile </b>: This is a work in progress, but this pipeline will be responsible for preparing your .qcow image that will be uploaded to CML and used with your new image definition. In its current state, you provide it an environment variable with the URL of your software repository. You can hardcode it or set it externally, but the pipeline will need some mechanism to download the initial image before converting it to a format compatible with CML. Once the image is converted into the proper format, it will be stored as an artifact in Jenkins for access during the other pipeline phases. This pipeline also keeps a running list of each build with a timestamp that will be used for cleaning up CML.
- <b> cml-image-update.jenkinsfile </b>: This pipeline can run nightly or can be set to trigger based on the qcow-create pipeline successfully completing. It will check the Jenkins artifacts for an updated .qcow2 file, upload it to your CML server, make any requested updates to the node definition, push a new image definition using the new .qcow2 file and attach it to the node definition, find your topology, and update the requested nodes with the new image.
- <b> cml-node-cleanup.jenkinsfile </b>: This pipeline allows the user to set an environment variable that will maintain a fixed number of new images on the CML server at any given time. For example, if you request 4 and a 5th image is uploaded, it will use the Jenkins artifiact from the qcow-create pipeline to identify the oldest image and remove it from CML. If there is an issue with the artifact_record file, it will fall back on deleting the oldest version.

### cml-qcow-create.jenkinsfile
This is currently under development. Right now, this pipeline will allow you to define a link to a repository of images. It will find the most recent image based on timestamp and keyword. It will download it, if it's a .img it will convert it to the proper format, name it, version it, and upload it as an artifact in Jenkins for retrival by the other pipelines. We are working on defining a .iso and creating a .qcow, but in its current state, a .iso will have to be manually converted and posted somewhere that Jenkins can access. This pipeline will still version it and upload it as an artifiact.

In your Jenkins dashboard, select New Item and name it cml-qcow-create. The names are important because the pipelines all work together, so make sure you name it correctly. Select "Pipeline" and "OK".

![Screenshot 2024-05-08 at 9 29 22 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/d21dc528-baf2-4594-bb35-52a02e369cee)

Under Advanced Project Options, you will see an area to insert a script under the "Pipeline" heading. The definition is Pipeline Script. Copy and paste the code from the cml-qcow-create.jenkinsfile in this repository right into the Script box and click save.

![Screenshot 2024-05-08 at 9 33 04 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/5fee975d-e574-49f3-b12f-f1ea40b2615e)

If you have defined your IMAGE_URL and IMAGE_KEYWORD variables, you should be able to run the script with no issues. Once it completes, you will see to artifacts produced. "artifact_record.csv" and a .qcow2 file with the name of your defined node plus a version numbe starting at 1. If you select "view" on the artifact_record.csv, you will notice this file is tracking each build. This file will be used later when we run the cml-cleanup pipeline.

(placeholder for screenshot)

### cml-image-update.jenkinsfile

For this next pipeline, we will follow the same process. Add a new item in your dashboard, name it cml-image-update, select Pipeline and select OK. Copy the script from the cml-image-update.jenkinsfile in this repo, right into the Script box and select okay. Assuming your credentials and environment variables are correct, and your cml-qcow-create pipeline has successfully posted an artifact, you can go ahead and run the pipeline. 

When you copy the script over, you will notice the "environment" block has IMAGE_DEF_ID and NODE_DEF_ID with the note to 'insert your ID here'. This is where we are going to use the IDs from the document plugin to grab your image and node definition templates. Go ahead and paste those IDs in.

```
pipeline {
  agent {  
    agent any
  }

  environment {
      IMAGE_DEF_ID = 'insert your ID here'  // ID of the managed image file
      NODE_DEF_ID = 'insert your ID here'  // ID of the managed node file
    }
```
Once you run this pipeline, it will execute the following workflow:
- Install any dependencies on the agent.
- Generate a auth token for CML.
- Check if there is matching qcow image that already exists on the CML server. If it doesn't, then it will proceed to download the artifact from the previous pipeline and upload it to CML.
- Create/update your node definition.
- Create/update your image definition.
- Identify your selected lab.
- Identify the nodes based on the node definition..
- If the node is running the most current version of software, it will be skipped.
- If the node is running an older version of software, it will be stopped, wiped, updated, and started.

(placeholder for CML screenshots)

### cml-node-cleanup.jenkinsfile


![Screenshot 2024-05-03 at 10 49 13 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/e0e5c165-eb90-451a-a059-8c0fff1159d1)
