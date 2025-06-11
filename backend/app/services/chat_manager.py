from app.services.embedding_manager import query_vectorstore
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# I think we need a prompt or something
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
so yeah you're like an AI bot and someone's gonna ask a question from this doc... 
just answer based on that, don't make stuff up okay?

CONTEXT START:
{context}

QUESTION:
{question}

REPLY BELOW:
"""
)

# Main function for this thing
def talk_to_doc(user_q, k=3):
    # get top k chunks - I hope this works
    contextList = query_vectorstore(user_q, top_k=k)
    
    full_context = ""
    for c in contextList:
        full_context += c + "\n\n"

    # plug into the prompt thing
    ready_prompt = prompt_template.format(
        context=full_context,
        question=user_q
    )

    # this is the model, keep it chill (temp=0)
    model = ChatOpenAI(temperature=0)

    # generate the thing
    result = model.invoke(ready_prompt)

    return result.content
