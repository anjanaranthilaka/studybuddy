# Python Functions and Scope

A function is a reusable block of code that runs only when called.

## Defining Functions
Functions are declared using the def keyword:
def greet(name: str) -> str:
    return f"Hello, {name}!"

## Arguments vs Parameters
- Parameter: Variable listed inside parentheses in function definition.
- Argument: Actual value sent to function when called.
- Positional vs Keyword: Positional arguments must match order; keyword arguments specify arg=value.
- Default values: def power(base, exp=2): allows default exponents.

## Scope: LEGB Rule
Variable resolution follows LEGB:
1. Local: Inside current function.
2. Enclosing: Any enclosing functions.
3. Global: Module top-level.
4. Built-in: Python built-in namespace (print, len).
