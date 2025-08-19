# Description
For the feature step 2, the target is to enhance the step 1 by adding the management of the static attachment. I mean "static" in the sense that those attachments are not personalized.

# Features and guidances
## Attach static documents
### Description
The program should attach the static documents that the folder "attachments" at the root of the provided folder for the campaign contains.
### Guidances

- I would like the program to validate the data provided by the user. Below is a list of validation to be done:
	- Check that all files in the attachments folder exist and are readable. If not, warn the user with file names and continue with y/n confirmation.
	- Check for potentially blocked file types (.exe, .zip, .bat, .scr, .com, .pif, .cmd, .jar, etc.). If found, warn the user about potential email delivery issues and continue with y/n confirmation.
	- Check the total size of the message given the size of the attachments to join:
		- **Warning at 15MB**: Display comprehensive message about email size limits across providers
		- **Alarm at 20MB**: Display stronger warning about delivery risks
		- No blocking in either case, always allow user to continue with y/n confirmation
		- Future enhancement: Consider suggesting to split into multiple emails
## Documentation
To Q Dev CLI to update the documentation. I suggest this one is also usable by the consumer of the application by using the command line.

## Testing
Provide Unit test to cover 100%.