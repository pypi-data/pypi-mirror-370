# Description
For the feature step 3, the target is to provide a set a command providing the ability of the user to personalize a document by generating one per recipient from a common template.
Now, there is a very large kind of document and kind of personalization to perform over. Therefore, the building of this feature can't be a generic one. Bellow, i will  described  the covered scope for this first version of the feature. Keep in mind that the kind of documents and the actions performed over will be enhanced later to fit with the evolution of the needs of the user of the application. For now, only 1 kind of document will be handled (jpeg picture) and 3 personalization actions possible.
# Build personalized jpeg document from a jpeg template
## Description

## Textual fusion into the picture:

### Static text
This feature give to the user the ability to provide a static text, meaning which do not depend on the recipient and fusion it into the picture. This is very useful to put a date on a ticket, like the date of an event, or a message and being able to change it easily to reuse or enhance the current campaign. 
### Personalized text
This feature give to the user the ability to provide, like a static text, a text which contains one or many reference corresponding to labels available in the recipients.csv file. This feature is very useful the put the name and/or address into the ticket, making the ticket personalized to the recipient.
### Text fusion into the picture
The user should be able to provide all the details about the fusion the text into the picture: 
- positioning (pixel X / pixel Y starting with a convention from one or the corner of the picture)
- policies
- shape (normal, bold, italic, strikethrough and double strikethrough)
- size 
- color
- text alignment (left, right, center)
- text orientation, ...

## Graphical fusion into the picture

### Static graphical reference
This feature give to the user the ability to provide a static path to a graphical file, meaning which do not depend on the recipient and fusion it into the picture. This is very useful to put a logo and being able to change it easily to reuse or enhance the current campaign. 
### Personalized graphical reference
This feature give to the user the ability to provide, like a graphical reference, a path which is provided by the reference corresponding to a label available in the recipients.csv file. This feature is very useful the put a QRCode, making the ticket personalized to the recipient. in the majority of the case, those files are provided into a folder at the root of the folder campaign which contain a file where the name involve the primary key of the recipient.csv data.
### Graphical fusion into the picture
The user should be able to provide all the information describing the fusion of the graphical file into the picture, like:
- positioning (pixel X / pixel Y starting with a convention from one or the corner of the picture)
- the size of the graphical shape (in pixel, horizontal, vertical before rotation, if only one value is provide, the second one is calculated in order to keep the proportion of the source)
- orientation (0 meaning not rotation and is the default value, value in between -180 to +180, where in fact -180 and +180 provide the same result, this value is in degree)

==%%*Note for Q Dev CLI: For the very first implementation of this feature, I would like to go straight forward to the simpliest use case. Therefore, we will consider only the png format for the graphical file to fusion into the picture, which also can be only a jpg (or jpeg) format.*%%==
## Technical guidances.
### Folder structure for the user to provide the fusion he wants to perform
I would like to reuse the current concept that all that the user drive is provided into the campaign folder. Therefore, i suggest to have a folder named "picture-generator" at the root of the campaign folder which is optional, as attachments. into this folder the user can create a folder which is corresponding to one picture generator project. 
This folder contains:
- the picture template, template.jpg (or jpeg)
- all static png files
- the csv file fusion.csv which will describe all the fusion the user wants to perform
- the folder "data" where the personalized pictures are generated using the name %primary key value%.jpg. Each execution to generate the pictures will erase the previous picture generated.
- a text file attach.txt which contain true or false in oder to drive the command "emailer-simple-tool send" for al available option. if the value is "true", then personalized pictures are attached to the email, if false, no attachment. if the file doesn't exits, this is a false.

==%%*Note for Q Dev CLI: Given the usage of the primary key of the recipient.csv file to give the name of the generated picture for each recipient, the primary key has to be changes to an ID because for some OS, you can't use an email address as a filename. Therefore, when a user start a run the picture generator project to generate the pictures, the program should check that the recipients.csv file use an ID as primary key. For more details, you can look at the Feature step 1/md file where we specify this aspect.*%%==

### Specification of the fusion.csv file
This file contains a number a labeled column and each line is corresponding to one fusion task. the process will execute the fusion task in the order of the of the line into the this file.
For the column, i suggest:
- fusion-type: text or graphic
- data: this is a text containing one or many labels in the same shape as the msg.txt and subject.txt file content. If fusion-type is set to graphic, then the data contain only the label pointing to the column into the recipients.csv file for a personalized graphical fusion or the static path to the png file to fusion into the picture for a static graphical fusion.
- positioning: a 2 digits content like x:y
- size: a single digit for fusion-type set to text where the digit is the policy size, the value is mandatory. For fusion-type set to graphic, a 2 digits content like x:y, where x is the horizontal size and y the vertical size, if only 1 digit (like "x:" or ":y"), then the fusion will resize the graphic source to fusion keeping the proportion.
- orientation: a digit in between -180 and +180 (value is in degree), used to fusion text and graphic following this value.
- alignment: value can be "center", "left", "right" and is use with the positioning 2 digits value provided to place the text or the graphic into the picture
- policies: only for fusion-type set to text, give the name of the policy to use to put the text
- shape: normal, bold, italic, strikethrough and double strikethrough
- color: only for fusion-type set to text, labeled (like black, white, red) or hexadecimal (#000000, #999999) color used to fusion the text into the picture

### emailer-simple-tool CLI updates
We have to add all the needed command to perform the tasks.
here is the list of the command to be added and or updated:
- in "emailer-simple-tool config show", add the list and the status of the picture-generator projects. For the status, precise if a data folder containing all the personalized pictures aligned with the recipients.csv file exists. check the consistancy, the data folder, if exists, contains one file per recipient available into the recipients.csv file. Warn the user is the consistancy is not ok.
- in all "send" command, check the consistency of the picture-generator project used by the campaign. if error, warn the user. look at the attach.txt file, as specified above to drive is the given picture-generator project as to be used or not.
- add a menu to run a picture generator project.

# Documentation
To Q Dev CLI to update the documentation. I suggest this one is also usable by the consumer of the application by using the command line.

# Testing
Provide Unit test to cover 100%.