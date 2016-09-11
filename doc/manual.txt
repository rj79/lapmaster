# Lap Master Manual

## Index
[About Lap Master][]
[System Requirements][]
[Features][]
[Setup][]
[Start a Race][]
[Correct a Lap][]
[Inspect the Log][]
[Configure a Race][]
[Define Classes][]
[Define Persons][]
[Define Teams][]

## About Lap Master
Lap Master is a program for timing sports races. It was developed for
Mountainbike Linköping 12-timmars, a 12 hour multi-lap mountainbike race,
but can be used for other sports as well.

## Features
* Interactive text-based program for registering laps
* Supports multi-lap races
* Generates results in HTML
* Possible to define multiple classes
* Supports both solo participants and teams
* Simple text-based configuration
* Checks for errors in race configuration

## System Requirements
Lap Master requires Python 2.7 to run and is tested under Ubuntu Linux.

## Lap Master components
Lap Master has three main tools that work together:

| Program    | Description |
|------------|-------------|
| lmshell    | An interactive text-based program to register laps. |
| publisher  | A tool that generates a HTML page with results. |
| logmonitor | A tool that monitors lap events and notifies the publisher. |

## Unit tests
To run unit tests, just type make.

## Virtual environment
To make Lap Master work across as many systems as possible it uses a python
virtual environment. The commands in the rest of this document assume that
the virtual environment has been created an activated in your current
terminal. To create the virtual environment just type "make" in your terminal.

This will create a directory called "venv". To activate the virtual
environment, type :

    . venv/bin/activate

From now on, when you type python in that terminal, it will use the python
executable located in venv/bin and the modules required by Lap Master.
You have to repeat the above step for each terminal in which you intend to
execute one of the Lap Master programs.

## Setup
First you need to configure your race. See the section [Configure a Race][].

If you just want to try out Lap Master right away, you can use the example
configuration provided in example_race directory. Remember to forst enable
the [Virtual Environment][] for each terminal you open.

Go to the directory containing Lap Master.

Open a terminal and type:

    ./lmshell -i example_race

Open another terminal in the same directory and type:

    ./publisher -i example_race -o html

Open a third terminal in the same directory and type:

    ./logmonitor -l example_race/log.csv

Start a browser and go to

<http://localhost:5000/static/index.html>

Go back to lmshell, start the race by typing
start all
Then register some laps and watch the html page update.

### Start a Race

First you need to start the race. Do this by typing:

    start all

This will start the clock for all classes defined in classes.csv. If you want
to start specific classes, you type start followed by the ids of the classes.
For instance to start class 1 and 3 you type:

    start 1 3

If you already have started 1 or 3, for instance using start all, you will
receive an error message.

### Register a Lap
To register a participant that passes the finish line or lap line, just type
the corresponding bib number and confirm with pressing the return key:

    101

Note how Lap Master confirms each action by showing the latest registered
events after each action

    : start all
    [    0] 14:44:42 start: all
    : 101
    [    0] 14:44:42 start: all
    [    1] 14:44:52  101 Anna Pihl

The number to the left is called the event id, next you see the time stamp, and
finally the event itself.
We can see that all classes started at 14:44:42 (event 0), and that participant
Anna Pihl with bib number 101 passed at 14:44:52 (event 1).

### Correct a Lap
If an event is entered by mistake, this can be corrected using the set command.

    : set 1 102
    [    0] 14:44:42 start: all
    [    1] 14:44:52  102 Maria Cruz

Here, event 1 is changed so that it says that participant Maria Cruz with bib
number 102 passed. Note that the time stamp is not changed.

In case an event should be invalidated altogether, it is possible to specify
a dash (-) instead of the bib number. Example:

    : set 1 -
    [    0] 14:44:42 start: all
    [    1] 14:44:52 !!!!

## Inspect the Log
It is possible to show the complete log of registered events by typing log.

   log

It is possible to specify the number of events to show:

   log 30

This will show the 30 latest events.

## Configure a Race

A race configuration consists of:

*   Definition of classes
*   Definition of persons
*   Definition of teams

It is good practice to put all files belonging to a race in one directory.
It is also good practice to have a separate directory for the HTML
result pages.

    my_race/
      classes.csv
      persons.csv
      teams.csv
      log.csv
    html/

### Define Classes

By default, Lap Master looks for a file called *classes.csv* which lists the
available classes.
Each row contains one class definition and the format is as follows:

**&lt;class id&gt;,&lt;max team size&gt;,&lt;class name&gt;**

    # Example of class.csv
    1,1,Ladies solo
    2,1,Men solo
    3,4,Mixed Team

In the above example, three classes are defined. "Ladies solo" class has class
id 1 and maximum 1 participant per team.
"Men solo" class has class id 2 and also maximum 1 participant per team.
Finally, "Mixed Team" class has class id 3 and maximum 4 participants per team.

### Define Persons

By default, Lap Master looks for a file called *persons.csv* which lists all
the persons in the race.
Each row contains one person.
There are two row formats, depending on whether the person is participating in
a team or is going solo.

A row that defines a person who is member of a team has the following format:

**&lt;bib&gt;,&lt;name&gt;**

    # Example of persons.csv
    3031,Dag Helstad
    3121,Stefan Jansson

A row that defines a person who is in a solo class (a class which has been
defined to have maximum one person per team) has a special format:

**s,&lt;class id&gt;,&lt;bib&gt;,&lt;name&gt;**


&lt;class id&gt; must refer to a defined class.

    # Example of persons.csv
    s,1,101,Peter Lundgren
    s,1,119,Jakob Lohmann

The format is somewhat longer than the one for team persons, but on the other
hand there is no need to define a team for persons in solo classes.

    # Example of persons.csv with both solo and team persons
    s,1,101,Peter Lundgren
    s,1,119,Jakob Lohmann
    3031,Dag Helstad
    3121,Stefan Jansson

### Define Teams

By default, Lap Master looks for team definitions in a file called *teams.csv*.
Each row defines one team.
The format is as follows:

**&lt;class id&gt;,&lt;team name&gt;,&lt;bib 1&gt;,
&lt;bib 2&gt;,...,&lt;bib N&gt;**

    # Example of teams.csv
    3,Team Babyhull,3131,3032,3033

&lt;class id&gt; must refer to a defined class.
Each &lt;bib X&gt; in the team member list must refer to a defined person.
The number of members in a team must not exceed the defined maximum team size
of the class.

You don't have to enter any information in the team definition file for solo
persons, since all the necessary information is already in the person
definition file.
