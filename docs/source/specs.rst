************************
Functional Specification
************************

User roles
==========
There are many things that can be done with projects and documents, but some
actions are only available to a restricted audience and/or only at certain times
or under certain circumstances.

SDIS's philosophy is to be permissive, but log everything.
The point of truth for project approval is the SCMT; necessarily, SDIS will always
require to be brought up to speed with the latest SCMT decisions.

After 4 years of development and honing, SDIS implements all known SCD rules and
workflows around project approval. If things go to plan, SDIS will
do, show, and allow "the right buttons", or appropriate actions.
But sometimes, we need a shortcut, or things don't follow the rules. In this case,
rather than blindly enforcing the rules (we did that, and it was more hassle
than worth), SDIS will allow privileged users to override business rules and
e.g. force-choke projects to death, or kill zombies (back out of Progress Reports
that were requested for projects that should have been closed).

SDIS features a role-based permission system, based on three roles:

Project teams
-------------
Team members and holders of project roles have the "submit" permission
for their respective project and its related documents. This allows them to
execute approval actions, e.g. submitting a document for review, or requesting
project closure.

Project roles are Project Owner, Data Custodian and Site Custodian.
All three default to the creator of a new Project, but can be updated at any time.
The Project Owner is added as "Supervising Scientist" to the project team when
a project is created. The Project Owner, and any other team members, can add/edit
Team membership.

While every logged in SDIS user can update any document (these updates are logged),
only team members of a project can execute any life cycle steps, such as
submitting related documents for review, or requesting closure.

Project team permissions are updated whenever a project team member gets added
or removed, or when a new document is added. Permissions are given to all team
members for the project (e.g. to request closure) and all related documents.

Program Leaders
---------------
Members of SCMT (all Program Leaders) have the permission "review".
This allows them to review documents (Concept Plans, Project Plans,
Progress Reports, Closure Forms, Student Reports), update them if appropriate,
and submit further up the approval chain, or request updates from the authors.

Program Leaders can review other programs' projects as well, because:
* some projects are registered under one SCD program, but administered under another
* PLs can stand in for each other
* we assume (as everything is logged), that no PL will act without SCMT's approval

Program Leader permissions are global (for all projects and documents).

Directorate
-----------
Representatives of the SCD Directorate (e.g. Director's EA) have the
authority to approve documents, or manage annual reports such as the ARAR.
Approval of documents will reflect the decisions of the SCMT and Directorate,
and will cause projects to proceed in their life cycle.

Directorate permissions are global (for all projects and documents).


Project Life Cycles
===================

This section goes into the full detail about the supported Project types and their life cycles.
In a nutshell, Project approval in SDIS is like playing a board game.
Newly created projects spawn documents, which have to be filled in and sent through their own
approval work flow. Approval of documents advances projects to new life cycle stages.


Science Projects and Core Functions
-----------------------------------
.. image:: https://www.lucidchart.com/publicSegments/view/958f90d2-acd3-46c3-984f-95767bfb52aa/image.png
   :alt: Science Project Life Cycle

Science Projects have

* a two-stage approval process,
* annual reporting requirements,
* a two-stage closure process, and
* a few admin shortcuts to force-choke projects into the correct status.

Core Functions have the same documentation as Science Projects, but as ongoing
Divisional business, have no formal approval or closure process.

Science Project Approval
~~~~~~~~~~~~~~~~~~~~~~~~
* Create new Science Project
* Update and submit ConceptPlan
* ConceptPlan approval creates ProjectPlan
* Update and submit ProjectPlan
* ProjectPlan approval activates Project


Science Project Annual Reporting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Users get one central email broadcast about Annual Report
* Users find all Progress Reports requiring their input in "My Tasks", update and submit them
* If an update is rejected, it will turn up in "My Tasks" again


Science Project Closure
~~~~~~~~~~~~~~~~~~~~~~~
There are many ways to retire a ScienceProject.

* Submitters (and their line management) can "request closure" on active projects
  to create a Project Closure form:

  * "Request closure" button creates Project Closure document;
  * Approval of Project Closure document advances the project to status "Closing pending final update";
  * The next ARAR will create a final Progress Report;
  * Approval of the final Progress Report will close the project.

* Approvers can force-choke any project into closure from almost any active state.
* Approvers can terminate or suspend active projects to reflect a change in strategy,
  take a project out of the circulation without due closure process.

All steps are reversible.

External Partnerships
---------------------
Partnerships have no approval or closure process, and require no separate annual updates.
Simply registering, updating project details every now and then,
and closing them as required will be enough.

Student Projects
----------------
Student Projects have no approval workflow or closure process, but require
simple annual progress reports.

Progress reports requiring your input will turn up in "My Tasks" as well.


Document Life Cycles
====================

.. image:: https://www.lucidchart.com/publicSegments/view/131bad06-80e1-465f-af8e-07e0b491186c/image.png
   :alt: Document Life Cycle

All documents share the same approval work flow:

* Submitters (project team) update the content, then submit for review.
* Reviewers (project's program leader) reject or submit for approval.
* Approvers (Directorate) reject (to reviewers or submitters) or approve the document.
* Approvers can reset the document to "new" and fast-track it through its approval stages.

Document approval will often advance their project to a new stage.
Revoking document approval will return the project into the previous stage.

The individual documents differ only in the actions caused by their approval.
