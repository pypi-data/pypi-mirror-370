# Description
For the feature step 4, the target is to enhance the step 1 and 3 by adding the management of formatted text management for the message of the email and the formatted text fusion in the picture handled by the picture generator.
# Features details and guidances
## Formatted text
i suggest to limit the way to provide formatted text to .docx format 'because the best supported solution. The content of the file is a text formatted (police, size, shape, color) and can embed table, picture (static), ... The text can reference label following our convention with {{label}} where label is corresponding to the label of one of the column of the recipients.csv file.
## For the message body
The file to provide is msg.docx. only one msg.txt|docx should exists. if more than one, warn the user and ask him to clean.
## For the picture generator
I suggest to add a new fusion-type allowed value: "formatted-text". The data column is managed in the same way as graphic function-type, this is a path static, or provided by the recipients.csv file by a column. however, the path should point to a file type docx.
Because police, size, shape, color are managed into the formatted text file, those columns should be empty. The columns positioning, orientation and alignment stay valid for fusion-type set to formatted-text.
## Impact over dry run output
This feature as an impact on the dry run outputs. For now, the output is a txt file, not formatted. with this evolution, the user would like to see the message as it is formatted, based on the msg.docx he provided. Therefore, i suggest to output .eml file that the user can open using his local email client, like outlook.
# Documentation
To Q Dev CLI to update the documentation. I suggest this one is also usable by the consumer of the application by using the command line.

# Testing
Provide Unit test to cover 100%.

