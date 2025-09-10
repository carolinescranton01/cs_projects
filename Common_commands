## Commonly used commands on the HPC

These commands are used to move around and view different files on the HPC.

*To log every command you use and everything it outputs, run script before you start working*
```
script todays_work_log.txt
```
This is especially helpful for us to see what commands you put in and what they outputted when looking for errors, and also for tracking the work you did on the HPC. If you don't need the log you can just delete it later. 

*Changing directories - moving around in your files using terminal: change directory (cd)*
```
# to go to a subfolder of the directory you are in
cd [folder_name]
# example
cd carolinescranton

# to go back a folder 
cd ..

# to go to a specific folder outside of your path
cd /path/to/folder
# example
cd /xdisk/kcooper/carolinescranton
```

*Making and removing directories - mkdir and rm*
```
# make a directory called 'folder'
mkdir folder

# remove a file called 'test_log.txt'
rm test_log.txt

# remove a folder and all contents within it
rm -r folder
```
NOTE: rm is permanent! If you delete your files you CANNOT recover them!

*Making a text file using nano*
```
nano test.txt
```
This will create a file called test.txt and open an editor where you can type. To exit the editor press control-X and then hit Y to save or N to not save. I usually will create a text file where I track the commands which I ran when processing data and what days I did them or any specific changes I made. 

*Viewing files and information in them*
```
# look at the first 10 lines (note - add -n 20 to look at the first 20 lines, or change 20 to any number)
head file.txt

# look at the last 10 lines (note - you can use the -n argument the same way as noted above)
tail file.txt

# look at the number of lines, words (spaces between each word), and bytes (all characters including spaces) in a file
# lines
wc -l file.txt
# words
wc -w file.txt
# bytes
wc -c file.txt
# these can be used in conjunction, ie. wc -lwc to get all three numbers
```

*View file permissions and sizes*
```
# ls is the most basic command - lists files in a directory
ls

# common flag options are l, h, a --> l adds the full name, a shows all files (including hidden), and h shows the size of the files in readable format (ie. gigabytes rather than bytes)
ls -lha
```

*Change file permissions* You likely won't use this one often unless you are sending your data to someone else.
```
# chmod command changes permissions and requires arguments for who, what, and which permissions.
# for 'who' you are granting permission to, your options are u=user (yourself), g=group (for example, kcooper or macooper lab), o=others, a=all (users and groups)
# for what you are doing, you can use + (give permission), - (remove permission), or = (set permissions to a specific combination)
# types of permissions are r (read - view files), w (write - edit files), and x (execute scripts)
chmod u+r file.txt  # grant myself permission to read 'file.txt'
chmod g=rwx script.sh   # grant the group permission to read, write, and execute script.sh
```

