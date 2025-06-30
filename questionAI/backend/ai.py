import os
import google.generativeai as genai
from PIL import Image
# High-level model for content generation
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
generation_model = genai.GenerativeModel("gemini-1.5-flash-latest")


def describe_image(image_path):
    imagemodel = genai.GenerativeModel("gemini-1.5-flash-latest")
    with Image.open(image_path) as img:
        response = imagemodel.generate_content(["Describe this image briefly for software context:", img])
    return response.text.strip()

def classify_question_category(question_text: str) -> str:
    cat_prompt = (
        f"I'm building a software architecture question tracking tool. "
        f"Given the question: '{question_text}', suggest the most relevant category "
        f"from this list: [architecture, performance, security, integration, maintainability, testing, devops]. "
        f"Respond only with the category name."
    )
    return generation_model.generate_content(cat_prompt).text.strip()

def classify_question_priority(question_text: str) -> str:
    pri_prompt = (
        f"I'm building a software architecture question tracking tool. "
        f"Given the question: '{question_text}', suggest the most relevant priority "
        f"from this list: [Low, Medium, High]. "
        f"Respond only with the category name."
        f"Most of your questions are usually high priority, so be careful with your answer."
        f"Given that everything is important you should consider that the question being low or medium or high priority should be based on the question itself. try to come up with a system for yourself where you rank a question priority in a scale of 1 to 10 and if it is a 1 through 4 its low priority, from 5 through 7 is medium priority and 8 to 10 is the high priority."
        f"High priority questions are usually the ones that are blocking the team or that are related to a decision that needs to be made soon."
        f"Low priority questions are usually the ones that are not blocking the team or that are related to a decision that can be made later."
        f"Medium priority questions are usually the ones that are not blocking the team but that are related to a decision that needs to be made soon."
        f"Respond only with the priority name."
    )
    return generation_model.generate_content(pri_prompt).text.strip()

def generate_question_suggestions(n=3) -> list[str]:
    prompt = f"Suggest {n} insightful software architecture design questions a team might ask during planning or development."
    response = generation_model.generate_content(prompt)
    suggestions = [line.strip("- ").strip() for line in response.text.strip().split("\n") if line.strip()]
    return suggestions[:n]

def classify_taxonomy(question_text: str) -> str:
    prompt = f"""
You are an expert in software architecture. Given the question below, tag it with 1 to 3 relevant **taxonomy tags** from this list or other terms you find more relevant, this list is just a suggestion:
["Architectural Style", "Quality Attribute", "Design Decision", "Communication", "Process", "Deployment", "Trade-off", "Tools", "Patterns", "Team", "Requirements", "Stakeholders"]
Also remember that you can tag it with 1, 2 or 3 tags, but not more than that. And if you think it doesnt need any more than 1 tag just put one tag. dont need to force it to be 3.
Respond strictly in the format:
Taxonomy: <comma-separated list of tags>

Question:
\"\"\"{question_text}\"\"\"
"""
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    content = response.text.strip()

    for line in content.splitlines():
        if line.lower().startswith("taxonomy:"):
            tags = line.split(":", 1)[1].strip()
            return tags
    return ""

def classify_question_meta(question_text: str) -> tuple[str, str, str]:
    prompt = f"""
You are an expert in software architecture.

Given the question below:
\"\"\"{question_text}\"\"\"

1. Suggest the most relevant **category** from this list:  
[architecture, performance, security, integration, maintainability, testing, devops].  
Respond only with the category name and with a upper first letter.

2. Suggest the most relevant **priority** from this list:  
[Low, Medium, High].  
Use this scale:  
- 1–4 → Low  
- 5–7 → Medium  
- 8–10 → High  
High = blocking/urgent.  
Low = non-blocking/postpone.  
Medium = important but not blocking.  
Respond only with the priority name, no numbers nor special characters.

3. Tag the question with 1 to 3 relevant **taxonomy tags** from this list or others you find more fitting:  
["Architectural Style", "Quality Attribute", "Design Decision", "Communication", "Process", "Deployment", "Trade-off", "Tools", "Patterns", "Team", "Requirements", "Stakeholders"]  
Respond strictly in the format:  
Taxonomy: <comma-separated list of tags>
---
Now, classify:
"""
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt).text.strip()

    # Fallback logic for formats with or without labels
    lines = [line.strip() for line in response.splitlines() if line.strip()]

    # Try labeled format
    category = priority = taxonomy = None
    for line in lines:
        if line.lower().startswith("category:"):
            category = line.split(":", 1)[1].strip()
        elif line.lower().startswith("priority:"):
            priority = line.split(":", 1)[1].strip()
        elif line.lower().startswith("taxonomy:"):
            taxonomy = line.split(":", 1)[1].strip()

    # If not labeled, fallback to positional assumption
    if not category and len(lines) >= 1:
        category = lines[0]
    if not priority and len(lines) >= 2:
        priority = lines[1]
    if not taxonomy:
        for line in lines:
            if "taxonomy:" in line.lower():
                taxonomy = line.split(":", 1)[1].strip()

    if not all([category, priority, taxonomy]):
        raise ValueError("Failed to extract all classification fields from Gemini response:\n" + response)

    return category, priority, taxonomy




# def generate_ai_response(user_message, initial_question, discussion_history):

#     conversation_context = initial_question + "\n"
#     for entry in discussion_history:
#         conversation_context += f"{entry['source']} says: {entry['message']}\n"
#     conversation_context += f"You say: {user_message}\n"


#     ai_response = (
#         f"You are an AI assistant helping with a software architecture question tracking tool. "
#         f"The following is a question that has been raised in the tool: '{conversation_context}'. "
#         f"Consider the context of the question carefully, along with its implications for software architecture. "
#         f"Please provide a detailed and relevant response to the question. "
#         f"Ensure your response is clear, actionable, and directly addresses the core concern. "
#         f"If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. "
#         f"Your response should help the user better understand the issue and guide them towards a more informed decision. "
#         f"Respond with a message that fits naturally into the ongoing discussion."
#         f"Respond only with the message and be brief and concise dont add any extra information or context."
#     )

#     return generation_model.generate_content(ai_response).text.strip()

def generate_ai_response(message, question_context, discussion_history, user_role):
    role_map = {
        "product_owner": generate_ai_response_po,
        "developer": generate_ai_response_dev,
        "architect": generate_ai_response_qo,
        "decision_maker": generate_ai_response_dm,
    }

    responder = role_map.get(user_role, generate_ai_response_default)
    return responder(message, question_context, discussion_history)


def generate_ai_response_po(message, question_context, discussion_history):
    prompt = f"""
Act as an helpful assistant who has the knowledge of a Product Owner. Focus on business value, stakeholder alignment, and requirements clarity. 
Respond with a message that fits naturally into the ongoing discussion and try to act like a normal person acting as a product owner in a company. 
Ensure your response is clear, actionable, and directly addresses the core concern.
Respond only with the message and be brief and concise dont add any extra unnecessary information or context.
If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. 


Question: {question_context}
Discussion:
{format_discussion(discussion_history)}

User says: {message}

Respond as a PO:
"""
    return call_gemini(prompt)


def generate_ai_response_dev(message, question_context, discussion_history):
    prompt = f"""
Act as an helpful assistant who has the knowledge of a Developer. Focus on implementation details, trade-offs, and feasibility.
Respond with a message that fits naturally into the ongoing discussion and try to act like a normal person acting as a developer in a company, however still behave professionally. 
Ensure your response is clear, actionable, and directly addresses the core concern.
Respond only with the message and be brief and concise dont add any extra unnecessary information or context.
If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. 

Question: {question_context}
Discussion:
{format_discussion(discussion_history)}

User says: {message}

Respond as a Developer:
"""
    return call_gemini(prompt)


def generate_ai_response_qo(message, question_context, discussion_history):
    prompt = f"""
Act as an helpful assistant who has the knowledge of a Software Architect and you act as a Questions Owner assistant. A questions owner Formulates the question and introduces it into the workflow, discussing it with other members to ensure it is clearly defined while also managing the question backlog and archival process. 
Focus on architectural quality attributes, trade-offs, and long-term implications.
Respond with a message that fits naturally into the ongoing discussion and try to act like a normal person acting as a questions owner in a company. 
Ensure your response is clear, actionable, and directly addresses the core concern.
Respond only with the message and be brief and concise dont add any extra unnecessary information or context.
If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. 

Question: {question_context}
Discussion:
{format_discussion(discussion_history)}

User says: {message}

Respond as an Architect:
"""
    return call_gemini(prompt)


def generate_ai_response_dm(message, question_context, discussion_history):
    prompt = f"""
Act as an helpful assistant who has the knowledge of a Decision Maker. Focus on strategic direction, risk, and prioritization. A decision maker evaluates all parameters and determines whether the question is resolved, deferred, or answered through assumptions so you need to have good feedback that can impact the end decision.
Respond with a message that fits naturally into the ongoing discussion and try to act like a normal person acting as a decision maker in a company. 
Ensure your response is clear, actionable, and directly addresses the core concern.
Respond only with the message and be brief and concise dont add any extra unnecessary information or context.
If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. 

Question: {question_context}
Discussion:
{format_discussion(discussion_history)}

User says: {message}

Respond as a Decision Maker:
"""
    return call_gemini(prompt)


def generate_ai_response_default(message, question_context, discussion_history):
    prompt = f"""
You are a helpful assistant. Provide general guidance.
Ensure your response is clear, actionable, and directly addresses the core concern.
Respond only with the message and be brief and concise dont add any extra unnecessary information or context.
If necessary, provide any trade-offs, benefits, or potential challenges related to the question at hand. 

Question: {question_context}
Discussion:
{format_discussion(discussion_history)}

User says: {message}

Response:
"""
    return call_gemini(prompt)


def format_discussion(discussion_history):
    if not discussion_history:
        return "No prior discussion."
    return "\n".join(f"{msg['source']}: {msg['message']}" for msg in discussion_history)


def call_gemini(prompt):
    response = generation_model.generate_content(prompt)
    return response.text.strip()