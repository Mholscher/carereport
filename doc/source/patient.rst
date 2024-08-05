The patient
===========

This object serves a dual purpose. On the one hand it holds and maintains the data for a patient, like address and birthdate, on the other hand it is identifying the patient for the objects that are linked to one patient.
Strictly also the items as address and birthdate should be objects, but these are considered not specific for medical purposes. If this turns out to be an incorrect premiss, we will add these to the candidate list.
Patients will generally not need all of the dependent objects listed here. For some (like medication) it is possible to have more than one applicable object.
Not specific objects:
    
    +------------------------+-----------------------------+
    | Item                   |Description                  |
    +========================+=============================+
    | Patient name           | The surname of the patient  |
    +------------------------+-----------------------------+
    | Patient initials       | Initials of the patient     |
    +------------------------+-----------------------------+
    | Birthdate              | Birthdate of the client     |
    +------------------------+-----------------------------+
    | Sex                    | Patient sex, not required   |
    +------------------------+-----------------------------+
   
