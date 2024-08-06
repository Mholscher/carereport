Patient medical data
====================

Diet
----

This specifies diet rules for a patient. It consists of a list of rules and the individual rules alike.
First the overview of the diet. This helps to group diet rules for the patient. A patient may have a diet for life (e.g. vegetarian) and/or a temporary diet, because of an illness.
The diet code is only used for special application. Normally each diet should have a unique name and the name will be used to show the diet on screen.

    :Diet name: A user chosen name for the diet rules combination
    :Diet code: The system supplied code for this diet.
    :Time frame: The start and end date of a diet or “permanent”, meaning either really permanent or until an unspecified end date.

Each diet will have one or more rules. The individual rules contained in the diet are specified by:

    :Food identification: The name of the food type (vegetable, pork, milk based etc.) that the rule applies to
    :Application type: The patient needs this type of food, may not have it or should have in a maximum or minimum quantity
    :Description: A text description of the content of the rule
    
Medication
----------

Medication holds records for each medication the patient uses. This is not a prescription which will serve as a trigger for the pharmacist to deliver medication. It serves as an overview of medication taken by the patient currently and in the past.

    :Medication: The name of the prescribed medication.
    :Frequency and strength: The frequency which the medication is to be taken/administered
    :Start date: First date the medicine is to be taken
    :End date: If applicable: end date of the medication
    
    
