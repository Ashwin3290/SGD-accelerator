import pandas as pd
from faker import Faker
fake = Faker()
import random
import datetime

data = []
for _ in range(200):
    age = random.randint(25, 35)
    salary = random.randint(55000, 75000)
    department = random.choice(['IT', 'HR', 'Sales'])
    join_date = datetime.date(2015, 1, 1) + datetime.timedelta(days=random.randint(0, 1461))
    data.append([age, salary, department, join_date])

generated_data = pd.DataFrame(data, columns=['age', 'salary', 'department', 'join_date'])
print(generated_data)
generated_data.to_csv('generated_data.csv', index = False)