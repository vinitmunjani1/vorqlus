# Django AI Role Player Chatbot MVP

A Django web application that provides an interactive chatbot interface with multiple AI roles, user authentication, and conversation history.

## Features

- **User Authentication**: Register, login, and logout functionality
- **AI Role Selection**: Choose from 100+ specialized AI roles
- **Real-time Chat**: Interactive chat interface with AI assistants
- **Conversation History**: All conversations are saved and can be accessed later
- **Modern UI**: Responsive design with Bootstrap 5
- **Context-Aware**: Maintains conversation context for intelligent responses

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup Steps

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** (copy from `.env.example`)
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   TOGETHER_API_KEY=your-together-api-key-here
   TOGETHER_MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct-Turbo
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load AI roles into database**
   The AI roles will be automatically loaded when you first access the dashboard. Alternatively, you can create a management command or load them via Django shell.

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Register a new account or login
   - Start chatting with AI roles!

## Project Structure

```
chatbot_project/
├── manage.py
├── requirements.txt
├── .env.example
├── chatbot_project/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── chatbot_app/
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   ├── services.py        # Business logic
│   ├── forms.py           # Django forms
│   ├── admin.py           # Admin configuration
│   ├── templates/         # HTML templates
│   └── static/            # CSS and JavaScript
└── AI_Role_Player_System_Prompts_Formatted.json
```

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Select AI Role**: Browse available AI roles and select one to chat with
3. **Start Chatting**: Send messages and receive AI responses
4. **View History**: Access your conversation history from the dashboard
5. **Continue Conversations**: Resume previous conversations anytime

## Configuration

### Environment Variables

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Enable/disable debug mode (default: True)
- `TOGETHER_API_KEY`: Your Together AI API key (required)
- `TOGETHER_MODEL_NAME`: Model to use (default: meta-llama/Llama-3.3-70B-Instruct-Turbo)

### Database

The application uses SQLite by default (for MVP). For production, consider using PostgreSQL or MySQL.

## Admin Interface

Access the admin interface at `/admin/` with your superuser credentials to:
- Manage AI roles
- View all conversations
- Manage users
- View messages

## API Endpoints

- `POST /chat/<conversation_id>/send/`: Send a message and get AI response (AJAX)

## Security Notes

- Never commit `.env` file to version control
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use environment variables for sensitive data

## Troubleshooting

### AI roles not loading
- Ensure `AI_Role_Player_System_Prompts_Formatted.json` exists in the project root
- Check file permissions

### API errors
- Verify `TOGETHER_API_KEY` is set correctly in `.env`
- Check your Together AI account and API limits

### Static files not loading
- Run `python manage.py collectstatic` (for production)
- Ensure `STATIC_URL` is configured correctly in settings

## License

This is an MVP project for demonstration purposes.


