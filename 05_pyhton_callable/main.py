from typing import Callable , Any , TypeVar , ClassVar , Generic
from dataclasses import dataclass , field 


#  a callable that takes two integers and return a string
@dataclass
class Calculator:
      operation: Callable[[int, int], str]
    #   here can also use __call__ . 

      def calculate (self , a : int , b: int)-> str:
        return self.operation(a , b)
def add_and_string(a :int , b:int)-> str:
    return str( a+ b)

calc = Calculator(operation= add_and_string)
print(calc.calculate(5 , 6))



#  generic 

# we use generic as for so that typing should be correct .
# like here it will return anything  . can take any type in the list and can return any 
# def first_item(list : list[Any])->Any:
#     return list[0]

# either here it can return hello
def first_item(list : list[Any])->Any:
     return "hello"   # type checker allows it
print(first_item([2,4])) # 2 
print(first_item(["a" , "b"])) # a

# thats why we use generic . generic means that whatever will come that will be the type 

T = TypeVar("T")

# def second_item(lst: list[T]) -> T:
#     return "hello"   # ❌ type checker will complain(mypy). # 2  main.py:39: error: Incompatible return value type (got "str", expected "T")  [return-value] Found 1 error in 1 file (checked 1 source file)
# print(second_item(["a" , "b"])) # a


def second_item(lst: list[T]) -> T:
    return lst[1]
# print(second_item(["a" , "b"])) # a
print(second_item([2,4])) 


#  now use of ths with dictionary ---
K = TypeVar("K")  # for keys
V = TypeVar("V") # for items

#  now for the dict
def get_item(container : dict[K ,V], key: K)-> V:
     return container[key]

d = {"a": 1 ,"b":2}
val= get_item(d , "a")
print(val)



# GENERIC  CLASSESS
C = TypeVar("C")
@dataclass
class Stack(Generic[C]):
    items: list['C'] = field(default_factory=  list)
    limit : ClassVar[int] = 10

    def push(self , item : C)->C:
        return self.items.append(item)
   
    def pop(self , item : C) ->C:
        return self.items.pop(item)
    

stack_of_ints = Stack[int]()
# print(stack_of_ints)
stack_of_ints.push(20)
stack_of_ints.push(10)
print(stack_of_ints)
