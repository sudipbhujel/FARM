# FARM stack

## Technology Stacks

- Fast API
- React JS
- Monngo DB

## Getting started

1. Create python virtualenv
   ```bash
   python3 -m vevn
   ```
2. Install requirements

   ```bash
   pip install -r requirements.txt
   ```

3. Make `.env` file inside `/backend` folder
   ```
   touch .env
   ```
4. Update .env file with following environment variables

   ```
   MONGOURI=mongodb://localhost:27017/test
   ```

5. To run fast API server, change directory to `/backend` and paste this command `uvicorn app.main:app --reload `
   ```
   uvicorn app.main:app --reload
   ```
