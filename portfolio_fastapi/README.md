# Data Science Portfolio with FastAPI

A modern, dynamic portfolio website built with FastAPI that showcases data science and optimization skills. The website includes interactive features such as a chatbot, time series forecasting, and a retrieval-augmented generation (RAG) system.

## Features

- **Modern Web Interface**: Clean, responsive design built with HTML5, CSS3, and JavaScript
- **Interactive Chatbot**: Powered by OpenAI's GPT-3.5-turbo model
- **Time Series Forecasting**: LSTM-based forecasting model for time series data
- **RAG System**: Document-based question answering system using FAISS and sentence transformers
- **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation

## Project Structure

```
portfolio_fastapi/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Project dependencies
├── .env                # Environment variables
├── models/             # ML model implementations
│   ├── chatbot.py      # Chatbot model
│   └── forecasting.py  # Time series forecasting model
├── utils/              # Utility functions
│   └── rag.py         # RAG system implementation
├── templates/          # Jinja2 HTML templates
├── static/            # Static files (CSS, JS, images)
└── documents/         # Documents for RAG system
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd portfolio_fastapi
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key and other configuration

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the application:
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs

## API Endpoints

- `GET /`: Home page
- `GET /about`: About page
- `GET /projects`: Projects page
- `GET /skills`: Skills page
- `GET /contact`: Contact page
- `POST /api/chat`: Chatbot endpoint
- `POST /api/forecast`: Time series forecasting endpoint
- `POST /api/rag`: RAG system endpoint

## Customization

1. **Content**: Edit the HTML templates in the `templates/` directory
2. **Styling**: Modify CSS files in the `static/css/` directory
3. **Functionality**: Update JavaScript files in the `static/js/` directory
4. **ML Models**: Adjust model parameters in the respective model files

## Dependencies

- FastAPI==0.109.2
- uvicorn==0.27.1
- jinja2==3.1.3
- python-multipart==0.0.9
- python-dotenv==1.0.1
- langchain==0.1.5
- langchain-community==0.0.16
- langchain-core==0.1.17
- sentence-transformers==2.5.1
- faiss-cpu==1.7.4
- torch==2.2.0
- pandas==2.2.0
- numpy==1.26.3
- scikit-learn==1.4.0
- plotly==5.18.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- Hugging Face for the sentence transformers
- FastAPI team for the excellent web framework 