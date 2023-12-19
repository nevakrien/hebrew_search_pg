from talk import generate_summary
from retriver import get_texts
from ui import run_app

def respond(user_text):
    print('started work')
    texts=get_texts(user_text,1)
    print("texts retrived")
    source_text=texts[0]
    ans=generate_summary(source_text,user_text)
    print("answer generated")
    return ans,source_text

if __name__=="__main__":
    run_app(respond)