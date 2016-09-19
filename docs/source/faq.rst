**************************
Frequently Asked Questions
**************************

Many questions will be covered by the instructions in :doc:`quickstart`.

Where are my projects?
======================
The `SDIS home page <https://sdis.dpaw.wa.gov.au/>`_ will display projects
you supervise or participate in under "My Projects".

Note:

* "My Tasks", "My Projects", and "My Collaborations" expand/collapse when clicked on.
* A black star indicates that you lead the project as "project owner".
* A hollow star indicates that you are part of the project team.

Where can I search for other projects?
======================================
The "Browse all Projects" allows you to filter projects by any of the columns.
Click on any of the column headings to sort or filter the list.
You can type to filter the dropdown menus!

"Browse all Projects" is also available in the top menu bar under "Projects".

Which projects will be discussed at the next SCMT meeting?
==========================================================
On the `SDIS home page <https://sdis.dpaw.wa.gov.au/>`_, in the "Projects" section,
click "View xxx projects awaiting SCMT approval" to expand a list of project
documents (Concept Plans and Project Closures) awaiting SCMT approval.

This selection is of particular interest to SCMT members as pre-read for the SCMT meeting.

Is there anything SDIS wants *me* to do?
======================================
If there are any documents awaiting your input, and possibly any approval actions,
they will be shown on the `SDIS home page <https://sdis.dpaw.wa.gov.au/>`_ under
"My Tasks". Click each link, update the content as appropriate, save the changes,
and if appropriate, execute any approval steps shown under "Actions".

Note: Save your changes to documents before leaving the page or executing any actions.
Make sure you leave the active fields by clicking outside before saving!

Why can't I submit my project's related documents for review, or request project closure?
=========================================================================================
Only project team members can execute these life cycle steps. If you can't, but
feel you should be able to, an existing project team member has to add you to the
team.


How can I change the project type?
==================================
Oh no! I've created a project which turned out to be of a different type.
The project creation form said "the project type cnanot be changed later on" but
this is what I need to do now.

Behind the scenes, SDIS projects are quite different, and SDIS creates a few
different items when a project is created. Therefore, it is not possible to
change project types later on. If you still need to change a project type:

* Create new project with the correct type. Copy/paste or re-type relevant fields.
* Ask the admins to delete the old project of incorrect type.

The admins can delete a project:

* Delete the (child-)project on the detail page, then
* delete the (parent-)project on the overview page.

SDIS requires this two-step process due to a
[known bug](https://github.com/django-polymorphic/django-polymorphic/issues/34)
in one of its third party libraries.

Why can't I update my project or edit documents?
================================================
You need to be on the project team to have write permission to the project or
its documents.
Furthermore, only "new" documents are editable - that's when the project
team is meant to fill in the document. Once a document is submitted for review to
the Program Leader ("reviewers"), only they can edit it. Once a document is
submitted to the Directorate ("approvers"), again only they can edit it.

If you wish to update a document sitting with your Program Leader "in review",
you can "recall" it from review, edit it, and resubmit it for review.

Can I download documents?
=========================
You sure can! The "View PDF" link above each document will create a beautifully
laid out PDF with a cover page indicating its approval status and project details.
The PDFs have links in the page headers back to their online counterparts in SDIS.

The "Create PDF" link does not work
===================================
Likely there's some invisible markup in at least one of the document's fields.
This can happen if the content has been copy-pasted from MS Word, EndNote, or
web pages.

Cut and paste the content into a simple text exitor like Notepad, then back into
SDIS to remove this invisible markup.
*Do not* use "clever" text processors like MS Word, as they
"understand" and preserve the invisible markup we want to get rid of.
*Do* use simple text editors like Notepad, which actively discard invisible markup.

What will happen when a new ARAR is kicked off?
===============================================
A new Annual Research Actitivy Report (ARAR) is created every year. It will request
updates from all Science Projects, Core Functions, and Student Projects.
It will include project level details from all existing External Collaborations.

* You will get one broadcast email when the ARAR process starts.
* SDIS will not email you separately for progress reports
* SDIS will show any progress reports requiring your input under "My Tasks"

Before the ARAR gets kicked off, make sure to get your things in SDIS up to date:

* Create new projects, start their approval process
* Close old projects (some will have a closure process incolving document approval)
* Update team lists on projects.

This will prevent SDIS from unknowingly requesting updates from long dead projects
(which create extra effort to get rid off again).

Can I provide ARAR updates before the new cycle begins?
=======================================================
No, not really - only kicking off a new ARAR cycle will create the documents
you need to update. They simply don't exist earlier.
If you need to provide early updates (e.g. because of field work), use the latest
progress reports as starting point (copy out the text), and email the new version
to Florian.

What happens in the last weeks before a new ARAR comes around?
==============================================================
The ARAR update process has three phases, relative to the last SCMT meeting before
the ARAR process starts. (This meeting has the power to approve requested project closures).

1. Before the last SCMT meeting before the ARAR: PLs and Scientists review their projects, request closure / termination / suspending where required, and update the team lists.
2. At the last SCMT meeting before the ARAR: SCMT discusses and approves/rejects Project Closure documents, and terminates / suspends projects as appropriate.
3. After the last SCMT meeting: SDIS admins (Paul/Florian) create a new ARAR when instructed to by the Directorate. This will generate Progress Reports for all active and closing ScienceProjects, all active CoreFunctions, and all active StudentProjects.

Running through updates in this order will speed up the update process considerably by preventing the confusion (as there's no staff training ahead of the ARAR process) and required subsequent individual coaching from the ARAR admins to involved staff members to back each falsely project open out of the ARAR update process.
