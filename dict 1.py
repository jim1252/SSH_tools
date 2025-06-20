

# Python3 code to demonstrate working of
# Update dictionary with other dictionary
# Using loop
 
# initializing dictionaries
test_dict1 = {'gfg': 1, 'best': 2, 'for': 4, 'geeks': 6}
test_dict2 = {'for': 3, 'geeks': 5, 'nerds': 9}
 
# printing original dictionaries
print("The original dictionary 1 is : " + str(test_dict1))
print("The original dictionary 2 is : " + str(test_dict2))
 
# Update dictionary with other dictionary
# Using loop
for key in test_dict1:
    if key in test_dict2:
        test_dict1[key] = test_dict2[key]
 
# printing result
print("The updated dictionary is : " + str(test_dict1))