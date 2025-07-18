from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

llm = OpenAI(temperature=0.6)


def generate_prompt_template():
    prompt_template_name = PromptTemplate(input_variables=['cuisine'],
               template="I want to open a restaurant for {cuisine} food. suggest a fency name for this. only one name please"
              )
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="restaurant_name")


    prompt_template_items = PromptTemplate(input_variables=['restaurant_name'],
                template="suggest some food menu items for {restaurant_name}. and return it as comma seperated list."
                )
    food_items_chain = LLMChain(llm=llm, prompt=prompt_template_items, output_key="menu_items")

    return name_chain, food_items_chain

def generate_restaurent_name_name_items(cuisine):

    name_chain, food_items_chain = generate_prompt_template()

    chains = SequentialChain(
            chains=[name_chain, food_items_chain],
            input_variables=['cuisine'],
            output_variables=['restaurant_name', 'menu_items']
        )

    return chains({'cuisine': "Arabic"})
