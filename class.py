## Example: Modifying object attributes
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

def increase():
    person.age = 31
    print(person.age)  ## Output: 31
    

person = Person("John Doe", 30)
print(person.age)  ## Output: 30
#person.age = 31
#print(person.age)  ## Output: 31
increase()
print(person.age)
