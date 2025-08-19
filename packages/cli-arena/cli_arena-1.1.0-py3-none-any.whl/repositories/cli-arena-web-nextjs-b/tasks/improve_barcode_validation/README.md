# CLI Arena Web (Next.js Barcode App)

This project contains a Next.js web app and a PostgreSQL database for barcode management.

## Project Structure
- `src/web/` — Main Next.js web app
- `db/init.sql` — Database schema and seed data
- `Dockerfile` — Build and run the web app
- `docker-compose.yml` — Orchestrates web app and database

---

## Running the Web App (Development, No Database)

```sh
cd src/web
npm install
npm run dev
```
- Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Running Full Stack (Web + Database) with Docker

From the project root:

```sh
docker-compose up --build
```
- Web app: [http://localhost:3000](http://localhost:3000)
- Database: `localhost:5432` (user: `postgres`, password: `postgres`, db: `barcodes`)

---

## File Explanations
- **Dockerfile:** Builds and runs the Next.js app in production mode.
- **docker-compose.yml:** Runs both the web app and a Postgres database, initializing the DB with `db/init.sql`.
- **db/init.sql:** Creates the `barcodes` table and seeds it with a sample row.

---

## Troubleshooting
- If you get dependency errors, run `npm install` in `src/web/`.
- If the app can't connect to the database, check the `DATABASE_URL` in `docker-compose.yml` and your app's config.

---

## More Info
- The main app code is in `src/web/`. See its README for more details on development and deployment.
