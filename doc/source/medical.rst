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
    
Examination request
-------------------

To be able to set a diagnosis, patients have to have examinations. These may entail taling an analysing blood samples, x-rays and/or scans. Specialist departments will be executing these examinations, so there has to be a way to request these. This item documents such a request. 

    :Date of  request: Date the request was made
    :Kind of examination: The sort of examination requested
    :Department: The department that will execute the examination
    :Requester: The department and official requesting the examination
    :Date of execution: The date the request was taken on
    :Request refusal: The request was refused, the reason will be in this field
    
Examination result
------------------

This is the result of the examination. It links to a request, unrequested examinations cannot exist.

    :Examination  request: The request that was fulfilled to get this result
    :Examination results: The result of the examination, in descriptive text form.
    :Examination executor: The person to be contacted for inquiries on this result.
    
    
