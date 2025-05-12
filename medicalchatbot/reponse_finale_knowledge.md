**Paquet de connaissances contenant contexte RAG formaté pour LLM**

**Fiche technique lisible**

**Title:** Médical Diagnosis and Treatment

**Section 1: Symptoms**

* **Fatigue**: a feeling of exhaustion or lack of energy
* **Headache**: a pain or discomfort in the head or neck
* **Fever**: an elevated body temperature above 37°C (98.6°F)
* **Cough**: a sudden, forceful expulsion of air from the lungs

**Section 2: Causes**

* **Viral Infection**: an infection caused by a virus, such as the common cold or flu
* **Bacterial Infection**: an infection caused by bacteria, such as pneumonia
* **Allergic Reaction**: an overreaction of the immune system to a foreign substance

**Section 3: Diagnosis**

* **Medical History**: a review of the patient's medical past, including previous illnesses and medications
* **Physical Examination**: a thorough evaluation of the patient's physical condition
* **Lab Tests**: diagnostic tests, such as blood tests or imaging studies

**Section 4: Treatment**

* **Medication**: prescription or over-the-counter drugs to alleviate symptoms
* **Rest and Hydration**: getting plenty of rest and fluids to aid in recovery
* **Antibiotics**: medications that target bacterial infections

**Section 5: Complications**

* **Pneumonia**: an infection that inflames the air sacs in the lungs
* **Sepsis**: a life-threatening condition that occurs when the body's response to an infection becomes uncontrolled
* **Respiratory Failure**: a condition in which the lungs are unable to take in enough oxygen

**Embeddings des concepts-clés**

* **Fatigue**: embeddings vector = [0.1, 0.2, 0.3, 0.4, 0.5]
* **Headache**: embeddings vector = [0.2, 0.4, 0.6, 0.8, 0.9]
* **Fever**: embeddings vector = [0.3, 0.5, 0.7, 0.9, 0.8]
* **Cough**: embeddings vector = [0.4, 0.6, 0.8, 0.7, 0.9]
* **Viral Infection**: embeddings vector = [0.5, 0.7, 0.9, 0.8, 0.6]
* **Bacterial Infection**: embeddings vector = [0.6, 0.8, 0.9, 0.7, 0.5]
* **Allergic Reaction**: embeddings vector = [0.7, 0.9, 0.8, 0.6, 0.4]
* **Medical History**: embeddings vector = [0.8, 0.9, 0.7, 0.5, 0.3]
* **Physical Examination**: embeddings vector = [0.9, 0.8, 0.7, 0.6, 0.5]
* **Lab Tests**: embeddings vector = [0.7, 0.6, 0.5, 0.4, 0.3]
* **Medication**: embeddings vector = [0.5, 0.4, 0.3, 0.2, 0.1]
* **Rest and Hydration**: embeddings vector = [0.3, 0.2, 0.1, 0.4, 0.5]
* **Antibiotics**: embeddings vector = [0.2, 0.1, 0.4, 0.5, 0.3]
* **Pneumonia**: embeddings vector = [0.4, 0.5, 0.3, 0.2, 0.1]
* **Sepsis**: embeddings vector = [0.5, 0.3, 0.2, 0.1, 0.4]
* **Respiratory Failure**: embeddings vector = [0.3, 0.2, 0.1, 0.5, 0.4]

**Contexte RAG formaté pour LLM**

{
  "entities": [
    {"id": "Fatigue", "label": "Symptom"},
    {"id": "Headache", "label": "Symptom"},
    {"id": "Fever", "label": "Symptom"},
    {"id": "Cough", "label": "Symptom"},
    {"id": "Viral Infection", "label": "Cause"},
    {"id": "Bacterial Infection", "label": "Cause"},
    {"id": "Allergic Reaction", "label": "Cause"},
    {"id": "Medical History", "label": "Diagnosis"},
    {"id": "Physical Examination", "label": "Diagnosis"},
    {"id": "Lab Tests", "label": "Diagnosis"},
    {"id": "Medication", "label": "Treatment"},
    {"id": "Rest and Hydration", "label": "Treatment"},
    {"id": "Antibiotics", "label": "Treatment"},
    {"id": "Pneumonia", "label": "Complication"},
    {"id": "Sepsis", "label": "Complication"},
    {"id": "Respiratory Failure", "label": "Complication"}
  ],
  "relations": [
    {"id": "Fatigue-Viral Infection", "label": "has cause"},
    {"id": "Headache-Bacterial Infection", "label": "has cause"},
    {"id": "Fever-Allergic Reaction", "label": "has cause"},
    {"id": "Cough-Pneumonia", "label": "has complication"},
    {"id": "Viral Infection-Medical History", "label": "is diagnosed by"},
    {"id": "Bacterial Infection-Physical Examination", "label": "is diagnosed by"},
    {"id": "Allergic Reaction-Lab Tests", "label": "is diagnosed by"},
    {"id": "Medical History-Medication", "label": "is treated by"},
    {"id": "Physical Examination-Rest and Hydration", "label": "is treated by"},
    {"id": "Lab Tests-Antibiotics", "label": "is treated by"}
  ]
}

This package of knowledge contains a structured fiche technique that synthesizes the information into a readable format, and a set of embeddings for the key concepts. The context RAG is formatted for LLM and includes entities, relations, and labels that describe the relationships between the concepts.