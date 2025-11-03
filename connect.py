import pymongo
import os
from dotenv import load_dotenv
import certifi

load_dotenv()


class UniversityDB:
    def __init__(self):
        self.students = []

    def connect_to_database(self, connection_string):
        client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
        db = client["University"]  # Creates database if it doesn't exist
        return db

    def create_collections(self, mydb):
        collec3 = mydb["Student"]

        mydb.drop_collection("Student")

        collec3.insert_many(self.students)
        print("Collections:", mydb.list_collection_names())

    def student_data(self):
        self.students = [
            {
                "student_id": "S1001",
                "name": "Alice Johnson",
                "major": "Computer Science",
                "enrollment_year": 2021,
                "gpa": 3.8,
                "credits_taken": 95,
                "credits_remaining": 25,
                "courses_completed": [
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "A"},
                    {
                        "course_id": "CSE 301",
                        "course_name": "Data Structures",
                        "grade": "A",
                    },
                    {
                        "course_id": "CSE 303",
                        "course_name": "Human Computer Interaction",
                        "grade": "A+",
                    },
                    {
                        "course_id": "CSE 402",
                        "course_name": "Software Engineering with Agile Practices",
                        "grade": "A",
                    },
                ],
            },
            {
                "student_id": "S1002",
                "name": "Bob Smith",
                "major": "Information Technology",
                "enrollment_year": 2020,
                "gpa": 3.1,
                "credits_taken": 110,
                "credits_remaining": 10,
                "courses_completed": [
                    {
                        "course_id": "CSE 301",
                        "course_name": "Data Structures",
                        "grade": "B",
                    },
                    {
                        "course_id": "CSE 302",
                        "course_name": "Discrete Mathematics",
                        "grade": "B+",
                    },
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "A-"},
                ],
            },
            {
                "student_id": "S1003",
                "name": "Charlie Brown",
                "major": "Software Engineering",
                "enrollment_year": 2022,
                "gpa": 2.5,
                "credits_taken": 60,
                "credits_remaining": 60,
                "courses_completed": [
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "A-"},
                    {
                        "course_id": "CSE 302",
                        "course_name": "Discrete Mathematics",
                        "grade": "A",
                    },
                ],
            },
            {
                "student_id": "S1004",
                "name": "Diana Prince",
                "major": "Computer Science",
                "enrollment_year": 2021,
                "gpa": 3.9,
                "credits_taken": 88,
                "credits_remaining": 32,
                "courses_completed": [
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "B+"},
                    {
                        "course_id": "CSE 401",
                        "course_name": "Machine Learning",
                        "grade": "B",
                    },
                ],
            },
            {
                "student_id": "S1005",
                "name": "Ethan Hunt",
                "major": "Cyber Security",
                "enrollment_year": 2019,
                "gpa": 3.2,
                "credits_taken": 120,
                "credits_remaining": 0,
                "courses_completed": [
                    {
                        "course_id": "CSE 402",
                        "course_name": "Software Engineering with Agile Practices",
                        "grade": "A",
                    },
                    {
                        "course_id": "CSE 401",
                        "course_name": "Machine Learning",
                        "grade": "A-",
                    },
                    {
                        "course_id": "CSE 303",
                        "course_name": "Human Computer Interaction",
                        "grade": "B+",
                    },
                ],
            },
            {
                "student_id": "S1006",
                "name": "Fiona Davis",
                "major": "Data Science",
                "enrollment_year": 2023,
                "gpa": 3.8,
                "credits_taken": 45,
                "credits_remaining": 75,
                "courses_completed": [
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "B"},
                    {
                        "course_id": "CSE 302",
                        "course_name": "Discrete Mathematics",
                        "grade": "A",
                    },
                ],
            },
            {
                "student_id": "S1007",
                "name": "George Miller",
                "major": "Artificial Intelligence",
                "enrollment_year": 2020,
                "gpa": 3.3,
                "credits_taken": 105,
                "credits_remaining": 15,
                "courses_completed": [
                    {
                        "course_id": "CSE 301",
                        "course_name": "Data Structures",
                        "grade": "A",
                    },
                    {
                        "course_id": "CSE 401",
                        "course_name": "Machine Learning",
                        "grade": "A-",
                    },
                    {
                        "course_id": "CSE 402",
                        "course_name": "Software Engineering with Agile Practices",
                        "grade": "B+",
                    },
                ],
            },
            {
                "student_id": "S1008",
                "name": "Hannah Lee",
                "major": "Information Systems",
                "enrollment_year": 2022,
                "gpa": 2.9,
                "credits_taken": 72,
                "credits_remaining": 48,
                "courses_completed": [
                    {
                        "course_id": "CSE 302",
                        "course_name": "Discrete Mathematics",
                        "grade": "B+",
                    },
                    {
                        "course_id": "CSE 303",
                        "course_name": "Human Computer Interaction",
                        "grade": "A",
                    },
                ],
            },
            {
                "student_id": "S1009",
                "name": "Ian Parker",
                "major": "Computer Engineering",
                "enrollment_year": 2021,
                "gpa": 3.6,
                "credits_taken": 90,
                "credits_remaining": 30,
                "courses_completed": [
                    {"course_id": "CSE 201", "course_name": "Calculus", "grade": "B"},
                    {
                        "course_id": "CSE 301",
                        "course_name": "Data Structures",
                        "grade": "A",
                    },
                    {
                        "course_id": "CSE 401",
                        "course_name": "Machine Learning",
                        "grade": "B+",
                    },
                ],
            },
            {
                "student_id": "S1010",
                "name": "Julia Roberts",
                "major": "Computer Science",
                "enrollment_year": 2019,
                "gpa": 3.7,
                "credits_taken": 125,
                "credits_remaining": 0,
                "courses_completed": [
                    {
                        "course_id": "CSE 301",
                        "course_name": "Data Structures",
                        "grade": "A+",
                    },
                    {
                        "course_id": "CSE 402",
                        "course_name": "Software Engineering with Agile Practices",
                        "grade": "A",
                    },
                    {
                        "course_id": "CSE 401",
                        "course_name": "Machine Learning",
                        "grade": "A-",
                    },
                ],
            },
        ]


def main():
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    db_instance = UniversityDB()
    db_instance.student_data()
    database = db_instance.connect_to_database(connection_string)
    db_instance.create_collections(database)
    print("Database and collection Student created successfully.")


if __name__ == "__main__":
    main()
