# PWP SPRING 2024
# PROJECT NAME
Job search site
# Group information
* Student 1. Janne Uutela, janne.uutela@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

dependencies in requirements.txt  
pip install -r requirements.txt  

Database is the default python3 sqlite


Run the backend in project root. The db will also be created if currently not existing:  
python3 main.py  


---api currently:  
localhost:3000/job   [GET,POST]  
localhost:3000/users    [POST]  
localhost:3000/login    [POST]  
    login required for posting a job (a token in cookies)  
    use postman or thunder client for postin login before posting a job (expires in 5min)  




