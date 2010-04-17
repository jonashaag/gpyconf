Model, View, Controller --- architecture theory
===============================================

In it's basic architecture, gpyconf follows the MVC paradigm. This section
explains the basic idea behind the Model, View, Controller pattern and
points out in what way gpyconf follows that pattern.

If you're familiar with the MVC idea, you can confidently skip the very next
subsection.


The MVC pattern
---------------
The MVC pattern is commonly used architecture pattern for software.
It separates business logic and database *Models* from the end-user *View*
(like a :abbr:`GUI (Graphical User Interface)` application or a web interface).
To connect those two components, a *Controller* is used.

Take a web service like `Twitter <http://twitter.com>`_ for example:
The database containing tweets and user data records represents the *Model*,
while Twitter's web site users use to communicate represents the *View*.

The resulting advantages are great: Every component can be used independently.
(Which is, basically, the idea behind
`Modularity <http://en.wikipedia.org/wiki/Modularity>`_.)

Basically, a MVC-based software runs through an operation sequence like this:

1. The user gives some input to the View/frontend
   (e.g., clicks on an :guilabel:`Add to shopping cart` button)
2. The frontend informs the Controller about that action
   (mostly this communication is handled using signals)
3. The controller decides what to do with that input
4. In this case, the Controller tells the Model/database backend about
   that purchase
5. The backend decides what to do with that information
   (in our case, it stores that information for further interactions)
6. (*Optional*) The Controller tells the frontend to update the presentation
   (e.g. because the total of sums of all offered products changed)
7. (*Optional*) The frontend updates the presentation with the information
   given by the Controller.
8. The frontend waits for further interactions by the user or signals by
   the Controller component (which restarts the cycle)

At first sight this appears to be an gratuitous complication to have, but it
makes sense if you're planning to replace one of the three components.
For example, it is very common to replace the View component with another one
or to have two or more frontends.

Look at our Twitter example: If Twitter wouldn't follow the MVC pattern,
no 3rd-party-clients (like all that iPhone and IM-like software) would exist,
because Twitter couldn't offer an
:abbr:`API (Application Programming Interface)` (which is, strictly speaking,
a View, too).

You can see that writing your software based on the MVC pattern is a nice thing
to have, but let's face the facts: It's a huge effort for programmers to
implement the Model, View and Controller components completely independently
(think about all the abstraction layers, the communication and all that stuff).
Therefore, the very vast majority of (modern) software declared as MVC software
does not *strictly* follow the MVC pattern. And so gpyconf does.


gpyconf's architecture
----------------------

As told before, gpyconf (more or less) follows the MVC pattern. It's
architecture is splitted in Model (your configuration option definition),
backend (which stores the options, e.g. into a file or in a database),
frontend (interaction with your users, typically using a configuration dialog)
and Controller (which connects the mentioned components and presents the
interface to you, the application developer). As communication between those
components, signals are used (see the :doc:`signals` section for more about
this).

The following digraph illustrates this architecture.

.. graphviz::

   digraph {
        rankdir=LR;
        User -> Frontend [color="#DCA133", label="interacts with"];
        Frontend -> Controller [color="#1AD41A", dir=both];
        Controller -> Backend [color="#1AD41A", dir=both];
        Developer -> Model [color="#8B6914", label="defines"];
        Model -> Controller -> Backend [color="#8B6914"];

        Model[shape=plaintext];
        User[shape=rect];
        Developer[shape=rect];
        Frontend[shape=circle];
        Backend[shape=circle];
        Controller[shape=doublecircle]
   }

In words: You -- the developer -- define your configuration model
(using :doc:`fields <fields>`). Every configuration option represents a
primitive (:class:`bool`, :class:`string`, :class:`int` etc) or non-primitive
(:class:`list`, table) datatype. The :class:`gpyconf.Configuration` class passes
this model definition the backend and the frontend. The backend reads stored
values from it's storage (file, database, ...) and passes them to the Controller
class. The Controller class updates the field's values with that new value.
Then, if the frontend is runned (*Running the frontend* means, for example,
building up the GUI and showing a configuration dialog window), and the user
interacts with that frontend (e.g. changes a field's value or presses the
:guilabel:`Save` button), the configuration class decides what to do next.
Let's say, for example, the user pressed the :guilabel:`Save and close` button.
The Controller class should now make the backend save the field's values and
then "shut down" the frontend.
