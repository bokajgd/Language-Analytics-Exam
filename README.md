# Exam Portfolio for Language Analytics

# Overview 

**Jakob Grøhn Damgaard, May 2021** <br/>
This folder contains  exam portfolio for the course *Language Analytics*

# Introduction
This document constitutes my collection of assignments from Spring 2021 course *Language Analytics*, part of the bachelor's elective in Cultural Data Science. These assignments all revolve around conducting computational analysis of language data with varying purposes in Python (Van Rossum & Drake, 2009). Four assignments were assigned by the teacher throughout the semester while the last one comprises a self-assignment project. All source scripts for each assignment are coded according to principles of object-oriented programming. Hence, each script consists of a class that houses different functions and is initialized when the script is executed from a command line. In this document, each assignment has appertaining sections that provide a short description of the topic and tasks, a section on how to interact with and run the code, a section describing the methods used and, lastly, a short reflection on the end results.


# General Instructions
This section provides a detailed guide for locally downloading the code from GitHub, initialising a virtual Python environment, and installing the necessary requirements. In order to maximise user-friendliness and ease the processes mentioned above, all projects have been collated into one single GitHub repository. Therefore, all code can be fetched into one local folder and as there are no overlapping dependencies, only a single virtual environment is needed. Please note, a local installation of Python 3.8.5 or higher is necessary to run the scripts.<br>
<br>
To locally download the code, please open a terminal window, redirect the directory to the desired location on your machine and clone the repository using the following command:

```bash
git clone https://github.com/bokajgd/Language-Analytics-Exam
```

Redirect to the directory to which you cloned the repository and then, proceed to execute the Bash script provided in the repository for initialising a suitable virtual environment: 

```bash
./create_venv.sh
```
<br>
This command may take a few minutes to finalise since multiple packages and libraries must be collected and updated. When it has run, your folder should have the following structure (folder depth of 2):

```bash

.
├── A2-Collocation
│   ├── README.md
│   ├── data
│   ├── output
│   ├── src
│   └── viz
├── A3-Sentiment-Analysis
│   ├── README.md
│   ├── data
│   ├── output
│   └── src
├── A4-Network-Analysis
│   ├── README.md
│   ├── data
│   ├── output
│   ├── src
│   └── viz
├── A5-Supervised-Learning
│   ├── README.md
│   ├── data
│   ├── output
│   ├── src
│   └── viz
├── Language_Analytics_Exam.pdf
├── README.md
├── SA-LDA-Feature-Extraction
│   ├── README.md
│   ├── data
│   ├── output
│   ├── src
│   └── viz
├── create_venv.sh
└── requirements.txt


```

You can verify this structure by running the following command:

```bash
tree -I lang_analytics_venv  -L 2
```

If everything checks out, you should be ready to execute the code scripts located in the respective assignment folders. This is the base folder from which you are advised to navigate back to whenever you are finished running and assessing the scripts in one of the assignment folders. Always remember to activate the virtual environment before executing scripts in the terminal command line. This command can only be executed when you are in the main folder.

```bash
source lang_analytics_venv/bin/activate
```

The same goes for deactivating the environment when use is ceases:

```bash
deactivate
```

All code has been tested in Python 3.8.5 on a 2020 MacBook Pro 13’’, 2 GHz Quad-Core Intel Core i5, 16 GB Ram running macOS Big Sur (11.2.6). Thus, following the instructions should allow for smooth execution on MacOS and Linux machines. If you are running the code in any other operating system, please adapt commands to that syntax. <br>
<bra>
More detailed instructions regarding the execution of the individual scripts can be found in the sections on the respective assignments.


# References
Van Rossum, G., & Drake, F. L. (2009). Python 3 Reference Manual. CreateSpace.

# License
Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg


