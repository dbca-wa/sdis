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
========================================
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
Behind the scenes, SDIS creates different items when a project is created.
It is not possible to migrate the content of the different fields and documents
without the risk of data loss.
Therefore, SDIS does not allow to change project types after their creation.
If you still need to change a project type, please do:

* Create new project with the correct type. Copy/paste or re-type relevant fields.
* Ask the admins to delete the old project of incorrect type.

The admins can delete a project:

* Delete the (child-)project on the detail page, then
* delete the (parent-)project on the overview page.

SDIS requires this two-step deletion process due to a
`known bug <https://github.com/django-polymorphic/django-polymorphic/issues/34>`_
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


How can I make my project stand out?
====================================
Provide a tagline, a description, and a nice thumbnail image!

Tagline
-------
Can you sell your project in one sentence to a non-expert audience?

Description
-----------
The description is the place to explain the project in up to three paragraphs to
the interested reader, much like a publication's abstract.

Project thumbnails
------------------
Project thumbnails are used as section thumbnails in the annual report
and as thumbnails to represent the project online.

* The thumbnails should use a standard image format,
  such as JPEG (.jpeg, .jpg) or PNG (.png).
* The thumbnails should be oriented correctly. If the thumbnail
  stands on its side, edit (rotate) the original file and re-upload.
* The aspect ratio should be 3:2 to 1:1 (width:height).
* The horizontal resolution should be at least 600 pixels.
* The vertical resolution should be at least 600 pixels.
* Larger images will be resized automatically, preserving aspect ratio, to fit
  a maximum width of 600 pixels and a maximum height of 600 pixels.
* The image should not contain too much detail or too much contrast.

Background images for divisional programs
-----------------------------------------
Program images could be used as page-width chapter images in the annual report,
and as background images online.

* The aspect ratio should be exactly 2:1 (width:height).
* The horizontal resolution should be at least 2480 pixels.
* The vertical resolution should be at least 1240 pixels.
* Larger images will be resized automatically, preserving aspect ratio, to fit
  a maximum width of 2480 pixels and a maximum height of 1240 pixels.
* The horizon, if shown, should be as level as possible and in the middle or
  top third - avoid the bottom third (this is where headings will be overlaid).
* The image should not contain very dark (shady) or bright (sun glare) areas.


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
3. After the last SCMT meeting: SDIS admins (Julian/Florian) create a new ARAR when instructed to by the Directorate. This will generate Progress Reports for all active and closing ScienceProjects, all active CoreFunctions, and all active StudentProjects.

Running through updates in this order will speed up the update process considerably by preventing the confusion (as there's no staff training ahead of the ARAR process) and required subsequent individual coaching from the ARAR admins to involved staff members to back each falsely project open out of the ARAR update process.

What happens during the ARAR reporting phase?
=============================================
The general purpose of SDIS is to encourage project management through the correct approval of related project documentation, and to audit the human decisions.
However, sometimes we need to fast-track some processes and override the system. A system admin with sufficient permissions can do so.

* SDIS admins assist BCS staff with the updates and their approval. Some projects and documents get stuck and need a superuser to reset approvals.
* Given a draft of the organigram, the developer updates the print version.
* Any other changes to the report structure are applied by the developer upon request from the Directorate.

How can I exclude an unwanted regular progress report?
------------------------------------------------------
A progress report was requested in error for a project that should have been started the project closure process.

* An SDIS admin can force close the project, which deletes the current progress report, excludes the project from the annual report, generates a project closure form, and sets the project status to "closing".
* Force closing a project can be reverted if needed.

How can I exclude an unwanted "final" progress report?
------------------------------------------------------
A project with a closure form in status "closing pending final progress report" is triggered by creating a new annual report. The annual report creates the final progress report. Instead of filling in and approving the final progress report, we want to close the project and remove the last and empty (dud) progress report.

* Closure form: reset approval status, change closure goal to "completed without final progress report", and fast forward closure form approval, skipping email notifications. This pushes the project status to "completed".
* Delete the empty final progress report.

Why can't I update a progress report?
-------------------------------------
Only users added as project team members can update that project's documents, including the progress reports.

* The creator of a project is added as a team member automatically.
* Other project authors have to be added by the project's creator or an admin.

How is a project plan endorsed and approved?
--------------------------------------------
As a Program Leader, I have received a notification email about a Project Plan which needs to be approved. I cannot see the button to approve the project plan but I'm not sure why.

* SDIS shows in the sidebar whether the endorsements of Biometrician (always required), the Herbarium Curator (if plant specimen collection involved) and the AEC (if animal handling involved) are required.
* Any SDIS user who is part of the Group "BM" / "HC" / "AEC" can set the endorsement field inside the main document to "Granted" or "Denied", then save.
* Once endorsements are given, the Program Leader will be shown the "approve" button, which sets the project to "active" without the need for additional Directorate approval.

How can I change how project team members are shown in the team list?
---------------------------------------------------------------------
To change a project team member's affiliation (and update the cached version):

* Staff > Browse SDIS users > User details, (e.g. field "Affiliations" > update affiliation "Curtin University") > Save User.
* Left column shows user's projects (where the users occur on project teams) > open each project in a new tab.
* Each project: Manage Team > "edit" membership > save. This updates the cached project team list.
* Update all (admins only): Backstage > update caches.
