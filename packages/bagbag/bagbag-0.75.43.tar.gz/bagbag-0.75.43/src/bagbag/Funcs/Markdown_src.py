import markdown2
import markdownify

#print("load " + __file__.split('/')[-1])

def Markdown2Html(text:str) -> str:
    extras = [
        'tables', 
        'toc', 
        'fenced-code-blocks', 
        'footnotes', 
        'task_list',
        'break-on-newline',
        'cuddled-lists',
        'strike',
        'target-blank-links'
    ]
    return markdown2.markdown(text, extras=extras)

def Html2Markdown(html:str) -> str:
    return markdownify.markdownify(html)