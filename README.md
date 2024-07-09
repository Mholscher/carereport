# carereport - administrating health care #

Carereport is a system for administrating health care. It does so under strict constraints. These constraints are:

-   Carereport is about the data for health care professionals. The professional will be maintaining the date about the patient and their own and their colleagues work in the way the professional sees fit.
-   The patient data is what is being maintained. To ease work, the user will choose a patient and, until a new patient is chosen, all data shown and input will be for this patient.
-   Of course there is also important data around the professional. Think of: where am I working today, which patients are in my care? This is a separate department, apart from the individual patient.
-   Carereport does not order any action for the professional. The system is there to record data about the patient and the professional, not having any knowledge about what to do next.
The system will provide help when entering data. It will search for terms already there in the date and propose these, like a spellchecker in a word processor. As it will only use words already in the database, in the beginning there will be no suggestions.
-   Because there are hardly any links between data items, it is very well possible to not use parts of the system. For example if there are no patients on a care department, no ward/room information needs to be maintained. Exceptions will be logical, like there needs to be an examination request (what do we want to examine) to obtain a result.

Carereport is a hobby project and is developed using Python 3.11 and mariadb for the database. Care is taken to use little constructs for this specific combination, but it is not tested. You can try other databases and Python versions, but things may fail. 
