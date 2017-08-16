# check

Check a CIS 322 project.  Designed to be used two ways: 

## Remote use (by students)

A web service for students to try turning in a credentials configuration file to check whether it can be cloned, installed, and run by the instructor.  The URL for remote checking, and notes on required project structure, will be published on Canvas as part of an assignment description.  

Note that this checker will be running on a small, weak computer.  We do not know yet whether the web service will be able to handle concurrent requests from many students.  It may be necessary to limit how many times each student may use the checker remotely. 

## Local use (by instructor or students)

### Instructor use

The instructor will use the core checking functions while grading.  By automating assessment of whether the project works, the instructor is freed to spend more time on critical evaluation of code readability, maintainability, documentation, etc. 

### Student use

Students can also run the checker themselves.  Ideally they should follow these steps in this order: 

* Unit test their project with nose
* Integration / system test at the command line
* Use this checker locally to make sure the deployment process will work, and to trouble-shoot issues
* Use this checker remotely to double-check that it will work for the instructor
* Turn credentials file in through Canvas, with confidence that it is going to work as well for the instructor as it worked for them. 

