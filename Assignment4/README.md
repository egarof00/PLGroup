# PLGroup

**Members:** Zuleyka Urieta, Keira Ryan, Emma Garofalo


**Source Files:** 
* grammar.lark
* interpreter_test.py
* interpreter.py

## Known Errors:
For all given test cases in the assignment our interpreter functions correctly, except for the last case

"interpreter, letrec map = \f. \xs. if xs==# then # else (f (hd xs)) : (map f (tl xs)) in (map (\x.x+1) (1:2:3:#)), (2.0 : (3.0 : (4.0 : #)))"

We are running into an infinite recursion error that we have been unable to resolve.
All other logic funtions as expected though.