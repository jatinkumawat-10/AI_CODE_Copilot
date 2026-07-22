from app.services.review_service import review_code

code = """
def add(a,b):
    return a+b
"""

review = review_code(
    code=code,
    language="python"
)

print(review)