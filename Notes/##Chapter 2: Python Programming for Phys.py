##Chapter 2: Python Programming for Physicist 

#Code: a list of instructions, resembling a mix of English words and math 
#When you are programing in Pythis you work in a development environment 
#when you first open python you see a window telling you what type of python you are using this is the IDLE
#where you see the text is called a python shell window
#What i am writing in right now is an editor window 
x=1 
print(x)
#2.2: Variables and assignments

#Quantities of interest in a program—which in physics usually means numbers,
#or sets of numbers like vectors or matrices—are represented by variables, which
#play roughly the same role as they do in ordinary algebra

x=1 #this is an assignment statement 
#a variable is like a box that stores information for you to refer to a later itme 
#Variable names in Python can be as long as you like and can contain both letters and
#numbers, as well as the underscore symbol “_”, but they cannot start with a
# number, or contain any other symbols, or spaces.

##Variable types:
# Integer: Can take on integer values and integer values only (e.g. 1, 0, or -2345)
# Float: A flloating point variable can take real or floating point variables such as 3.145, -6.60*10^(-43)
# String: stores text in the form of strings or letters, punctuation, symbols, and digits. (cannot do math with this)
# Complex: A complex variable can take on a complex value, such as 1+2j (cannot take on i)
#*take note that many of these can be represented as the other but are based on convenience, computer processing power, and computer storage
#*integer valriables are more accurate than floating point variables a lot of the time

## Examples of Integers: This is an important lesson, and one that is often missed when people first start programming computers: if you have an integer quantity, use an integer variable. 
# In quantum mechanics most quantum numbers are integers. 
#The number of atoms in a gas is an integer. So is the number of planets in the solar system or the number of stars in the galaxy. 
# Coordinates on lattices in solid-state physics are often integers. 
# Dates are integers. 
# The population of the world is an integer. 

## A thing to note: whenever you create a variable to represent a quantity in one of your programs, think about what type of value that quantity will take and
#choose the type of your variable to match it.

x=1.0 
#is logically equivalent to 
x=float(1) #this tells the computer to take the value 1 

##2.2.3 OUTPUT AND INPUT STATEMENTS
x = 1.5
z = 2+3j
print(x,z,sep="...")

#The code sep="..." tells the computer to use whatever appears between the quotation marks as a separator between values

#input statement
x = input("Enter the value of x: ")
# the value entered is always interpreted as a string value, even if you type in a number
x = input("Enter the value of x: ")
print("The value of x is",x)

#to convert a string into a number
temp = input("Enter the value of x: ")
x = float(temp)
y = float(temp)
print("The value of x is",x)
#or
x = float(input("Enter the value of x: "))
print("The value of x is",x)

x+y #addition
x-y #subtraction
x*y #multiplication
x/y #division (never gives integer result)
x**y #raising x to the power of y
x//y #the integer part of x divided by y, meaning x is divided by y and the result is rounded down to the nearest integer
x%y #modulo, which means the remainder after x is divided by y. For instance, 14%3gives 2, because 14 divided by 3 gives 4-remainder- 2. 

x += 1 #add 1 to x(i.e., make xbigger by 1)
x -= 4 #subtract 4 from x
x *= -2.6 #multiply x by−2.6
x /= 5*y #divide x by 5 times y
x //= 3.4#divide x by 3.4 and round down to an integer

#e.g. of physics type coding 
h = float(input("Enter the height of the tower: "))
t = float(input("Enter the time interval: "))
g= 9.81
s = g*t**2/2
print("The height of the ball is",h-s,"meters")

#you must import certain packages such as log 

from math import log 

log(5)

#different operations present in math package in python 
log #natural logarithm
log10 #log base 10
exp #exponential
sin, cos, tan #sine, cosine, tangent (argument in radians)
asin, acos, atan #arcsine, arccosine, arctangent (in radians)
sinh, cosh, tanh #hyperbolic sine, cosine, tangent
sqrt #positive square root

#Note that the trigonometric functions work with angles specified in radians, not degrees.

#to import all functions from math you can write 
from math import *

#the linear algebra module is called 
from math import numpylinalg

#the Fourier transform module is called 
from math import numpyfft

#2.3.1 THE IF STATEMENT
#It will happen often in our computer programs that we want to do something only if a certain condition is met

x = int(input("Enter a whole number no greater than ten: "))
if x>10:
        print("You entered a number greater than ten.")
        print("Let me fix that for you.")
        x = 10
print("Your number is",x)

#there are a lot of conditions an if statement can take 
#if x==1: Check if x = 1. Note the double equals sign.
#if x>1: Check if x > 1
#if x>=1: Check if x ≥ 1
#if x<1: Check if x < 1
#if x<=1:Check if x ≤ 1
#if x!=1: Check if x ̸= 1

#The while statement 

#As with the if statement, the while statement checks if the condition given is
#met (in this case if x > 10). If it is, it executes the indented block of code
#immediately following; if not, it skips the block. However (and this is the
#important difference), if the condition is met and the block is executed, the
#program then loops back from the end of the block to the beginning and checks
#the condition again. If the condition is still true, then the indented lines will be
#executed again. And it will go on looping around like this, repeatedly checking
#the condition and executing the indented code, until the condition is finally
#false

x = int(input("Enter a whole number no greater than ten: "))
while x>10:
    print("This is greater than ten. Please try again.")
    x = int(input("Enter a whole number no greater than ten: "))
print("Your number is",x)

#2.3.3 BREAK AND CONTINUE
#Two useful refinements of the while statement are the break and continue statements. The break statement allows us to break out of a loop even if the condi-
#tion in the while statement is not met.

while x>10:
    print("This is greater than ten. Please try again.")
    x = int(input("Enter a whole number no greater than ten: "))
    if x==111:
        break

#this contains an if statement inside a while loop. This is allowed in Python and used often. In the
#programming jargon we say the if statement is nested inside the while loop.

#2.4 LISTS AND ARRAYS
#Python provides standard features, called containers, for storing collections of numbers.

#The most basic type of container in Python is the list. A list, as the name suggests, is a list of quantities, one after another
#The quantities in a list, which are called its elements, do not have to be all of the same type. You can have an integer, followed by a float, followed by a
#complex number if you want

#e.g.
[ 3, 0, 0, -7, 24 ]

x = 1.0
y = 1.5
z = -2.2
r = [ x, y, z ]

#length of a vector in three dimensions
from math import sqrt
r = [ 1.0, 1.5, -2.2 ]
length = sqrt( r[0]**2 + r[1]**2 + r[2]**2 )
print(length)

#map: Thus map(log,r) takes the natural logarithm of each element of a list r in turn. More precisely, map creates a
#specialized object in the computer memory, called an iterator, that contains the logs, one after another in order. 

from math import log
r = [ 1.0, 1.5, 2.2 ]
logr = list(map(log,r))
print(logr)

#add a new element to the end of the list and set that element equal to the value given,

r= [ 2, 3, 4, 5]
x=2.2 
r.append(x)
print(r)

#empty list  a list with no elements in it at all, then add elements to it one by one as we learn of or calculate their values
#To create an empty list we say

r = []

#work on this slowly(not necessary lowkey)