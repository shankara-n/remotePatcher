### Py script to read commands from a file, and execute on remote computer.

The commands are read from the csv file inside this folder.


The commands are executed serially, but DO NOT MAINTAIN FILE SCOPE. eg,

`cd pi, ls,` is NOT the same output as `cd pi; ls;,`.

Each commmand is executed in a virtual shell on the target pc, and then the virtual shell returns to the root of the pc.

The login details are hardcoded. 

##To-do

- [ ] Remove the precommand postcommand feature


