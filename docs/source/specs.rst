************************
Functional Specification
************************

User roles
==========
There are many things that can be done with projects and documents, but some
actions are only available to a restricted audience and/or only at certain times
or under certain circumstances.

SPMS's philosophy is to be permissive, but log everything.
The point of truth for project approval is the SCMT; necessarily, SPMS will always
require to be brought up to speed with the latest SCMT decisions.

After 4 years of development and honing workflows and user interface,
SPMS implements all known SCD rules and
workflows around project approval. If things go to plan, SPMS will
show "the right buttons" to allow appropriate actions.

SPMS features a role-based permission system, based on three roles:

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

Only team members of a project can update a document and execute any life cycle steps, such as
submitting related documents for review, or requesting closure.

**Only DPaW staff are notified** when the team is emailed. SPMS leaves prompting
contributions from external collaborators to personal communication as (and when)
appropriate by DPaW staff.

Program Leaders
---------------
Members of SCMT (all Program Leaders) have the permission to "review".
This allows them to review documents (Concept Plans, Project Plans,
Progress Reports, Closure Forms, Student Reports), update them if appropriate,
and submit further up the approval chain, or request updates from the authors.

Program Leaders can review other programs' projects as well, because:
* some projects are registered under one SCD program, but administered under another
* PLs can stand in for each other
* we assume (as everything is logged), that no PL will act without SCMT's approval

Program Leader permissions are global (for all projects and documents).
**Only the direct Program Leader is notified** when actions from reviewers are
requested. SPMS leaves the edge case of prompting another PL for input as (and when)
appropriate to the directly involved and notified PLs.

Directorate
-----------
Representatives of the SCD Directorate (e.g. Director's EA) have the
authority to approve documents, or manage annual reports such as the ARAR.
Approval of documents will reflect the decisions of the SCMT and Directorate,
and will cause projects to proceed in their life cycle.

Directorate permissions are global (for all projects and documents).

**Only explicitly nominated representatives of the Directorate are notified** when
actions from the Directorate is required.


Special Roles
-------------
Project Plans require endorsement of the Biometrician (mandatory),
the Herbarium Curator (if plants are collected), an Animal Ethics
representative (if animals are involved), and (soon) the Data Manager (to setup
the project's data management).

Special Roles will find Project Plans requiring their endorsement in their Tasks,
and will receive an email when a new Project Plan requires their attention.

For each Project Plan, the following should happen:

* SPMS sends an email when the Project Plan is created
* BM reads the "Methodology" section, discusses with team as required
* HV reads the "No. specimens" section, discusses with team as required
* Soon: DM trains team to create datasets on the
  [Internal Data Catalogue](http://data.dbca.wa.gov.au), sets them up
  with a high performance computing (HPC) environment if required, and points out
  documentation on data management.
* The Program Leader enters AE endorsement as per (external to SPMS) communication
  with the Animal Ethics Committee.
* Endorsement is granted or denied by setting the respective "endorsement" fields
  in the Project Plan to "granted" or "denied", respectively, and saving the document.
  This action is logged in the document history.
* The Project Plan can only proceed in its life cycle once all required endorsements
  are granted.

**Note** Special Roles are granted the privilege to edit Project Plans even after
these have been approved, in order to facilitate their adding of endorsements where
required.


Project Life Cycles
===================

This section goes into the full detail about the supported Project types and their life cycles.
In a nutshell, Project approval in SPMS is like playing a board game.
Newly created projects spawn documents, which have to be filled in and sent through their own
approval work flow. Approval of documents advances projects to new life cycle stages.

.. _project_lc:

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

.. _document_lc:

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

Publication approval
====================

Publication types
-----------------
Definition: Media released publicly or internally with a defined approval process


* peer reviewed journal articles
* reports
* conference abstracts
* posters
* info sheets
* fact sheets
* book chapters
* all endnote publication types?
* social media posts (involves Zoran and Margaret)
* Threatened fauna and flora recovery plans
* Translocation proposals


step 1: review by PL
step 2: review by A/Dir


Publication
-----------
External, possibly peer-reviewed, publication:

* Peer-reviewed paper
* Report

Commonality: Public document written in the affiliation of DPaW.

* Author compiles draft
* Author discovers publication approval guideline
* Author reads publication approval guideline
* Guideline requests author to seek informal feedback from Project leader
* Publication may link to SPP
* Author starts online publication approval process (creates form):
    * manuscript ID (auto) MS-YYYY-NNN
    * title
    * synopsis (plain english)
    * management implications (text)
    * author team (text, not User)
    * manuscript (file)
    * attachments (file) x n
    * related projects (text): SPMS projects, non-SPMS projects
    * formatted citation
    * RIS (text)
    * DOI
* Author submits form ("in review"), which opens checkbox: notify (depending on required roles)
  PL, BM, HerbC (if plants)
  but not Fauna folks (if fauna), plus possibly other roles.
* Approval roles:
    * PL
    * BM
    * HC (if "involves plant taxonomy")
    * possible other roles
* Approval roles may choose to litigate feedback from higher roles via "send email"
* Approval roles see open publications in "My Tasks"
* "Seek external feedback" creates email with blank recipients and attaches whole manuscript and attachments
* "Seek internal feedback" creates email with blank recipients with only a link to pub approval detail page
* "Seek author feedback" creates email to author with link
* Author can update manuscript any time while "in review"
* Author can "re-submit" the publication, which sends an email notification to
  reviewers pending endorsement
* Reviewer roles other than PL endorse, which sets flag and sends notification to other roles
* PL approves (status "approved")
* Once all approvals are given, author gets notified to submit manuscript
* Author and PL can "retract" at any time (status "retracted")
* Authors can "delete"
* Author goes through publication process with publisher
* If successful, author attaches final manuscript, DOI, citation and presses "published"
* "published" notifies librarian with citation
* ARAR builds publication list from "published"

REQ Publication guideline must be discoverable
REQ Updated guidelines relevant to SPMS need to be published
REQ Publication has authors

TODO should we retain deleted forms?


Recovery plans
--------------
RP are a tool to identify actions needed to improve the conservation status of
exactly one species (fauna or flora).
State RPs cover 10 years, interim RPs cover 5 years.

The review and approval process exists to ensure and audit that the plan:

* is achievable,
* is correct from the reviewing role's perspective, and
* conforms to relevant corporate policy.

Model fields
------------
* document - file
* for each role: involves_X (y/n), determines whether role needs to review
* for each role: endorsed by role Y, editable only to members of role
* citation metadata as required
* authors - either plain text or SPMS user list

Life cycle
----------

* RP is prepared by staff member who keeps working version on their desk.
* RP is uploaded to SPMS as read-only PDF copy.
* User provides criteria which determine required review roles.
* SPMS shows document as "draft".
* User submits document for review and approval.
* SPMS shows document status as "in review".
* SPMS notifies each involved role by email containing instructions and URL.
* Each role can follow URL in email to RP and read the plan.
* Each role can choose to provide feedback, which opens an email to author allowing
  the reviewer to provide private, direct feedback to author.
* Prompted by reviewer feedback or by own volition, authors can update the document
  and (during saving) opt in to notify reviewers pending endorsement.
* Any reviewer content with document can endorse
* Certain reviewer roles will only be notified by email once other roles have
  endorsed the document:
* In parallel: district, regional staff, spec & comm branch, pricipal zoologist
  or botanist),
* then Manager Species and Comm Ken Atkins
* then A/Dir Conservation
* If nationally threteaned species in other (interstate) jurisdictions, the
  document is sent (external to SPMS) to Commonwealth who have their separate process.
* If Commonwealth agencies are involved, their feedback is handled by (TODO insert role here).
* Once all reviewers have endorsed, email notification for approval is sent to Dir SCD.
* SPMS shows document as "in approval".
* Dir SCD can either provide feedback via email, or approve.
* SPMS turns record read-only to prevent tampering and shows document as "approved".
* SPMS notified librarian of approval, sending URL, citation and document.
* Document is filed and released to public (both external to SPMS).

Questions
---------

* Where is the point of truth for the approved document?
* SPMS should rename "PL" to accommodate "Branch Manager", eg. "PL or BM"

Translocation proposals
-----------------------

* written by staff, staff and external person, rarely only external
* endorsement process depends on origin and destination of animal to be translocated
* endorsed by principal zoologist or senior botanist
* endorsed by animal ethics committee (Manda Page will know)
* endorsed by Manager Species and Comm Ken Atkins
* endorsed by A/Dir Conservation
* approved by Dir SCD
* publication to intranet (?) and filing

Roles
-----

* TODO: fill from above
