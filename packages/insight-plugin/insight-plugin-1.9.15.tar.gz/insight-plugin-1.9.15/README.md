# Insight Plugin - CLI Tooling for plugin development

## Commands

### Analysis
Run Static Code Analysis on the plugin.

This command will run the static code analysis check on the plugin.

### Checks
Run analysis, linter and validate on the plugin.

This will allow you to recreate, locally, all the github checks that get run
on plugins.

### Create
Create a new plugin.

This command will generate the skeleton folder structure and 
code for a new plugin, based on the provided plugin.spec.yaml file.

### Export
Export a plugin Docker image to a tarball.

This tarball can be uploaded as a custom plugin 
via the import functionality in the InsightConnect UI.

### Refresh
Refresh the plugin.

This command will update the current plugin code, 
when updates are made in the plugin.spec.yaml file, 
and will also run 'black' to format the code.

### Validate
Validate / Run checks against the plugin. 

This command performs quality control checks on the current 
state of the plugin. 
This should be run before finalizing any new updates.

### Samples
Create test samples for actions and triggers. 

This command will create new files under the 'tests' folder which can be 
used to test each new action/trigger. 
Note if a file already exists for a particular action/trigger, it will be overwritten.

### Run
Run an action/trigger from a json test file (created during sample generation)

### Server
Run the plugin in HTTP mode. 

This allows an external API testing program to be used to test a plugin 

### Shell
Run the plugin via the docker shell to enable advanced debugging

### Convert Event Source

Convert a RapidKit event source to a plugin

This command will generate the skeleton folder structure and 
code for a new plugin, based on the provided RapidKit config.yaml file.
