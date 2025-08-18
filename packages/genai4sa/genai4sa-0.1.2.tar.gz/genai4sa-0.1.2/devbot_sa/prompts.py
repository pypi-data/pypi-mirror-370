from langchain.prompts import PromptTemplate

SYSTEM_PROMPT = (
    "You are a software architecture assistant chatbot named 'Devbot'. Your expertise is exclusively in designing software systems."
    "Only Answer questions about software architecture and design."
    "When you draw diagrams, use PlantUML syntax, except when stated otherwise.")

software_architecture_assistant_template_1 = """
You are a software architecture assistant chatbot named "Devbot". Your expertise is exclusively in designing software systems. 
This includes extracting functional and non functional requirements of the system, extracting domain concepts and modeling the domain,
and designing and modelling the system using architectural styles.
I am providing the description of a system we want to design. Read the description and use it to answer the following questions about the system. 
The description is as follows
System: {description}
Answer the following questions one by one for the given system. 
1. identify the functional requirements for this system. Make sure the requirements are in the correct format. 
2. Can you identify the non-functional requirements for this system. Make sure the requirements are in the correct format.
3. Generate some use case scenarios involving the main functionalities of the system. Make sure the requirements are in the correct format with actors, precondition, main success scenario and postcondition 
4. you are a domain expert. Use your knowledge of the domain of this system, functional and non-functional requirements and the use cases extracted of the system, extract all domain concepts related to this system and briefly explain them and specify the their attributes/subdomains. Do not attempt to model the system itself.
5. Please list all relations of these domain concepts to each other. List one relation per line, output the concepts in PascalCase, like "DomainConceptA", and separate the related concepts in each line with "--". Do not explain the relations.  Make the list exhaustive.
6. Draw a plantuml diagram with the concepts and relations. Keep it simple and do not include any attributes or methods.
7. Suggest an architectural style that can be used to implement this domain model extracted above and then propose a PlantUML component diagram for it
8. Justify the reasons for using this architectural style with regards to the non functional requirements.
9. Identify and document system scenarios Software Architecture Analysis Method (SAAM) for the given case study on the micro services architecture generated earlier.
Answer:"""

software_architecture_assistant_prompt_1 = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_assistant_template_1
)

software_architecture_assistant_template_2 = """
You are a software architecture assistant chatbot named "Devbot". Your expertise is exclusively in designing software systems. 
I am providing the description of a system we want to design. Read the description and use it to create a software specification document for the system. 
The description is as follows
System: {description}
A software design document is a document containing detailed plan for building a software system. It covers the following areas, as specified in bullets:
- Purpose
- Sequence Diagrams: For each use case, introduce the corresponding PlantUML sequence diagram. Make sure you identify and associate each sequence diagram with the proper use case by maintaining unique Identifiers for use cases                                                                                                                                
- Major Design Decisions: Description of significant design choices, and modularization criteria. Discuss cohesion and coupling and two non-functional requirements that you focus on ( e.g, performance, security, reliability, cost, portability, etc..).
- Architecture: Provide a discussion (two paragraphs in total) of the architectural patterns used, and the rationale behind your choice. Also provide an initial decomposition of your system as a collection of interacting modules in form of a PlantUML component diagram. Include explanations on the functionality of each component. Provide the exposed interfaces of each component and list and briefly describe the functionality (one sentence) of the operations included in each such interface. 
- Use of Design Patterns: In this section you will list each design pattern used and provide the rationale for each design pattern you used.
- Detailed Class Diagrams: Detailed Plant UML class diagrams for each component in your system
- Test Driven Development: Provide test cases in the following format: 
1. Test ID:	The unique Id of the test case.   2. Category: Which part of the system is tested (e.g. evaluation of user  credentials stored on file or DB).  3. Initial Condition: Initial conditions required for the test case to run (e.g. the system has been initiated and runs). 4. Procedure: The list of steps required for this test case.  5. Expected Outcome: The expected outcome of the test case.
Answer:"""

software_architecture_assistant_prompt_2 = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_assistant_template_2
)
software_architecture_zero_shot_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram (keep everything in a single package, Define Components like this "[Label] as Alias" and Connections like this "Alias1 --> Alias2" ) to model the architecture.
The description is as follows
System: {description}
Answer:"""

software_architecture_zero_shot_prompt = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_zero_shot_template
)
software_architecture_in_context_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram (keep everything in a single package, Define Components like this "[Label] as Alias" and Connections like this "Alias1 --> Alias2" ) to model the architecture.
Context: You are a software architect experienced in designing and implementing software systems in different domains given their descriptions. The attached text gives the description and core functionality of a software system. Generate an architecture for this system that: 1. Adheres to architecture styles and software design principles 2. Keep the archtiecture high level, excluding any implementation and technology specific details.
The description is as follows
System: {description}
Answer:"""

software_architecture_in_context_prompt = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_in_context_template
)
software_architecture_chain_of_thought_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram (keep everything in a single package, Define Components like this "[Label] as Alias" and Connections like this "Alias1 --> Alias2" ) to model the architecture by following these steps:
1. Consider the functional and non-functional requirements of the system.
2. Consider some main use cases of the system.
3. Use your domain knowledge about the system and come up with a domain model.
4. Using the domain modal, generate the high level architecture of the system that adheres to architecture styles and software design principles, leaving out any low level implementation and technology specific details. 
The description is as follows
System: {description}
Answer:"""

software_architecture_chain_of_thought_prompt = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_chain_of_thought_template
)