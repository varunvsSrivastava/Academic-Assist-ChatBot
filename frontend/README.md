This is the React frontend for the Academic Assistant.

- Start the backend API with `python backend/run.py` from the project root.
- The frontend points to `http://127.0.0.1:8001` by default.
- Set `REACT_APP_API_BASE_URL` if your backend is not running on the same origin.
- From `frontend/`, run `npm install` then `npm start` to launch the React dev server.

The app provides a styled chatbox, PDF upload panel, and dashboard that shows average metrics by calling the backend endpoints.
