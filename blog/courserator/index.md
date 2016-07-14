---
title: Introducing COURSERATOR3000
date: 2014-12-06
description: Overview of how COURSERATOR3000 resolves schedule conflicts by reducing them to Boolean SAT problems.
layout: post
---

[COURSERATOR3000](http://courserator.anthony-zhang.me/) is a course schedule generator for courses at the University of Waterloo, created due to frustrations with existing scheduling tools.

What's the problem? If you have, say, 5 or 6 courses, finding a schedule without conflicts is a nightmare. For each course, you must choose a section for lectures, tutorials, tests, and possibly labs. Sometimes, only very specific combinations of section choices will work out. Trying each possibility by hand is time consuming, error prone, and occasionally, entirely impractical.

What makes scheduling tools limited today? Resolving schedule conflicts is actually a lot more complex a problem than it appears at first. Resolving one conflict may result in a new conflict, resolving that one might result in another, and so on. Existing tools used very naive algorithms to compute conflict-free schedules, and the computational requirements soon grow out of control as soon as you have any engineering courses, which seem designed to create conflicts with every other course.

How can we do better? One way is to formalize the conflict-free schedule problem, and then apply standard constraint-solving and optimization techniques to solve for conflict-free schedules. This is what COURSERATOR3000 does.

The schedule conflict solver uses [Pycosat](https://pypi.python.org/pypi/pycosat) to directly calculate schedules with no conflicts. This eliminates a lot of the work in searching for non-conflicting schedules. For example, out of a search space of roughly 38,000 possible schedules in the code examples, we can solve for the 72 possibilities within 5 milliseconds.

Reducing the schedule conflicts to SAT clauses is simple. Let $$A_1, \ldots, A_m$$ be courses, each with sections $${A_i}_1, \ldots, {A_i}_m$$. Then to specify that we want one of the sections of each course, we specify the clause $${A_i}_1 \lor \ldots \lor {A_i}_1$$ for each $$i$$.

To avoid multiple sections of the same course being selected, we specify the clauses $$\neg {A_i}_x \lor \neg {A_i}_y$$ for each distinct set $$\set{x, y}$$, for each $$i$$. Now we have specified that we want one and only one section from each course.

The conflict detector is responsible for detecting every possible pair of conflicting sections. This means that we run it once over all the sections and obtain a list of conflicting pairs, which is a good thing since its time complexity is pretty bad (but still polynomial). However, in practice it completes quickly enough, helped by the fact that we only need to run it once per query.

The conflict detector outputs pairs $$\tup{ {A_i}_x, {A_j}_y}$$, which represent the idea that the section $${A_i}_x$$ conflicts with $${A_j}_y$$. For each of these pairs, we specify the clause $$\neg {A_i}_x \lor \neg {A_j}_y$$. Now we have specified that the conflicting sections cannot both be chosen.

Solving for all these clauses using the SAT solver, we obtain solutions of the form $${A_1}_x, \ldots, {A_n}_y$$ - a list of course sections that were solved for. These are the conflict-free schedules. The only thing left to do after this is display the results.

Essentially:

* User requests courses to attempt to schedule.
* Course data for each course is requested from the uWaterloo Open Data API, computing the start/end times of each individual block for each section. A simple caching mechanism cuts down on unnecessary requests.
* Conflicts are detected by looking for overlapping blocks.
* Constraints are generated from the course sections and conflicts between them.
* Schedules are solved for using PycoSAT.
* Schedules are formatted and displayed to the user.

Edit: this content is now included in the [README](https://github.com/Uberi/COURSERATOR3000#readme)!
