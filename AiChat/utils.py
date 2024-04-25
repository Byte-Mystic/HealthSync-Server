from dotenv import load_dotenv

# import google.generativeai as palm

load_dotenv()
# palm.configure(api_key="AIzaSyDyyBhtKdy5Zys8RjN5cs--wF6RRvxqvoA")


def chat_with_me(question: str) -> str | None:
    return "Answer"
    # response = palm.chat(messages=[question])
    # return response.last
