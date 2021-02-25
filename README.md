# Sight Words

A simple app to help kids with sight words. It tracks the progress of 
a student and uses some basic statistics (thomson sampling) to 
choose good practice/test words.

## Installation:
Using pip, run `pip install .` from the root folder.

## Usage:

### Setup:
Create a new datafile to track results by calling:

```word_practice new_data_file <student_name>.yml <grade>```

### Practice/Testing:

To choose a new practice word run: 

```word_practice read <student_name>.yml```
or
```word_practice spell <student_name>.yml```



