# coding=utf-8
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import subprocess

def run_script():
    return_code = subprocess.call(["switch_to","nothing"], shell=True)

    filepath = 'S12_testCases.txt'       # A text file with a list of commands
    #pipeOutFile = "pipout_" + filepath  # The file to write the command outputs to

    # Wait for the user to be ready before beginning the program
    startResponse = True
    while(startResponse):
        # Ask the user if they are ready
        userInput = raw_input("\n\nReady to begin testing? (y - yes, n - no)\nNote: n - no ends the program: ")
        userInput = userInput.upper()
        # Check the user's response
        if (userInput == "Y"):
            # Break out of the while loop and begin the program
            startResponse = False

        elif(userInput == "N"):
            # Output that he prgram is ending and end the program
            print("\nTest program " + filepath + " ended\n")
            quit()
        else: # catch all
            # Ask the user again
            startResponse = True


    with open(filepath) as fp:
        lines = fp.readlines()

    # Clean the commands by stripping the newline characters (\n) and the \r
    commands = []
    testCase = []
    for line in lines:
        line = line.strip("\n").strip("\r")
        commands.append(line)
        line = line.split()
        tempCase = line[-1].strip(".bin")
        testCase.append(tempCase)
        print(tempCase)

    i = -1
    # Execute the commands
    for command in commands:
        i += 1
        print("\n\nTest: " + command + "\n")
        pipeOutFile = testCase[i] + "pipeout.txt"

        # Call the command and write the output to a file
        with open(pipeOutFile, "w") as poutfile:
            line = "\n" + command + "\n"    # The command to be called
            poutfile.write(line)            # Write the command to be called at the top of the output
        with open(pipeOutFile, "a") as poutfile:
            return_code = subprocess.call([command], shell=True, stdout=poutfile)   # Call the command

        # Wait for the user to continue, repeat, or end the program
        userValid = True
        while(userValid):
            # Ask the user to continue, repeat, or exit
            userInput = raw_input("\n\nContinue? (y - yes, n - no, r - repeat.\n Note: r - repeat overwrites the saved data: ")
            userInput = userInput.upper()

            # Check user input end, repeat, or continue testing
            if(userInput == 'N'):
                print("\nTest program " + filepath + " ended\n")
                quit()
            elif(userInput == 'R'):
                # Repeat then ask again
                userValid = True
                print("\n\nRepeating test: " + command + "\n")

                # Call the command and write the output to a file
                with open(pipeOutFile, "a") as poutfile:
                    line = "\n" + command  # The command to be called
                    poutfile.write(line)  # Write the command to be called at the top of the output
                with open(pipeOutFile, "a") as poutfile:
                    return_code = subprocess.call([command], shell=True, stdout=poutfile)  # Call the command
            elif('Y'):
                # Exit the while loop and begin next test
                userValid = False
            else: #Catch all
                # ask again
                userValid = True

        # SCP the files back to save memory on the device
        #
        #
        #

    # Let the user know the program ended
    print("\nTest program " + filepath + " ended\n")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_script()

