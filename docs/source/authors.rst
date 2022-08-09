.. _authors:

************************
Project owners and teams
************************

This chapter guides project owners and their teams through their tasks.

Project owners are those who register a Project in SPMS to get departmental approval.
They have to author documents and submit them for approval.

Complete your Profile
=====================
* Follow the link "My SPMS Profile" in the main menu underneath your name.
* Update your Profile and save.

Create a Project
==============================
* Choose the Project type - you cannot change the type later on.
* Fill out Project details. See the FAQ for guidance on thumbnail images, and read the helptext of the form fields.
* Next, add colleagues to the Team list, and fill out the first Document, the Concept Plan.

Oops, wrong project type - now what?
====================================
For technical reasons, you cannot change the type of a project once it has been created.

* Create a new project of the correct type.
* Deleting projects is limited to SPMS admins.
  Notify an SPMS admin to delete the Project of incorrect type.
  Use the "Share" link to create an email containing direct links to the respective Project or Document.

The reason we restrict deletion of Projects is to retain the history of past Projects.
It would be an easy error to make to delete a Project on completion. 
Instead of being deleted at the end of their active life, Projects go through a formal closure process, 
creating yet more documentation (reasons, outputs) that adds to the history of the Project.
Completed projects are kept with status "Completed and closed".

Ask a question about a Project or Document
==========================================
Each Project and Document has a "Share" button. 
This button opens an email containing a direct link to the Project or Document in question.

Opening a direct link is much faster for the receiver than to hunt through SPMS, 
searching by project year, number and/or title.

Onboarding a DBCA colleague to SPMS
===================================
SPMS maintains a list of User profiles with all the details we need for reporting and display purposes.

SPMS automatically creates a User profile when a new User visits SPMS for the first time.

The profile then needs some more information (full names, affiliations, DBCA Program) which the Users can enter themselves.
SPMS does not receive enough information from DBCA's login system to automatically set the Program, so the User has to set this manually.
Setting the Program will infer the User's Division, which in turn drives the SPMS User experience - 
BCS staff have more documentation and reporting features available than other Divisions.

Add DBCA colleagues to a Project Team
=====================================
* If the colleague is new to DBCA, assist them through the onboarding outlined above. Primarily, prompt them to visit SPMS once.
* The DBCA colleague must have visited SPMS prior to that in order to be known to SPMS.
  They should also update their profile so SPMS gets their name and title right in Team lists.
* At the Project's detail page, click on the "Add team member" button to select any DBCA colleague.
* Only Project Team members can update Documents.
* Project Team members can add others to the Team.

Caveat: you cannot add a DBCA colleague to a Project Team until they have visited SPMS at least once.

Add an external colleague to a Project Team
===========================================
To add external colleagues to a Project Team, they also require an SPMS profile. 
There's only one little catch - they can't access SPMS (yet) being external to DBCA.
Therefore, you will have to create a profile for them.

* At the Project's detail page, click on the "Register an external colleague" button to create a new User profile for them.
* As username, choose their ``givenname_surname`` in all lower case and separated with an underscore. DO NOT use your own email address here.
* As password, choose any password of your choice. The external user will never login and never need this password. 
  Having a password is a requirement of the software framework SPMS is written in. Set and forget!
* Enter profile details and save the profile.
* Once you have created and saved the new SPMS User profile, you can add them to the Project Team via "Add team member".
* Student Projects and External Partnerships often have external colleagues.

Caveat: External colleagues will never need to login to SPMS, and do not need to know about this profile.

Document visibility
===================
* Currently, only BCS staff are meant to see Project Documents. 
* Members of other Divisions will see no reference to Documents and are not required to fill in any Documents. Less work!
* If you however think you should see more or less Documents than you currently do, please get in touch with the administrators.

Complete and submit a Document
==============================
This section applies generally to any SPMS Document.

* Click on any field to enable a rich text editor.
* Follow the guidance in the helptext of the form fields.
* When done updating a field, make sure to click outside of the editable area to close the editor and save the changes to that field.
* Once all fields are updated, finish editing the document by clicking on the "Save" button at the bottom. 
  This saves changes to all fields. Make sure you've closed any active editors by clicking outside.
* You can view the edit history through the "History" link at the top, and restore older versions if needed.
* Documents are editable only to those involved (Project team members as per the Project overview, reviewers, approvers), 
  and only when it is their turn to provide input.
* If a Document is read-only, you should not have any reason to update it. If that seems wrong, contact the admins.
* Read-only Documents show the text content including the embedded formatting markup (HTML directives like ``<style>``). 
  Text pasted directly from a MS Word document with track changes enables looks particularly bad.
* In the rich text editor, use the "Source View" button to hand-edit content, and "Clear Formatting" to reset most unwanted style.
  If the source view shows much unwanted formatting markup, paste the text into a plain-text editor like Notepad 
  and back into SPMS to get rid of invisible formatting markup.

In general, SPMS wants formatting to be restricted to the styles provided by its embedded rich text editor.
Start with unformatted text, then format content in SPMS.

Register your Data
==============================
* Once the Concept Plan is approved, the Project is near guaranteed to be approved. Now it is time to set up data management.
* Create an account on the `Data Catalogue <https://data.dbca.wa.gov.au/>`_ (with its own password - NOT your DBCA password).
* Contact the Data Catalogue admin for write access to your Program(s). 
  They will add you to as "members" of the Data Catalogue "Organization" corresponding to your DBCA Program (or equivalent).
* Create initial metadata entries for all expected datasets on the Data Catalogue.
* Label them with your project code, e.g. ``SP-2022-001``.

Provide a Progress Report
==============================
* When an annual report requires an update from your Project(s), you will receive a broadcast email ahead of time, 
  and find any ProgressReport Documents in your TODO list.


Close a Project
==============================
* The months before annual reporting are a good time to initiate project closure for any completed or otherwise finished projects.
* You can close a Project by clicking on the "Request Closure" button on the Project's detail page. This generates a Project Closure Document.
* Fill out and submit the Project Closure Document for review.
* There are several flavours of Project Closure determining what comes next:

  * The Project was completed successfully, and all progress was reported in the last annual report. There is no need for a final Progress Report.
  * Same, but some progress was made after the last annual report. A final Progress Report is required.
  * The Project is suspended. No Progress Report will be required. The Project might be resumed later.
  * The Project is terminated. No Progress Report will be required.
* Update the Project's datasets on the Data Catalogue. 
  This is the last time someone with intimate knowledge of the data is around to do so. 
  This preserves the Project's data outputs, and your name will live on in the metadata.

Find Help
==============================
The following steps aim to solve any problems. Ideally they are followed in this sequence:

* Read this documentation carefully.
* Consult the :doc:`faq`.
* Ask the admins.
* If you think you've encountered a bug, feel free to open an `issue here <https://github.com/dbca-wa/SPMS/issues>`_.
* If you feel that the documentation is missing something, or is unclear on something, your feedback would be highly appreciated and will help us to improve the documentation.