from flask import Flask, render_template, request, jsonify
import openai
import markdown

app = Flask(__name__)

# Tu clave de API de OpenAI
OPENAI_API_KEY = 'sk-sZcEzjtfKF_4wRR3LXfSxHU1I3wgaapNXfaqL7XtN6T3BlbkFJoRHRt7XPCM41Bo3eaRl3C3fAhcqnpE0k9afStWAaAA'
openai.api_key = OPENAI_API_KEY

# ID del asistente de OpenAI
assistant_id = "asst_yzVfJkTZFFTH3yFUyAMfr80r"

def create_thread(ass_id, user_input):
    """Crea un hilo de conversación y envía el mensaje del usuario"""
    thread = openai.beta.threads.create()
    my_thread_id = thread.id

    openai.beta.threads.messages.create(
        thread_id=my_thread_id,
        role="user",
        content=user_input
    )

    run = openai.beta.threads.runs.create(
        thread_id=my_thread_id,
        assistant_id=ass_id,
    )

    return run.id, my_thread_id

def check_status(run_id, thread_id):
    """Verifica el estado del hilo"""
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

@app.route('/')
def index():
    """Renderiza la interfaz HTML"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Maneja la comunicación entre el usuario y el chatbot"""
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400

    my_run_id, my_thread_id = create_thread(assistant_id, user_input)

    status = check_status(my_run_id, my_thread_id)
    while status != "completed":
        status = check_status(my_run_id, my_thread_id)

    response = openai.beta.threads.messages.list(thread_id=my_thread_id)

    if response.data:
        for message in response.data:
            if message.role == "assistant":
                assistant_reply = markdown.markdown(message.content[0].text.value)  # Convierte Markdown a HTML
                return jsonify({'response': assistant_reply})
    else:
        return jsonify({'error': 'No response received from the assistant'}), 500

if __name__ == '__main__':
    app.run(debug=True)