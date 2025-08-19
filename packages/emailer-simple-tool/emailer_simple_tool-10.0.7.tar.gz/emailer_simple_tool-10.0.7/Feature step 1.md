# Description
For the feature step 1, the target is to build the minimum set for the application and put in place the foundation of the technical solution we see as mandatory for the next steps.
# Features and guidances
## Send simple emails
### Description
The program should send a simple email, just subject and body can be personalized, to a list of recipients. 
I suggest this user experience. Using a command line program, the user should provide a folder path which contains:
- The recipients.csv file where the first column is the label of the data
- The msg.txt file and the subject.txt file which contain the text to be used respectively for the body and the subject of the message.
### Guidances

- For the command line, used as the interaction method with the user, I would like to follow the RClone (https://rclone.org/) command line. I like very much the user experience. Same in this program, being able to save an email-inao campaign which is corresponding to the folder provided initially by the user and being able to reopen it and run updates, and action on it based on the proposed menu of available actions is very good. This design will help us to provide a more friendly interface in the very last step of the initial building of this application.
- I would like the program to validate the data provided by the user. Below is a list of validation to be done:
	- The recipients.csv file should contain a label "email" and the data in the column of that label should be for all lines a valid email. If not the program should warn the user and guide him to solve.
	- Each email should be unique in the CSV file. If not, warn the user, provide lines where email and line numbers where the same email had been found.
	- The email can be used as a unique key identifier but this is not mandatory. If the first column is not the email column, then the first column serves as the primary key of the data in the CSV file. The program should check that this column is valid to be a primary key. If duplicates found, same as email, warn the user, provide value and lines where the same value had been found. 
	- The msg.txt file and the subject.txt file contain textual data with reference to the label. The program should check that all references to label are ok and there is no reference pointing nowhere. It is not necessary to warn users about unused labels.
		==%% *Note for Q Dev CLI: Please, for the reference identification into the text of this 2 files, could you provide some guidance to maximize the user experience of the consumer of this application. You should keep in mind they are simple users, not dev neither IT. In python, the string.format method use '{}', is it the best way ? How the escape '{' and '}' if the text contains those characters intentionally ?* %%==
- The user has to provide the credential to connect to his smtp server to send email. In the majority of the case, the user will provide the smtp server for their online email address (gmail.com, outlook.com, laposte.net, yahoo.fr|com, etc). The application should provide a secure way to store this credential. I suggest this is an action in the menu of the campaign create/update. Also, the delete of the campaign should delete the saved credential but should not touch the initially provided folder by the user.
- I would like the program being able to test the smtp connection after the credential provided. I would like the program provide guidance to the user to troubleshoot smtp connection error, starting from the tcp layer (the output traffic is blocked and provide if possible at which hope the traffic is blocked) up to the application configuration. When possible, based on the domain (like the list I provided above), provides very precise guidances which reference the configuration of those solutions.
- I would like the program to provide a dry run feature. This one will generate the msg files into the user campaign provided folder under a folder name "dryrun" (the program creates the folder if it doesn't exist) in which the program create a folder for each dry run. Use a default naming convention of each dry run, but provide also the ability to the end user to give a name. check the name that not correspond to an already existing dry run, let the user accept the replace is it already exists.
- I would like the program to generate logs into the user campaign provided folder under a folder name "logs" (the program creates the folder if it doesn't exist). I suggest that as part of the create/update of a campaign, the user can set the log level and verbosity overwriting default value.
## Documentation
To Q Dev CLI to provide the documentation. I suggest this one is also usable by the consumer of the application by using the command line.

## Testing
Provide Unit test to cover 100%.
I guess the smtp connection is out of the scope of testing. This is managed into the campaign create/update menu action of the command line.