Place holder for Jenkins pipeline.

This section assumes you do not have access to source control and would like to run these workflows natively in Jenkins.

## Plugin Requirements
- <b>Managed Files Plugin:</b> Stores the node and image definition json templates.
- <b>httpRequest Plugin:</b> Used to send payloads to CML.
- <b>readJSON and writeJSON:</b> Pretty straight forward. Needed to read and write JSON.

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

You should have both of your definition files uploaded and accessible to your pipleine now.
![Screenshot 2024-05-03 at 9 33 52 AM](https://github.com/model-driven-devops/cml-lifecycle/assets/65776483/dc778fe5-115f-43bd-a8a9-79a2fa236d6f)
