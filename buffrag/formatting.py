# File: formatting.py
from IPython.display import display, HTML
import ipywidgets as widgets
from IPython.core.display import Javascript

def pretty_print_analysis(title, content):
    wrapped_content = textwrap.fill(content, width=80)
    formatted_content = f"""
    <div style="
        width: 100%;
        max-width: 800px;
        margin: 10px auto;
        background-color: #F9F9FF;
        border-left: 6px solid #3A4C8C;
        color: #212529;
        font-family: Arial, sans-serif;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border-radius: 5px;
    ">
        <h3 style="
            color: #3A4C8C;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.5em;
            font-family: inherit;
        ">{title}</h3>
        <pre style="
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #2D3748;
            color: #E2E8F0;
            border: 1px solid #4A5568;
            border-radius: 4px;
            padding: 15px;
            font-size: 0.9em;
            line-height: 1.6;
            font-family: inherit;
            width: 100%;
            box-sizing: border-box;
        ">{wrapped_content}</pre>
    </div>
    """
    display(HTML(formatted_content))


def create_dynamic_input_box(rag_chain, search_results_store):
    # Updated CSS for styling
    style = """
    <style>
    body, input, button, div, pre {
        font-family: Arial, sans-serif;
    }
    .separation-line {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, rgba(52, 152, 219, 0), rgba(52, 152, 219, 0.75), rgba(52, 152, 219, 0));
        margin: 30px 0;
    }
    .widget-text input[type="text"] {
        border-radius: 8px;
        padding: 12px 15px;
        border: 2px solid #3498db;
        transition: all 0.3s ease;
        font-size: 16px;
        width: 100%;
        max-width: 600px;
        line-height: 1.5;
    }
    .widget-text input[type="text"]:focus {
        outline: none;
        box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
    }
    .widget-button button {
        border-radius: 8px;
        transition: all 0.3s ease;
        font-size: 14px;
        padding: 8px 15px;
        margin: 10px 5px 0;
    }
    #analyzing {
        font-size: 16px;
        font-weight: bold;
        color: #3498db;
        margin-top: 15px;
    }
    #result {
        font-size: 16px;
        color: #2ecc71;
        margin-top: 10px;
        white-space: pre-wrap;
    }
    .input-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }
    .button-container {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .show-results-button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 15px;
        font-size: 14px;
        transition: background-color 0.3s;
    }
    .show-results-button:hover {
        background-color: #2980b9;
    }
    .google-results-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        display: none;
    }
    .google-results-box pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: inherit;
        font-size: 14px;
    }
    </style>
    """
    
    # JavaScript remains the same
    js = """
    <script>
    var dotInterval;
    function animateDots() {
        var dots = 0;
        clearInterval(dotInterval);
        dotInterval = setInterval(function() {
            var analyzing = document.getElementById('analyzing');
            if (analyzing) {
                dots = (dots + 1) % 4;
                analyzing.textContent = "Analyzing" + ".".repeat(dots);
            } else {
                clearInterval(dotInterval);
            }
        }, 500);
    }
    
    function stopAnimateDots() {
        clearInterval(dotInterval);
        var analyzing = document.getElementById('analyzing');
        if (analyzing) {
            analyzing.textContent = "Analysis complete!";
        }
    }
    
    function toggleGoogleResults() {
        var resultsBox = document.getElementById('google-results-box');
        if (resultsBox.style.display === 'none' || resultsBox.style.display === '') {
            resultsBox.style.display = 'block';
        } else {
            resultsBox.style.display = 'none';
        }
    }
    </script>
    """
    
    # Display CSS and JavaScript
    display(HTML(style + js))
    
    # Display separation line
    display(HTML('<hr class="separation-line">'))
    
    # Rest of the function remains the same
    text_input = widgets.Text(
        placeholder="Enter your question here...",
        description="Question:",
        layout=widgets.Layout(width='100%', max_width='600px')
    )
    
    submit_button = widgets.Button(
        description='Submit',
        button_style='primary',
        layout=widgets.Layout(width='100px')
    )
    
    clear_button = widgets.Button(
        description='Clear',
        button_style='warning',
        layout=widgets.Layout(width='100px')
    )
    
    output = widgets.Output()
    
    display(HTML('<div class="input-container">'))
    display(text_input)
    display(HTML('<div class="button-container">'))
    display(widgets.HBox([submit_button, clear_button]))
    display(HTML('</div>'))
    display(output)
    display(HTML('</div>'))
    
    def on_submit_click(b):
        question = text_input.value
        if question:
            with output:
                output.clear_output()
                display(HTML('<div id="analyzing">Analyzing</div>'))
                display(Javascript('animateDots();'))
                
                result, search_results = run_analysis(rag_chain, question, search_results_store)
                
                display(Javascript('stopAnimateDots();'))
                
                output.clear_output()
                pretty_print_analysis("Warren Buffett's Analysis:", result)
                
                display(HTML('<button onclick="toggleGoogleResults()" class="show-results-button">Show Google Results</button>'))
                
                google_results_html = f"""
                <div id="google-results-box" class="google-results-box">
                    <h4>Google Search Results:</h4>
                    <p><strong>Search Query:</strong> {search_results.get("search_query", "N/A")}</p>
                    <h5>Relevant News Snippets:</h5>
                    <pre>{search_results.get("relevant_news", "No relevant news found.")}</pre>
                </div>
                """
                display(HTML(google_results_html))

    def on_clear_click(b):
        with output:
            output.clear_output()
        text_input.value = ""

    submit_button.on_click(on_submit_click)
    clear_button.on_click(on_clear_click)
    
    return text_input, submit_button, clear_button, output
    
def display_search_results(search_results):
    if search_results:
        html_content = f"""
        <div style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
            <h4 style="color: #333;">Search Information:</h4>
            <p><strong>Search Query:</strong> {search_results.get("search_query", "N/A")}</p>
            <h5 style="color: #333;">Relevant News Snippets:</h5>
            <pre style="white-space: pre-wrap; word-wrap: break-word;">{search_results.get("relevant_news", "No relevant news found.")}</pre>
        </div>
        """
        display(HTML(html_content))
    else:
        print("No search results available for this query.")
    # ... (implementation)

def display_vector_store_info(client, collection_name="test"):
    points_count, sources = query_vector_store(client, collection_name)
    
    html_content = f"""
    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 10px; font-family: Arial, sans-serif;">
        <h3 style="color: #333;">Vector Store Information</h3>
        <p><strong>Total Documents:</strong> {points_count}</p>
        <h4 style="color: #333;">Data Sources:</h4>
        <ul>
    """
    
    for source, count in sources.items():
        html_content += f"<li><strong>{source}:</strong> {count} document(s)</li>"
    
    html_content += """
        </ul>
    </div>
    """
    
    display(HTML(html_content))