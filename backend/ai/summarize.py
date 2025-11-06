from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model & tokenizer
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Input text
text = """Stack is a linear data structure that follows LIFO (Last In First Out) Principle, the last element inserted is the first to be popped out. It means both insertion and deletion operations happen at one end only.

push232
LIFO(Last In First Out) Principle
The LIFO principle means that the last element added to a stack is the first one to be removed.

New elements are always pushed on top.
Removal (pop) also happens only from the top.
This ensures a strict order: last in → first out.
Real-world examples of LIFO:

Stack of plates  The last plate placed on top is the first one you pick up.
Shuttlecock box  The last shuttlecock inserted is the first one taken out, since both operations happen from the same end.
Basic Terminologies of Stack
Top: The position of the most recently inserted element. Insertions (push) and deletions (pop) are always performed at the top.
Size: Refers to the current number of elements present in the stack.
Types of Stack:
Fixed Size Stack
A fixed size stack has a predefined capacity.
Once it becomes full, no more elements can be added (this causes overflow).
If the stack is empty and we try to remove an element, it causes underflow.
Typically implemented using a static array.
Example: Declaring a stack of size 10 using an array.

Dynamic Size Stack
A dynamic size stack can grow and shrink automatically as needed.
If the stack is full, its capacity expands to allow more elements.
As elements are removed, memory usage can shrink as well.
Can be implemented using:
-> Linked List → grows/shrinks naturally.
-> Dynamic Array (like vector in C++ or ArrayList in Java) → resizes automatically.
Example: Stack implementation using linked list or resizable array.

Note: We generally use dynamic stacks in practice, as they can grow or shrink as needed without overflow issues.

Common Operations on Stack:
In order to make manipulations in a stack, there are certain operations provided to us.

push() to insert an element into the stack.
pop() to remove an element from the stack.
top() Returns the top element of the stack.
isEmpty() returns true if stack is empty else false.
size() returns the size of the stack.
Refer to this article to know more about Operations on Stack.

Implementation of Stack
Stack can be implemented in Different Ways :-

Implementation of Stack using Array
Implementation of Stack using Linked List
Implementation of Stack using Deque"""

# Prepare input
inputs = tokenizer("Summarize the following notes in concise, meaningful sentences:\n " + text, return_tensors="pt", max_length=512, truncation=True)

# Generate summary
outputs = model.generate(
    **inputs,
    max_length=150,
    min_length=30,
    num_beams=4,
    repetition_penalty=2.5,
    length_penalty=1.2,
    early_stopping=True
)


# Decode summary
summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Summary:", summary)
