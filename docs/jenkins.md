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
![Screenshot 2024-05-03 at 10 49 13 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/e0e5c165-eb90-451a-a059-8c0fff1159d1)
