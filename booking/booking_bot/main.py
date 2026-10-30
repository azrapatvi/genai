from agent import agent

while True:
    config1={'configurable':{'thread_id':'chat1'}}
    user_input=input('YOU: ')
    

    if user_input.lower().strip()=='exit':
        break

    response=agent.invoke({'messages':user_input},config=config1)

    print("BOT: ",response['messages'][-1].content)

