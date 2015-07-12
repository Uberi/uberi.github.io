---
title: "Python Gotchas: Bound Methods"
date: 2015-04-05
layout: post
---

I've seen this one a few times now, and apparently it's a pretty common mistake to make. Consider the following:

    class A:
        def x(self): print(self)

    def f(callback):
        callback("hello")

    a = A()

Now, assuming we've run this code, what's the difference between `f(a.x)` and `f(A.x)`?

If you're used to languages like Javascript (or other languages with prototypal OOP), then you'd probably expect that the `x` method print out `"hello"` in both cases - that methods act like functions with a `self` parameter when separated from their class.

This is not the case - the first snippet will actually result in an error! The difference becomes immediately obvious when we check the types of these two:

    >>> A.x
    <unbound method A.x>
    >>> a.x
    <bound method A.x of <__main__.A instance at 0x4f698e2b2370>>

Most Pythoners have seen issues caused by something like what's described in [this StackOverFlow answer](http://stackoverflow.com/questions/114214). This is because calls like `a.x()` are actually translated into something similar to `A.x(a)`.

However, this translation is **actually applied to method accesses, not method calls**. Anytime we access a method of an object using something like `a.x`, its first parameter actually gets bound to the object's instance!

In other words, `a.x` gets translated into something like `(lambda *args, **kwargs: A.x(a, *args, **kwargs))` - the method is partially applied to its associated class instance. This is called a **bound method**. Note that given this transformation `a.x()` is equivalent to `(lambda *args, **kwargs: A.x(a, *args, **kwargs))()`.

This difference becomes very important when we're doing things like using methods as callbacks. In the first example, we made things work by just accessing the method through the class itself in order to get the unbound version. This works, but is definitely not best practice - it's easy to mix up bound and unbound versions of the method.

The correct thing to do is to use the `@staticmethod` decorator on our callback, which eliminates its `self` parameter entirely and means that we can sidestep the whole bound/unbound distinction:

    class A:
        @staticmethod
        def x(stuff): print(stuff)

    def f(callback):
        callback("hello")

    f(A.x)

Note that if we used the `@classmethod` decorator to make `x` a class method, `A.x` would also bind `A` to the first parameter of `x`. In other words, when we access class methods, their first parameters are bound to their classes.
