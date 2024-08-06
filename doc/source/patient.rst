The patient
===========

Patient identification
----------------------

This object serves a dual purpose. On the one hand it holds and maintains the data for a patient, like address and birthdate, on the other hand it is identifying the patient for the objects that are linked to one patient.
Strictly also the items as address and birthdate should be objects, but these are considered not specific for medical purposes. If this turns out to be an incorrect premise, we will add these to the candidate list.
Patients will generally not need all of the dependent objects listed here. For some (like medication) it is possible to have more than one applicable object.
Not specific objects:
    
    :Patient name: The surname of the patient
    :Patient initials: Initials of the patient
    :Birth date: Birth date of the patient
    :Sex: Patient sex, not required

Intake
------

This object specifies what we need to create a patient. It will accept the data which is at the patient level (through a dedicated patient screen) and allow the user to switch to the other items that are applicable at intake. The intake object is very simple.
Once a patient is created, it is possible to select this patient and create a new intake. So, to be able to maintain a patient history, users should reuse patients whenever possible. The intake is the starting point of a (new) treatment.

    :Date of intake: The date at which the intake took place
    :Result of intake: The patient was admitted, or refused, or admitted at some later time, or an appointment was made 
    :Result key: What the key(s) are to the result (appointment etc.) of this intake. Intakes may not have any key to a separate result.
